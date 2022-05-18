import sys
import operator
import json
import time
import logging
import calendar
from functools import reduce
from datetime import date
from dateutil.relativedelta import relativedelta
from collections import defaultdict
from decimal import Decimal
from copy import deepcopy
from enum import Enum
from bisect import bisect_left, bisect_right
from django.db.models import Q, Prefetch, OuterRef, Subquery
from termcolor import colored, COLORS
from math import floor

from pac.pre_costing.rateware import ltl_rate_shipment_multiple, error_code_lookup
from pac.models import (WeightBreakHeader, ServiceLevel, ServicePoint, BasingPoint)
from pac.rrf.models import (Request, Customer, RequestInformation, RequestProfile, RequestLane,
                            RequestSection, RequestLane, RequestSectionLane,
                            RequestType, RequestSectionLanePricingPoint)
from pac.pre_costing.models import (CurrencyExchange, TerminalCost, BrokerContractCost, Lane,
                                    LaneRoute, DockRoute, TerminalServicePoint, LaneCost, TerminalCostWeightBreakLevel,
                                    LaneCostWeightBreakLevel)

from pac.helpers.functions import update_instance_history_bulk
from pac.helpers.connections import pyodbc_connection


# Required History imports for Bulk Save
from pac.rrf.models import (
    RequestSectionHistory, RequestSectionLaneHistory, RequestSectionLanePricingPointHistory, ProvinceHistory,
    RegionHistory, CountryHistory, TerminalHistory, BasingPointHistory, ServicePointHistory, PostalCodeHistory,
    RequestSectionLanePointTypeHistory)

#import settings for key vault variables
from django.conf import settings

class RequestCalculator:
    # Temporary hardcoded values
    LINE_HAUL_CAPACITY_FACTOR = 0.85
    WEIGHT_BREAK_MAX_UPPER_BOUND_INCREMENT = 500
    SPEED_SHEET_PROFIT_MARGIN_MULTIPLIER = 1.1

    def __init__(self, request_id, pricing_engine_rating_filters):
        logging.info(f'*** Starting Data Load ***')
        logging.info(f'Loading Request ID {request_id}')

        logging.getLogger().setLevel(logging.INFO)

        # Prepare Request Section/Lane/PricingPoint Filter data
        self.rating_filters = pricing_engine_rating_filters
        self.rating_filters_calculate_all = pricing_engine_rating_filters['is_calculate_all']
        rating_filters_request_section_ids = [x['request_section_id']
                                              for x in pricing_engine_rating_filters['request_sections']]
        rating_filters_request_section_lane_ids = [y['request_section_lane_id']
                                                   for x in pricing_engine_rating_filters['request_sections']
                                                   for y in x['request_section_lanes']]
        self.rating_filters_request_lane_wb = {
            y['request_section_lane_id']: [int(t) for t in y['weight_breaks']]
            for x in pricing_engine_rating_filters['request_sections']
            for y in x['request_section_lanes']}
        # self.rating_filters_request_pricing_points_wb = {
        #     z['request_section_lane_pricing_point_id']: [int(t) for t in z['weight_breaks']]
        #     for x in pricing_engine_rating_filters['request_sections']
        #     for y in x['request_section_lanes']
        #     for z in y['request_section_lane_pricing_points']}

        # TODO: Confirm if we need to check active, viewable
        self.request_data = Request.objects \
            .select_related(
                'request_information',
                'request_profile',
                'request_information__customer',
                'request_information__request_type'
            ).get(
                request_id=request_id,
            )
        logging.info('Request Loaded')

        if not self.rating_filters_calculate_all:
            q_filter_request_section_ids = Q(request_section_id__in=rating_filters_request_section_ids)
            q_filter_request_section_lane_ids = Q(request_section_lane_id__in=rating_filters_request_section_lane_ids)
        else:
            q_filter_request_section_ids = Q()
            q_filter_request_section_lane_ids = Q()

        self.section_data = RequestSection.objects.filter(
            request_lane__request_number=self.request_data.request_number,
            weight_break_header__unit__unit_name='LB',
            is_active=True,
            request_lane__is_active=True,
            weight_break_header__is_active=True
        ).filter(
            q_filter_request_section_ids
        ).exclude(
            sub_service_level__service_level__pricing_type='OTHER'
        ).select_related(
            'sub_service_level',
            'sub_service_level__service_level',
            'sub_service_level__service_level__service_offering',
            'override_class',
            'rate_base'
        ).prefetch_related(
            Prefetch(
                'requestsectionlane_set',
                queryset=RequestSectionLane.objects.filter(is_active=True).filter(q_filter_request_section_lane_ids),
                to_attr='requestsectionlane_list'
            )
        )

        # Get and assigns all RequestSectionLanePricingPoint For RequestNumber
        if not self.rating_filters_calculate_all:
            q_filter_pp_request_section_ids = Q(
                request_section_lane__request_section__request_section_id__in=rating_filters_request_section_ids)
        else:
            q_filter_pp_request_section_ids = Q()

        request_section_lane_pricing_points = RequestSectionLanePricingPoint.objects.filter(
            request_section_lane__request_section__request_lane__request_number=self.request_data.request_number
        ).filter(
            q_filter_pp_request_section_ids
        ).select_related(
            'origin_postal_code__service_point',
            'destination_postal_code__service_point'
        ).prefetch_related(
            Prefetch(
                'origin_postal_code__service_point__terminalservicepoint_set',
                queryset=TerminalServicePoint.objects.filter(is_active=True),
                to_attr='origin_terminalservicepoint_list'
            ),
            Prefetch(
                'destination_postal_code__service_point__terminalservicepoint_set',
                queryset=TerminalServicePoint.objects.filter(is_active=True),
                to_attr='destination_terminalservicepoint_list'
            )
        )

        request_section_lane_pricing_point_dict = defaultdict(list)
        for point in request_section_lane_pricing_points:
            request_section_lane_pricing_point_dict[point.request_section_lane_id].append(point)

        for request_section in self.section_data:
            for section_lane in request_section.requestsectionlane_list:
                section_lane.requestsectionlanepricingpoint_list = request_section_lane_pricing_point_dict[
                    section_lane.request_section_lane_id]

        # Calculate WeightBreakUpperBound for weight breaks
        # Last weight break is incremented by self.WEIGHT_BREAK_MAX_UPPER_BOUND_INCREMENT
        for request_section in self.section_data:
            request_Section_weight_breaks = json.loads(request_section.weight_break_details)

            # Temporary Null WB to 0
            for wb in request_Section_weight_breaks:
                if not wb['LevelLowerBound']:
                    wb['LevelLowerBound'] = 0

            request_Section_weight_breaks.sort(key=lambda x: x['LevelLowerBound'], reverse=True)

            for i, weight_break in enumerate(request_Section_weight_breaks):
                if i == 0:
                    level_upper_bound = weight_break['LevelLowerBound'] + self.WEIGHT_BREAK_MAX_UPPER_BOUND_INCREMENT
                weight_break['LevelUpperBound'] = level_upper_bound
                level_upper_bound = weight_break['LevelLowerBound']

            request_Section_weight_breaks.sort(key=lambda x: x['LevelLowerBound'], reverse=False)
            request_section.weight_break_details = json.dumps(request_Section_weight_breaks)

        logging.info(
            f'Loaded {len(self.section_data)} Request Sections with {sum([len(x.requestsectionlane_list) for x in self.section_data])} RequestSectionLanes')

        # #LaneDataForEngine
        self.section_lanes = [section_lane for section in self.section_data
                              for section_lane in section.requestsectionlane_list]

        self.currency_exchange = CurrencyExchange.objects.filter(is_active=True)
        logging.info(f'Loaded {len(self.currency_exchange)} Currency Exchange records')

        self.request_types = RequestType.objects.filter(is_active=True)
        logging.info(f'Loaded {len(self.request_types)} Request Types')

        self.terminal_costs = TerminalCost.objects.filter(is_active=True)
        logging.info(f'Loaded {len(self.terminal_costs)} Terminal Costs')

        self.terminal_cost_weight_break_levels = list(TerminalCostWeightBreakLevel.objects.filter(is_active=True))
        self.terminal_cost_weight_break_levels.sort(key=lambda x: x.weight_break_lower_bound, reverse=False)
        logging.info(f'Loaded {len(self.terminal_cost_weight_break_levels)} Terminal Cost Weight Break Levels')

        # TODO: Do we need this separate?
        self.service_levels = [x.sub_service_level.service_level for x in self.section_data]

        # self.broker_contract_cost = BrokerContractCost.objects.filter(
        #     service_level__in=self.service_levels,
        #     is_active=True)
        # logging.info(f'Loaded {len(self.broker_contract_cost)} Broker Contract Costs')

        # Only query Lanes if Request has lanes
        if self.section_lanes:
            # Get list of Lane origin and destinations for Lanes and Pricing Points
            service_point_origin_destination_map = [(
                y.origin_postal_code.service_point.origin_terminalservicepoint_list[0].terminal_id,
                y.destination_postal_code.service_point.destination_terminalservicepoint_list[0].terminal_id)
                for x in self.section_lanes
                for y in x.requestsectionlanepricingpoint_list
                if x.is_lane_group]
            lane_origin_destination_map = [(lane.origin_terminal_id, lane.destination_terminal_id)
                                           for lane in self.section_lanes
                                           if lane.origin_terminal_id and lane.destination_terminal_id]
            origin_destination_map = lane_origin_destination_map + service_point_origin_destination_map

            # Remove duplicates of O/D -> D/O
            lane_origin_destination_unique = list({tuple(sorted(item)) for item in origin_destination_map})
            # Deplicate to reverse O/D
            lane_origin_destination_unique_flipped = [(item[1], item[0])
                                                      for item in lane_origin_destination_unique]
            # Merge Lists
            lane_origin_destination = lane_origin_destination_unique + lane_origin_destination_unique_flipped

            # Create query for all O+D Pairs
            if not lane_origin_destination:
                self.lanes = []
            else:
                # TODO: May require pagination
                lane_query = reduce(
                    operator.or_,
                    (Q(origin_terminal=lane[0], destination_terminal=lane[1])
                     for lane in lane_origin_destination)
                )

                self.lanes = Lane.objects.filter(
                    sub_service_level__service_level__in=self.service_levels,
                    is_active=True
                ).filter(
                    lane_query
                ).prefetch_related(
                    Prefetch(
                        'laneroute_set',
                        to_attr='laneroute_list'
                    ),
                    Prefetch(
                        'legcost_set',
                        to_attr='legcost_list'
                    ),
                    Prefetch(
                        'dockroute_set',
                        to_attr='dockroute_list'
                    ),
                    Prefetch(
                        'lanecost_set',
                        to_attr='lanecost_list'
                    ),
                    Prefetch(
                        'origin_terminal__brokercontractcost_set',
                        queryset=BrokerContractCost.objects.filter(sub_service_level__service_level__in=self.service_levels, is_active=True),
                        to_attr='brokercontractcost_list'
                    ),
                    Prefetch(
                        'destination_terminal__brokercontractcost_set',
                        queryset=BrokerContractCost.objects.filter(sub_service_level__service_level__in=self.service_levels, is_active=True),
                        to_attr='brokercontractcost_list'
                    )
                )

            # TODO: EK: Add is_active check to Terminal on Dock Cost section

            # Get RouteLegLanes
            lane_route_lane_ids = []
            for lane in self.lanes:
                if lane.laneroute_list:
                    for lane_route in lane.laneroute_list:
                        route_legs = json.loads(lane_route.route_legs)
                        for route_leg in route_legs:
                            lane_route_lane_ids.append(route_leg['LegLaneID'])

            lane_route_lanes = [x for x in self.lanes if x.lane_id in lane_route_lane_ids]
            for lane_route_lane in lane_route_lanes:
                lane_route_lane_ids.remove(lane_route_lane.lane_id)

            # Load remaining Lanes for Routing
            additional_lanes = []
            if lane_route_lane_ids:
                additional_lanes = Lane.objects.filter(
                    sub_service_level__service_level__in=self.service_levels,
                    is_active=True,
                    lane_id__in=lane_route_lane_ids
                ).prefetch_related(
                    # Prefetch(
                    #     'laneroute_set',
                    #     to_attr='laneroute_list'
                    # ),
                    Prefetch(
                        'legcost_set',
                        to_attr='legcost_list'
                    ),
                    Prefetch(
                        'dockroute_set',
                        to_attr='dockroute_list'
                    )
                )

            lanes_dict = {x.lane_id: x for x in self.lanes}
            additional_lanes_dict = {x.lane_id: x for x in additional_lanes}
            lanes_id_dict = {**lanes_dict, **additional_lanes_dict}

            # Initialize Lane Error
            for lane in self.lanes:
                print('Clearing Lane Error State')
                lane.is_error_state = False
                lane.error_messages = []

            # Create LegCosts and DockRoutes from aggregate of lanes in LaneRoute Route Legs
            for lane in self.lanes:
                if not hasattr(lane, 'legcost_route_list'):
                    lane.legcost_route_list = []

                if lane.laneroute_list:
                    for lane_route in lane.laneroute_list:
                        route_legs = json.loads(lane_route.route_legs)
                        for route_leg in route_legs:
                            # lane_route_lane_ids.append(route_leg['LegLaneID'])
                            if not hasattr(lane, 'legcost_route_list'):
                                lane.legcost_route_list = []
                            # if not hasattr(lane, 'dockroute_list'):
                            #     lane.dockroute_list = []

                            if route_leg['LegLaneID'] not in lanes_id_dict:
                                lane.is_error_state = True
                                lane.error_messages.append(
                                    f"RouteLeg Lane from {route_leg['LegOriginTerminalCode']} to {route_leg['LegDestinationTerminalCode']} not found.  Please update in LineHaul Lane Costs")
                                continue

                            lane.legcost_route_list.extend(lanes_id_dict[route_leg['LegLaneID']].legcost_list)
                            # lane.dockroute_list.append(lanes_id_dict[route_leg['LegLaneID']].dockroute_list)

                            # Error handling initialization

            # Assign lanes to Section Lanes or Pricing Points
            for section_lane in self.section_lanes:
                if section_lane.is_lane_group:
                    # Pricing Points
                    for pricing_point in section_lane.requestsectionlanepricingpoint_list:
                        lanes = [x for x in self.lanes if
                                x.origin_terminal_id == pricing_point.origin_postal_code.service_point.origin_terminalservicepoint_list[0].terminal_id  # nopep8
                                and x.destination_terminal_id == pricing_point.destination_postal_code.service_point.destination_terminalservicepoint_list[0].terminal_id  # nopep8
                                and x.sub_service_level.service_level.service_level_id == section_lane.request_section.sub_service_level.service_level_id]  # nopep8
                        lanes_reverse = [
                            x for x in self.lanes
                            if x.destination_terminal_id == pricing_point.origin_postal_code.service_point.origin_terminalservicepoint_list[0].terminal_id  # nopep8
                            and x.origin_terminal_id == pricing_point.destination_postal_code.service_point.destination_terminalservicepoint_list[0].terminal_id  # nopep8
                            and x.sub_service_level.service_level.service_level_id == section_lane.request_section.sub_service_level.service_level_id]  # nopep8

                        # Reverse when Pricing Point Lane IsBetween and Lane not IsHeadHaul
                        for lane in lanes:
                            if section_lane.is_between and not lane.is_headhaul:
                                # Swap
                                lane_temp = next(x for x in lanes_reverse
                                                 if x.origin_terminal_id == lane.destination_terminal_id
                                                 and x.destination_terminal_id == lane.origin_terminal_id)
                                lanes_reverse.remove(lane_temp)
                                lanes_reverse.append(lane)
                                lanes.remove(lane)
                                lanes.append(lane_temp)

                                # Reverse postal codes to match reversed lane
                                pricing_point.set_origin_postal_code_id = pricing_point.destination_postal_code_id
                                pricing_point.set_origin_postal_code_name = pricing_point.destination_postal_code_name
                                pricing_point.set_destination_postal_code_id = pricing_point.origin_postal_code_id
                                pricing_point.set_destination_postal_code_name = pricing_point.origin_postal_code_name

                                # Swap Request Section O/D data
                                section_lane.set_origin_service_point_id = section_lane.destination_service_point_id
                                section_lane.set_destination_service_point_id = section_lane.origin_service_point_id
                                section_lane.set_origin_service_point_name = section_lane.destination_service_point_name
                                section_lane.set_destination_service_point_name = section_lane.origin_service_point_name
                                section_lane.set_origin_basing_point_id = section_lane.destination_basing_point_id
                                section_lane.set_destination_basing_point_id = section_lane.origin_basing_point_id
                                section_lane.set_origin_basing_point_name = section_lane.destination_basing_point_name
                                section_lane.set_destination_basing_point_name = section_lane.origin_basing_point_name
                                section_lane.set_origin_country_id = section_lane.destination_country_id
                                section_lane.set_destination_country_id = section_lane.origin_country_id
                                section_lane.set_origin_country_code = section_lane.destination_country_code
                                section_lane.set_destination_country_code = section_lane.origin_country_code

                                logging.info(
                                    f"Swapping IsBetween Non HeadHaul Pricing Point {section_lane.origin_service_point_name} - {section_lane.destination_service_point_name}")
                            else:
                                # Do not reverse Postal Codes
                                pricing_point.set_origin_postal_code_id = pricing_point.origin_postal_code_id
                                pricing_point.set_origin_postal_code_name = pricing_point.origin_postal_code_name
                                pricing_point.set_destination_postal_code_id = pricing_point.destination_postal_code_id
                                pricing_point.set_destination_postal_code_name = pricing_point.destination_postal_code_name

                                # Do not reverse Request Section O/D data
                                section_lane.set_origin_service_point_id = section_lane.origin_service_point_id
                                section_lane.set_destination_service_point_id = section_lane.destination_service_point_id
                                section_lane.set_origin_service_point_name = section_lane.origin_service_point_name
                                section_lane.set_destination_service_point_name = section_lane.destination_service_point_name
                                section_lane.set_origin_basing_point_id = section_lane.origin_basing_point_id
                                section_lane.set_destination_basing_point_id = section_lane.destination_basing_point_id
                                section_lane.set_origin_basing_point_name = section_lane.origin_basing_point_name
                                section_lane.set_destination_basing_point_name = section_lane.destination_basing_point_name
                                section_lane.set_origin_country_id = section_lane.origin_country_id
                                section_lane.set_destination_country_id = section_lane.destination_country_id
                                section_lane.set_origin_country_code = section_lane.origin_country_code
                                section_lane.set_destination_country_code = section_lane.destination_country_code

                        pricing_point.lanes_list = deepcopy(lanes or [])
                        # pricing_point.lanes_list_reverse = lanes_reverse
                else:
                    # Section Lanes
                    lanes = [x for x in self.lanes if
                             x.origin_terminal_id == section_lane.origin_terminal_id
                             and x.destination_terminal_id == section_lane.destination_terminal_id
                             and x.sub_service_level.service_level.service_level_id == section_lane.request_section.sub_service_level.service_level_id]
                    lanes_reverse = [
                        x for x in self.lanes
                        if x.destination_terminal_id == section_lane.origin_terminal_id
                        and x.origin_terminal_id == section_lane.destination_terminal_id
                        and x.sub_service_level.service_level.service_level_id == section_lane.request_section.sub_service_level.service_level_id]

                    # Reverse when Request Section Lane IsBetween and Lane not IsHeadHaul
                    for lane in lanes:
                        if section_lane.is_between and not lane.is_headhaul:
                            # Swap
                            lane_temp = next(x for x in lanes_reverse
                                             if x.origin_terminal_id == lane.destination_terminal_id
                                             and x.destination_terminal_id == lane.origin_terminal_id)
                            lanes_reverse.remove(lane_temp)
                            lanes_reverse.append(lane)
                            lanes.remove(lane)
                            lanes.append(lane_temp)

                            # Reverse postal codes to match reversed lane
                            section_lane.set_origin_postal_code_id = section_lane.destination_postal_code_id
                            section_lane.set_origin_postal_code_name = section_lane.destination_postal_code_name
                            section_lane.set_destination_postal_code_id = section_lane.origin_postal_code_id
                            section_lane.set_destination_postal_code_name = section_lane.origin_postal_code_name

                            # Swap Request Section O/D data
                            section_lane.set_origin_service_point_id = section_lane.destination_service_point_id
                            section_lane.set_destination_service_point_id = section_lane.origin_service_point_id
                            section_lane.set_origin_service_point_name = section_lane.destination_service_point_name
                            section_lane.set_destination_service_point_name = section_lane.origin_service_point_name
                            section_lane.set_origin_basing_point_id = section_lane.destination_basing_point_id
                            section_lane.set_destination_basing_point_id = section_lane.origin_basing_point_id
                            section_lane.set_origin_basing_point_name = section_lane.destination_basing_point_name
                            section_lane.set_destination_basing_point_name = section_lane.origin_basing_point_name
                            section_lane.set_origin_country_id = section_lane.destination_country_id
                            section_lane.set_destination_country_id = section_lane.origin_country_id
                            section_lane.set_origin_country_code = section_lane.destination_country_code
                            section_lane.set_destination_country_code = section_lane.origin_country_code

                            logging.info(
                                f"Swapping IsBetween Non HeadHaul Lane {section_lane.origin_service_point_name} - {section_lane.destination_service_point_name}")
                        else:
                            # Do not reverse Postal Codes
                            section_lane.set_origin_postal_code_id = section_lane.origin_postal_code_id
                            section_lane.set_origin_postal_code_name = section_lane.origin_postal_code_name
                            section_lane.set_destination_postal_code_id = section_lane.destination_postal_code_id
                            section_lane.set_destination_postal_code_name = section_lane.destination_postal_code_name

                            # Do not reverse Request Section O/D data
                            section_lane.set_origin_service_point_id = section_lane.origin_service_point_id
                            section_lane.set_destination_service_point_id = section_lane.destination_service_point_id
                            section_lane.set_origin_service_point_name = section_lane.origin_service_point_name
                            section_lane.set_destination_service_point_name = section_lane.destination_service_point_name
                            section_lane.set_origin_basing_point_id = section_lane.origin_basing_point_id
                            section_lane.set_destination_basing_point_id = section_lane.destination_basing_point_id
                            section_lane.set_origin_basing_point_name = section_lane.origin_basing_point_name
                            section_lane.set_destination_basing_point_name = section_lane.destination_basing_point_name
                            section_lane.set_origin_country_id = section_lane.origin_country_id
                            section_lane.set_destination_country_id = section_lane.destination_country_id
                            section_lane.set_origin_country_code = section_lane.origin_country_code
                            section_lane.set_destination_country_code = section_lane.destination_country_code

                    section_lane.lanes_list = deepcopy(lanes or [])
                    # section_lane.lanes_list_reverse = lanes_reverse

            # Fix Null Cost Overrides to 0
            for section_lane in self.section_lanes:
                section_lane.cost_override_dock_adjustment_multiplier = section_lane.cost_override_dock_adjustment if section_lane.cost_override_dock_adjustment else 1
                # section_lane.cost_override_pickup_count_multiplier = section_lane.cost_override_pickup_count if section_lane.cost_override_pickup_count else None
                section_lane.cost_override_delivery_count_multiplier = section_lane.cost_override_delivery_count if section_lane.cost_override_delivery_count else 1
                # section_lane.cost_override_margin_multiplier = section_lane.cost_override_margin if section_lane.cost_override_margin else 0

            logging.info(f'Loaded {len(self.lanes)} Origin/Destination Lanes')
        else:
            self.lanes = []
            logging.info(f'No Lanes loaded due to no Section Lanes')

        # self.lane_routes = LaneRoute.objects.filter(lane__in=self.lanes)
        # logging.info(f'Loaded {len(self.lane_routes)} Lane Routes')

        # self.dock_routes = DockRoute.objects.filter(lane__in=self.lanes)
        # logging.info(f'Loaded {len(self.dock_routes)} Dock Routes')

        # self.lane_costs = LaneCost.objects.filter(lane__in=self.lanes)
        # logging.info(f'Loaded {len(self.lane_costs)} Lane Costs')

        # self.terminal_service_points = TerminalServicePoint.objects.filter(is_active=True) \
        #     .select_related('service_point') \
        #     .select_related('service_point__basing_point')
        # logging.info(f'Loaded {len(self.terminal_service_points)} Terminal Service Points')

        self.lane_cost_weight_break_levels = LaneCostWeightBreakLevel.objects.filter(
            is_active=True,
            is_inactive_viewable=True)
        logging.info(f'Loaded {len(self.lane_cost_weight_break_levels)} Lane Cost Weight Break Levels')

        logging.info(f'*** Done Data Load ***')

    def pre_run_clear_data(self, debug_logging=False):
        logging.info(f'*** Starting Clearing Data ***')
        # Clear PricingRates and WorkflowErrors from RequestSectionLanes and RequestSectionPricingPoints being processed
        # TODO: Change to only action on WB, Lanes, etc that we are working on

        # if is_pricing_point:
        #     filter_wb_json = self.rating_filters_request_pricing_points_wb[
        #         lane_parent.request_section_lane_pricing_point_id]
        # else:
        #     filter_wb_json = self.rating_filters_request_lane_wb[lane_parent.request_section_lane_id]

        for request_section in self.section_data:
            for section_lane in request_section.requestsectionlane_list:
                dr_rate = json.loads(section_lane.dr_rate)
                customer_rate = json.loads(section_lane.customer_rate)

                # Clear only WB meant to be priced
                if self.rating_filters_calculate_all:
                    filter_wb_json = dr_rate.keys()
                else:
                    filter_wb_json = self.rating_filters_request_lane_wb[section_lane.request_section_lane_id]

                section_lane.pricing_rates = None
                section_lane.workflow_errors = None
                section_lane.is_error_state = False
                section_lane.dr_rate = json.dumps({x: 0 if x in filter_wb_json
                                                   else dr_rate[x] if x in dr_rate
                                                   else 0
                                                   for x in dr_rate.keys()})
                section_lane.dr_rate_clear = section_lane.dr_rate
                section_lane.customer_rate = json.dumps({x: 0 if x in filter_wb_json
                                                         else customer_rate[x] if x in dr_rate
                                                         else 0
                                                         for x in customer_rate.keys()})
                section_lane.customer_rate_clear = section_lane.customer_rate

                for pricing_point in section_lane.requestsectionlanepricingpoint_list:
                    dr_rate = json.loads(pricing_point.dr_rate)

                    # Clear only WB meant to be priced
                    if self.rating_filters_calculate_all:
                        filter_wb_json = dr_rate.keys()
                    else:
                        filter_wb_json = self.rating_filters_request_lane_wb[section_lane.request_section_lane_id]
                    pricing_point.pricing_rates = None
                    pricing_point.workflow_errors = None
                    pricing_point.is_error_state = False
                    pricing_point.dr_rate = json.dumps({x: 0 if x in filter_wb_json
                                                        else dr_rate[x] if x in dr_rate
                                                        else 0
                                                        for x in dr_rate.keys()})
                    pricing_point.dr_rate_clear = pricing_point.dr_rate

                    # import pdb; pdb.set_trace()

        logging.info(f'*** Done Clearing Data ***')

    def pre_run_validate_data(self, debug_logging=False):
        logging.info(f'*** Starting Data Validation ***')

        for request_section in self.section_data:
            for request_section_lane in request_section.requestsectionlane_list:
                lanes_list_in_section_lane = []

                # Validate if lanes exist
                if request_section_lane.is_lane_group:
                    for pricing_point in request_section_lane.requestsectionlanepricingpoint_list:
                        lanes_list = pricing_point.lanes_list
                        lanes_list_in_section_lane.extend(lanes_list)

                        # Error if Request Pricing Point does not map to a Lane
                        if not lanes_list:
                            lane_return = {
                                "error_state": True,
                                "error_date": str(date.today()),
                                "error_messages": ["Cannot match request to Lane with this Service Level.  Please update in LineHaul Lane Costs"]
                            }
                            pricing_point.workflow_errors = json.dumps(lane_return)
                            pricing_point.is_error_state = True
                else:
                    lanes_list = request_section_lane.lanes_list
                    lanes_list_in_section_lane.extend(lanes_list)

                    # Error if Request Lane does not map to a Lane
                    if not lanes_list:
                        lane_return = {
                            "error_state": True,
                            "error_date": str(date.today()),
                            "error_messages": ["Cannot match request to Lane with this Service Level.  Please update in LineHaul Lane Costs"]
                        }
                        request_section_lane.workflow_errors = json.dumps(lane_return)
                        request_section_lane.is_error_state = True

                # Validate each lane
                if lanes_list_in_section_lane:
                    for lane in lanes_list:
                        if not lane.laneroute_list:
                            lane.is_error_state = True
                            lane.error_messages.append("Lane does not have Lane Routes set up")
                        elif not lane.legcost_route_list:
                            lane.is_error_state = True
                            lane.error_messages.append("Lane Route does not have Leg Costs")
                        if not lane.origin_terminal.brokercontractcost_list:
                            lane.is_error_state = True
                            lane.error_messages.append("Lane does not have Pickup Costs")
                        if not lane.destination_terminal.brokercontractcost_list:
                            lane.is_error_state = True
                            lane.error_messages.append("Lane does not have Delivery Costs")
                        if not lane.dockroute_list:
                            lane.is_error_state = True
                            lane.error_messages.append("Lane does not have Dock Routes")

        logging.info(f'*** Done Data Validation ***')

    def request_setup(self, debug_logging=False):
        logging.info(f'*** Starting Request Setup ***')

        # Set Request Expiry Date if Expiry Date is null
        if not self.request_data.request_information.expiry_date:
            year = date.today().year
            month = date.today().month

            # If SpeedSheet - 6 months Expiry, otherwise 1 year.
            if self.request_data.uni_type == 'SPEEDSHEET':
                year = year + floor((month + 6) / 12)
                month = (month + 6) % 12 or 12
            else:
                year = year + 1

            last_day_of_month = calendar.monthrange(year, month)[1]
            self.request_data.request_information.expiry_date = date(year, month, last_day_of_month)

            if debug_logging:
                logging.info(f'RequestInfo ExpiryDate set to {self.request_data.request_information.expiry_date}')

        logging.info(f'*** Done Request Setup ***')

    def calculate_lane_density(self, debug_logging=False):
        logging.info(f'*** Starting Calculating Lane Density ***')
        for request_section in self.section_data:
            if debug_logging:
                logging.info(
                    f'Processing Request Section {request_section.request_section_id} with {len(request_section.requestsectionlane_list)} Lanes')
            for request_section_lane in request_section.requestsectionlane_list:
                # First calculate the customer density as this applies to all lanes/PP in a section
                customer_density = min(
                    request_section.override_density or self.request_data.request_profile.avg_weight_density or sys.maxsize,
                    self.request_data.request_profile.override_density or self.request_data.request_profile.avg_weight_density or sys.maxsize
                )

                # TODO: 10 is D&R Standard default density - May need to be refactored in the future to pull from a PreCosting table.
                if customer_density == sys.maxsize:
                    customer_density = 10

                # Get all lanes in either a pricing point or request lane
                if request_section_lane.is_lane_group:
                    lanes_list = [(x, y) for x
                                  in request_section_lane.requestsectionlanepricingpoint_list
                                  for y in x.lanes_list]
                    is_pricing_point = True
                else:
                    lanes_list = [(request_section_lane, request_section_lane.lanes_list[0])
                                  ] if request_section_lane.lanes_list else []
                    is_pricing_point = False

                for lane_pair in lanes_list:
                    lane_parent = lane_pair[0]
                    lane = lane_pair[1]

                    weight_break_density = {}
                    weight_break_density_overrides = {}
                    if lane_parent.cost_override_density and lane_parent.cost_override_density != '[]':
                        weight_break_density_overrides_json = json.loads(lane_parent.cost_override_density)
                        weight_break_density_overrides = {
                            int(x): weight_break_density_overrides_json[x] for x in
                            weight_break_density_overrides_json.keys()}
                    if request_section.weight_break_details and request_section.weight_break_details != '[]':
                        for wb_density in json.loads(request_section.weight_break_details):
                            wb = wb_density['LevelLowerBound']
                            if wb in weight_break_density_overrides and weight_break_density_overrides[wb] > 0:
                                weight_break_density[wb] = weight_break_density_overrides[wb]
                            elif (self.request_data.request_profile.linear_length_rule
                                  and self.request_data.request_profile.weight_per_linear_length_rule
                                    and self.request_data.request_profile.linear_length_rule * self.request_data.request_profile.weight_per_linear_length_rule <= wb_density['LevelLowerBound']):
                                weight_break_density[wb] = max(
                                    customer_density,
                                    self.request_data.request_profile.weight_per_linear_length_rule / 64)
                            else:
                                if self.request_data.request_profile.use_actual_weight:
                                    weight_break_density[wb] = customer_density
                                else:
                                    weight_break_density[wb] = max(
                                        customer_density,
                                        self.request_data.request_profile.subject_to_cube or 0)
                    lane.weight_break_density = weight_break_density
                    if debug_logging:
                        if is_pricing_point:
                            logging.info(
                                f'Pricing Point Lane {lane_parent.origin_postal_code_name}-{lane_parent.destination_postal_code_name} - Density {colored(weight_break_density, "magenta")}')
                        else:
                            logging.info(
                                f'Lane {lane_parent.origin_code}-{lane_parent.destination_code} - Density {colored(weight_break_density, "magenta")}')

        logging.info(f'*** Done Calculating Lane Density ***')

    def calculate_line_haul_cost(self, debug_logging=False):
        logging.info(f'*** Starting Calculating Lane Haul Cost ***')
        for request_section in self.section_data:
            unit_factor = float(request_section.unit_factor)

            if request_section.sub_service_level.service_level.service_offering.service_offering_name == "Freight":
                # FreightLinehaulCost
                for request_section_lane in request_section.requestsectionlane_list:
                    if request_section_lane.is_error_state:
                        continue

                    if request_section_lane.is_lane_group:
                        lane_list = [y
                                     for x in request_section_lane.requestsectionlanepricingpoint_list
                                     for y in x.lanes_list
                                     if not x.is_error_state]
                    else:
                        lane_list = request_section_lane.lanes_list

                    for lane in lane_list:
                        if lane.is_error_state:
                            continue

                        lane_routes = lane.laneroute_list
                        leg_costs = lane.legcost_route_list

                        line_haul_cost = {}
                        leg_count = 0

                        if lane_routes:
                            lane_route_legs = json.loads(lane_routes[0].route_legs)
                            leg_count = len(lane_route_legs)
                            if leg_count == 0:
                                lane.is_error_state = True
                                lane.error_messages.append("LaneRoute has 0 LegCounts")
                        else:
                            lane.is_error_state = True
                            lane.error_messages.append("LaneRoute info does not exist")

                        if leg_costs:
                            for leg_cost in leg_costs:
                                leg_cost_by_distance = json.loads(json.loads(leg_cost.cost)[0])[0]

                                trailer_capacity = float(leg_cost_by_distance['TrailerCapacity'].replace(',', ''))

                                if not trailer_capacity:
                                    lane.is_error_state = True
                                    lane.error_messages.append("LegCost Trailer Capacity set to 0")
                                    continue

                                for wb_density in lane.weight_break_density:
                                    cost = (leg_cost_by_distance['FerryCost'] +
                                            (leg_cost_by_distance['RatePerUnitDistance'] *
                                             (leg_cost_by_distance['LegDistance'] +
                                                leg_cost_by_distance['BackHaulDistance'] +
                                                0 +  # @OriginExtraMiles
                                                0  # @DestinationExtraMiles
                                              )
                                             )
                                            ) / (
                                        trailer_capacity *
                                        self.LINE_HAUL_CAPACITY_FACTOR *
                                        min(
                                            float(lane.weight_break_density[wb_density]),
                                            float(trailer_capacity)
                                        )
                                    )

                                    line_haul_cost[wb_density] = line_haul_cost.get(wb_density, 0) + cost
                        else:
                            # import pdb
                            # pdb.set_trace()
                            lane.is_error_state = True
                            lane.error_messages.append("LegCost info does not exist")

                            # import pdb
                            # pdb.set_trace()

                        for wb_density in lane.weight_break_density:
                            line_haul_cost[wb_density] = round(line_haul_cost[wb_density] * unit_factor, 4)

                        lane.line_haul_cost = line_haul_cost
                        if debug_logging:
                            logging.info(
                                f'LaneID {lane.lane_id} between {lane.origin_terminal_id}-{lane.destination_terminal_id} - Freight LineHaul Cost {colored(line_haul_cost,"yellow")}')

            elif request_section.sub_service_level.service_level.service_offering.service_offering_name == "SameDay":
                # SamedayLinehaulCost
                for request_section_lane in request_section.requestsectionlane_list:

                    if request_section_lane.is_lane_group:
                        lane_list = [y
                                     for x in request_section_lane.requestsectionlanepricingpoint_list
                                     for y in x.lanes_list]
                    else:
                        lane_list = request_section_lane.lanes_list

                    for lane in lane_list:
                        if lane.is_error_state:
                            continue

                        lane_routes = lane.laneroute_list
                        leg_costs = lane.legcost_route_list

                        line_haul_cost = {}
                        leg_count = 0

                        if lane_routes:
                            lane_route_legs = json.loads(lane_routes[0].route_legs)
                            leg_count = len(lane_route_legs)
                            if leg_count == 0:
                                lane.is_error_state = True
                                lane.error_messages.append("LaneRoute has 0 LegCounts")
                        else:
                            lane.is_error_state = True
                            lane.error_messages.append("LaneRoute info does not exist")

                        if leg_costs:
                            for leg_cost in leg_costs:
                                leg_cost_by_weight = json.loads(leg_cost.cost)[0]['CostByWeight'][0]

                                for weight_break in json.loads(request_section.weight_break_details):
                                    density_factor = 10 / \
                                        lane.weight_break_density[weight_break['LevelLowerBound']]
                                    billed_weight = density_factor * weight_break['LevelUpperBound']

                                    if density_factor != 1 and (
                                            leg_cost_by_weight['UseVolumetricWeightForCosting']
                                            or weight_break['LevelUpperBound'] > billed_weight):
                                        weight_to_use = billed_weight
                                    else:
                                        weight_to_use = weight_break['LevelUpperBound']

                                    cost = leg_cost_by_weight['RatePerUnitWeight'] * float(weight_to_use)

                                    line_haul_cost[weight_break['LevelLowerBound']] = line_haul_cost.get(
                                        weight_break['LevelLowerBound'], 0) + cost
                        else:
                            lane.is_error_state = True
                            lane.error_messages.append("LegCost info does not exist")

                        for wb_density in lane.weight_break_density:
                            line_haul_cost[wb_density] = round(line_haul_cost[wb_density] * unit_factor, 4)

                        lane.line_haul_cost = line_haul_cost
                        if debug_logging:
                            logging.info(
                                f'LaneID {lane.lane_id} between {lane.origin_terminal_id}-{lane.destination_terminal_id} - Sameday LineHaul Cost {colored(line_haul_cost,"yellow")}')
            else:
                logging.info("Invalid Service Offering Name")

        logging.info(f'*** Done Calculating Lane Haul Cost ***')

    def calculate_dock_cost(self, debug_logging=False):
        logging.info(f'*** Starting Calculating Dock Cost ***')

        terminal_cost_weight_break_levels_lower_bounds = [
            x.weight_break_lower_bound for x in self.terminal_cost_weight_break_levels]
        terminal_cost_weight_break_levels_lookup = {x.weight_break_lower_bound: x.weight_break_level_id
                                                    for x in self.terminal_cost_weight_break_levels}

        for request_section in self.section_data:
            request_section_wb_details = json.loads(request_section.weight_break_details)
            unit_factor = float(request_section.unit_factor)

            for request_section_lane in request_section.requestsectionlane_list:
                # Get all lanes in either a pricing point or request lane
                if request_section_lane.is_error_state:
                    continue

                if request_section_lane.is_lane_group:
                    lanes_list = [y
                                  for x in request_section_lane.requestsectionlanepricingpoint_list
                                  for y in x.lanes_list
                                  if not x.is_error_state]
                else:
                    lanes_list = request_section_lane.lanes_list

                # Next calculate the Dock Costs for each lane
                for lane in lanes_list:
                    dock_cost_factor = next(((x.intra_region_movement_factor
                                              if x.is_intra_region_movement_enabled else 1)
                                             for x in self.terminal_costs
                                             if x.terminal_id == lane.origin_terminal_id and x.terminal_id
                                             == lane.destination_terminal_id),
                                            1)

                    route_terminals = list(
                        set(
                            [(y['LegOriginTerminalID'], y['LegOriginTerminalCode']) if s
                             else(y['LegDestinationTerminalID'], y['LegDestinationTerminalCode'])
                             for x in lane.dockroute_list
                             for y in json.loads(x.route_legs) for s in range(2)]))

                    if request_section.sub_service_level.service_level.service_offering.service_offering_name == "Freight":
                        dock_cost = {}
                        for wb_density in lane.weight_break_density:
                            terminal_cost_weight_break_level = bisect_left(
                                terminal_cost_weight_break_levels_lower_bounds, wb_density)

                            terminal_wb_cost_total = 0

                            for terminal, terminal_code in route_terminals:
                                terminal_wb_cost = next(
                                    (x for x in self.terminal_costs if x.terminal_id == terminal), None)

                                if not terminal_wb_cost:
                                    lane.is_error_state = True
                                    lane.error_messages.append(
                                        f"Lane Dock Route has missing Terminal Costs for {terminal_code}")
                                    continue

                                # if terminal_wb_cost:
                                wb_cost = json.loads(terminal_wb_cost.cost)['CostComponents']['CostByWeightBreak'].get(str(
                                    terminal_cost_weight_break_levels_lookup[terminal_cost_weight_break_levels_lower_bounds[terminal_cost_weight_break_level]]), None)
                                if wb_cost:
                                    terminal_wb_cost_total += wb_cost
                                else:
                                    lane.is_error_state = True
                                    lane.error_messages.append("Dock cost could not be calculated")

                                # else:
                                #     lane.is_error_state = True
                                #     lane.error_messages.append(
                                #         "One or more docks could not be found or costed for the lane")

                            dock_cost[wb_density] = round(
                                (terminal_wb_cost_total / 100) *
                                float(request_section_lane.cost_override_dock_adjustment_multiplier) *
                                float(dock_cost_factor) *
                                unit_factor,
                                4)

                        lane.dock_cost = dock_cost
                        if debug_logging:
                            logging.info(
                                f'LaneID {lane.lane_id} between {lane.origin_terminal_id}-{lane.destination_terminal_id} - Freight Dock Cost {colored(dock_cost,"yellow")}')

                    elif request_section.sub_service_level.service_level.service_offering.service_offering_name == "SameDay":
                        dock_cost = {}
                        for wb_density in lane.weight_break_density:
                            terminal_wb_cost_total = 0

                            wb_upper_bound = next(x for x in request_section_wb_details
                                                  if x['LevelLowerBound'] == wb_density)['LevelUpperBound']

                            for terminal, terminal_code in route_terminals:
                                terminal_wb_cost = next(
                                    (x for x in self.terminal_costs if x.terminal_id == terminal), None)

                                if not terminal_wb_cost:
                                    lane.is_error_state = True
                                    lane.error_messages.append(
                                        f"Lane Dock Route has missing Terminal Costs for {terminal_code}")
                                    continue

                                # if terminal_wb_cost:
                                terminal_wb_cost_total += json.loads(terminal_wb_cost.cost)['CostComponents'][
                                    'CrossDockCost']['CrossDockCostPerWeightUnit']
                                # else:
                                #     lane.is_error_state = True
                                #     lane.error_messages.append(
                                #         "One or more docks could not be found or costed for the lane")

                            dock_cost[wb_density] = round(
                                terminal_wb_cost_total *
                                float(request_section_lane.cost_override_dock_adjustment_multiplier) *
                                float(dock_cost_factor) *
                                wb_upper_bound *
                                unit_factor,
                                4)

                        lane.dock_cost = dock_cost
                        if debug_logging:
                            logging.info(
                                f'LaneID {lane.lane_id} between {lane.origin_terminal_id}-{lane.destination_terminal_id} - Sameday Dock Cost {colored(dock_cost,"yellow")}')
        logging.info(f'*** Done Calculating Dock Cost ***')

    def calculate_pickup_cost(self, debug_logging=False):
        logging.info(f'*** Starting Calculating Pickup Cost ***')

        for request_section in self.section_data:
            request_section_wb_details = json.loads(request_section.weight_break_details)
            unit_factor = float(request_section.unit_factor)

            for request_section_lane in request_section.requestsectionlane_list:
                # Get all lanes in either a pricing point or request lane
                if request_section_lane.is_error_state:
                    continue

                if request_section_lane.is_lane_group:
                    lanes_list = [y
                                  for x in request_section_lane.requestsectionlanepricingpoint_list
                                  for y in x.lanes_list
                                  if not x.is_error_state]
                else:
                    lanes_list = request_section_lane.lanes_list

                if not lanes_list:
                    continue

                origin_country_id = request_section_lane.set_origin_country_id

                # Next calculate the Pickup Costs for each lane
                for lane in lanes_list:
                    if request_section.sub_service_level.service_level.service_offering.service_offering_name == "Freight":
                        pickup_cost = {}
                        for wb in lane.weight_break_density:
                            # Check for Cost Override for this WB
                            cost_override_pickup_cost_value = 0
                            if request_section_lane.cost_override_pickup_cost:
                                cost_override_pickup_cost = json.loads(request_section_lane.cost_override_pickup_cost)
                                if str(wb) in cost_override_pickup_cost:
                                    cost_override_pickup_cost_value = float(cost_override_pickup_cost[str(wb)])
                                else:
                                    cost_override_pickup_cost_value = float(cost_override_pickup_cost[wb])

                            if origin_country_id != 1:
                                wb_cost = 0
                            elif cost_override_pickup_cost_value > 0:
                                wb_cost = cost_override_pickup_cost_value / unit_factor
                            else:
                                avg_weight_per_shipment = 0
                                # avg_pickup_per_week = 0
                                avg_shipment_pickup = 0
                                override_avg_weight_per_shipment = 0
                                if self.request_data.request_profile.shipping_controls and self.request_data.request_profile.shipping_controls != '[]':
                                    shipping_controls = json.loads(self.request_data.request_profile.shipping_controls)

                                    shipping_control = next(
                                        (x for x in shipping_controls
                                         if x['origin_service_point_id']
                                         == request_section_lane.set_origin_service_point_id),
                                        None)

                                    if shipping_control:
                                        avg_weight_per_shipment = shipping_control['avg_weight_per_shipment']
                                        # avg_pickup_per_week = shipping_control['avg_pickup_per_week']
                                        avg_shipment_pickup = float(shipping_control['avg_shipment_pickup'])
                                        override_avg_weight_per_shipment = float(
                                            shipping_control['override_avg_weight_per_shipment'])

                                if request_section_lane.cost_override_pickup_count and request_section_lane.cost_override_pickup_count > 0:
                                    override_pickup_count = request_section_lane.cost_override_pickup_count
                                else:
                                    override_pickup_count = max(avg_shipment_pickup, 1)

                                pickup_weight = override_pickup_count * (override_avg_weight_per_shipment
                                                                         if override_avg_weight_per_shipment > 0 else
                                                                         max(avg_weight_per_shipment, 0))

                                weight = max(wb, pickup_weight)

                                broker_contract_cost = next((x
                                                             for x in
                                                             lane.origin_terminal.brokercontractcost_list),
                                                            None)
                                if broker_contract_cost:
                                    broker_contract_cost_data = json.loads(broker_contract_cost.cost_by_weight_break)

                                    broker_cost_by_wb_list = broker_contract_cost_data['CostComponents'][
                                        'CostByWeightBreakByPickupDeliveryCount']

                                    broker_cost_by_wb_list_max_wb = max(
                                        [x['PickupDeliveryCount'] for x in broker_cost_by_wb_list])

                                    pickup_count = min(override_pickup_count, broker_cost_by_wb_list_max_wb)
                                    broker_cost_by_wb = next(
                                        (x for x in broker_cost_by_wb_list
                                         if x['PickupDeliveryCount'] == pickup_count),
                                        None)
                                    if (broker_cost_by_wb):
                                        # Get the weight break floor from BrokerCost and use that cost
                                        wb_to_broker_cost = {x['WeightBreakLowerBound']: x
                                                             for x in broker_cost_by_wb['Cost']}

                                        wb_to_broker_cost_keys = list(wb_to_broker_cost.keys())
                                        wb_to_broker_cost_keys.sort()

                                        broker_cost_weight_break_floor = next(
                                            (x for x in wb_to_broker_cost
                                             if x ==
                                             wb_to_broker_cost_keys[bisect_right(wb_to_broker_cost_keys, weight) - 1]),
                                            None)

                                        wb_cost = wb_to_broker_cost[broker_cost_weight_break_floor]['Cost'] / 100

                                        # Adjust for density
                                        if lane.weight_break_density[wb] > 0 and lane.weight_break_density[wb] < 10:
                                            wb_cost = wb_cost * 10 / lane.weight_break_density[wb]
                                    else:
                                        lane.is_error_state = True
                                        lane.error_messages.append(
                                            "PickupDeliveryCount does not exist for Broker Contract Cost")
                                else:
                                    lane.is_error_state = True
                                    lane.error_messages.append(
                                        "Broker Contract Cost does not exist for Destination Terminal Service Level")
                                    break

                            pickup_cost[wb] = round(wb_cost * unit_factor, 4)

                        lane.pickup_cost = pickup_cost
                        if debug_logging:
                            logging.info(
                                f'LaneID {lane.lane_id} between {lane.origin_terminal_id}-{lane.destination_terminal_id} - Freight Pickup Cost {colored(pickup_cost,"yellow")}')

                    elif request_section.sub_service_level.service_level.service_offering.service_offering_name == "SameDay":
                        pickup_cost = {}
                        for wb in lane.weight_break_density:
                            # Check for Cost Override for this WB
                            cost_override_pickup_cost_value = 0
                            if request_section_lane.cost_override_pickup_cost:
                                cost_override_pickup_cost = json.loads(request_section_lane.cost_override_pickup_cost)
                                if str(wb) in cost_override_pickup_cost:
                                    cost_override_pickup_cost_value = float(cost_override_pickup_cost[str(wb)])
                                else:
                                    cost_override_pickup_cost_value = float(cost_override_pickup_cost[wb])

                            if origin_country_id != 1:
                                wb_cost = 0
                            elif cost_override_pickup_cost_value > 0:
                                wb_cost = cost_override_pickup_cost_value / unit_factor
                            else:
                                avg_weight_per_shipment = 0
                                # avg_pickup_per_week = 0
                                avg_shipment_pickup = 0
                                override_avg_weight_per_shipment = 0
                                if self.request_data.request_profile.shipping_controls and self.request_data.request_profile.shipping_controls != '[]':
                                    shipping_controls = json.loads(self.request_data.request_profile.shipping_controls)

                                    shipping_control = next(
                                        (x for x in shipping_controls
                                         if x['origin_service_point_id']
                                         == request_section_lane.set_origin_service_point_id),
                                        None)

                                    if shipping_control:
                                        avg_weight_per_shipment = shipping_control['avg_weight_per_shipment']
                                        # avg_pickup_per_week = shipping_control['avg_pickup_per_week']
                                        avg_shipment_pickup = shipping_control['avg_shipment_pickup']
                                        override_avg_weight_per_shipment = shipping_control['override_avg_weight_per_shipment']

                                if request_section_lane.cost_override_pickup_count and request_section_lane.cost_override_pickup_count > 0:
                                    override_pickup_count = request_section_lane.cost_override_pickup_count
                                else:
                                    override_pickup_count = max(avg_shipment_pickup, 1)

                                broker_contract_cost = next((x
                                                             for x in
                                                             lane.origin_terminal.brokercontractcost_list),
                                                            None)
                                if broker_contract_cost:
                                    broker_contract_cost_data = json.loads(broker_contract_cost.cost_by_weight_break)

                                    rate_base = broker_contract_cost_data['CostComponents']['CostByWeightBreak'][
                                        'RateBase']
                                    rate_max = broker_contract_cost_data['CostComponents']['CostByWeightBreak'][
                                        'RateMax']

                                    wb_to_cost = {x['WeightBreakLowerBound']: x
                                                  for x in broker_contract_cost_data['CostComponents']
                                                  ['CostByWeightBreak']['Cost']}

                                    wb_to_cost_keys_reversed = sorted(list(wb_to_cost.keys()), reverse=True)

                                    wb_upper_bound = next(x for x in request_section_wb_details
                                                          if x['LevelLowerBound'] == wb)['LevelUpperBound']

                                    weight_remaining = wb_upper_bound * override_pickup_count
                                    got_partial = False
                                    total_sum = 0
                                    for cost_wb in wb_to_cost_keys_reversed:
                                        if not got_partial:
                                            if weight_remaining > cost_wb:
                                                weight_diff = weight_remaining - cost_wb
                                                total_sum += weight_diff * wb_to_cost[cost_wb]['Cost']
                                                got_partial = True
                                        else:
                                            total_sum += wb_upper_bound * wb_to_cost[cost_wb]['Cost']

                                    total_sum_or_max = min(total_sum / override_pickup_count, rate_max)

                                    wb_cost = rate_base + total_sum_or_max
                                    # pickup_cost[wb] = round(wb_cost * unit_factor, 4)
                                else:
                                    lane.is_error_state = True
                                    lane.error_messages.append(
                                        "Broker Contract Cost does not exist for Destination Terminal Service Level")

                            pickup_cost[wb] = round(wb_cost * unit_factor, 4)

                        lane.pickup_cost = pickup_cost
                        if debug_logging:
                            logging.info(
                                f'LaneID {lane.lane_id} between {lane.origin_terminal_id}-{lane.destination_terminal_id} - SameDay Pickup Cost {colored(pickup_cost,"yellow")}')

        logging.info(f'*** Done Calculating Pickup Cost ***')

    def calculate_delivery_cost(self, debug_logging=False):
        logging.info(f'*** Starting Calculating Delivery Cost ***')

        for request_section in self.section_data:
            request_section_wb_details = json.loads(request_section.weight_break_details)
            unit_factor = float(request_section.unit_factor)

            for request_section_lane in request_section.requestsectionlane_list:
                if request_section_lane.is_error_state:
                    continue

                if request_section_lane.is_lane_group:
                    lanes_list = [y
                                  for x in request_section_lane.requestsectionlanepricingpoint_list
                                  for y in x.lanes_list
                                  if not x.is_error_state]
                else:
                    lanes_list = request_section_lane.lanes_list

                if not lanes_list:
                    continue

                destination_country_id = request_section_lane.set_destination_country_id

                # Next calculate the Delivery Costs for each lane
                for lane in lanes_list:
                    if request_section.sub_service_level.service_level.service_offering.service_offering_name == "Freight":
                        delivery_cost = {}
                        for wb in lane.weight_break_density:
                            # Check for Cost Override for this WB
                            cost_override_delivery_cost_value = 0
                            if request_section_lane.cost_override_delivery_cost:
                                cost_override_delivery_cost = json.loads(
                                    request_section_lane.cost_override_delivery_cost)
                                if str(wb) in cost_override_delivery_cost:
                                    cost_override_delivery_cost_value = float(cost_override_delivery_cost[str(wb)])
                                else:
                                    cost_override_delivery_cost_value = float(cost_override_delivery_cost[wb])

                            if destination_country_id != 1:
                                wb_cost = 0
                            elif cost_override_delivery_cost_value > 0:
                                wb_cost = cost_override_delivery_cost_value / unit_factor
                            else:
                                override_delivery_count = max(
                                    request_section_lane.cost_override_delivery_count_multiplier, 1)

                                broker_contract_cost = next((x
                                                             for x in
                                                             lane.destination_terminal.brokercontractcost_list),
                                                            None)
                                if broker_contract_cost:
                                    broker_contract_cost_data = json.loads(broker_contract_cost.cost_by_weight_break)

                                    broker_cost_by_wb_list = broker_contract_cost_data['CostComponents'][
                                        'CostByWeightBreakByPickupDeliveryCount']

                                    broker_cost_by_wb_list_max_wb = max(
                                        [x['PickupDeliveryCount'] for x in broker_cost_by_wb_list])

                                    delivery_count = min(override_delivery_count, broker_cost_by_wb_list_max_wb)
                                    broker_cost_by_wb = next(
                                        (x for x in broker_cost_by_wb_list
                                         if x['PickupDeliveryCount'] == delivery_count),
                                        None)
                                    if (broker_cost_by_wb):
                                        # Get the weight break floor from BrokerCost and use that cost
                                        wb_to_broker_cost = {x['WeightBreakLowerBound']: x
                                                             for x in broker_cost_by_wb['Cost']}

                                        wb_to_broker_cost_keys = list(wb_to_broker_cost.keys())
                                        wb_to_broker_cost_keys.sort()

                                        broker_cost_weight_break_floor = next(
                                            (x for x in wb_to_broker_cost
                                             if x ==
                                             wb_to_broker_cost_keys[bisect_right(wb_to_broker_cost_keys, wb) - 1]),
                                            None)

                                        wb_cost = wb_to_broker_cost[broker_cost_weight_break_floor]['Cost'] / 100

                                        # Adjust for density
                                        if lane.weight_break_density[wb] > 0 and lane.weight_break_density[wb] < 10:
                                            wb_cost = wb_cost * 10 / lane.weight_break_density[wb]
                                    else:
                                        lane.is_error_state = True
                                        lane.error_messages.append(
                                            "PickupDeliveryCount does not exist for Broker Contract Cost")
                                else:
                                    lane.is_error_state = True
                                    lane.error_messages.append(
                                        "Broker Contract Cost does not exist for Destination Terminal Service Level")
                                    break

                            delivery_cost[wb] = round(wb_cost * unit_factor, 4)

                        lane.delivery_cost = delivery_cost
                        if debug_logging:
                            logging.info(
                                f'LaneID {lane.lane_id} between {lane.origin_terminal_id}-{lane.destination_terminal_id} - Freight Delivery Cost {colored(delivery_cost,"yellow")}')

                    elif request_section.sub_service_level.service_level.service_offering.service_offering_name == "SameDay":
                        additional_delivery_charge = 0

                        delivery_cost = {}
                        for wb in lane.weight_break_density:
                            # Check for Cost Override for this WB
                            cost_override_delivery_cost_value = 0
                            if request_section_lane.cost_override_delivery_cost:
                                cost_override_delivery_cost = json.loads(
                                    request_section_lane.cost_override_delivery_cost)
                                if str(wb) in cost_override_delivery_cost:
                                    cost_override_delivery_cost_value = float(cost_override_delivery_cost[str(wb)])
                                else:
                                    cost_override_delivery_cost_value = float(cost_override_delivery_cost[wb])

                            if destination_country_id != 1:
                                wb_cost = 0
                            elif cost_override_delivery_cost_value > 0:
                                wb_cost = cost_override_delivery_cost_value / unit_factor
                            else:
                                override_delivery_count = max(
                                    request_section_lane.cost_override_delivery_count_multiplier, 1)

                                broker_contract_cost = next((x
                                                             for x in
                                                             lane.destination_terminal.brokercontractcost_list),
                                                            None)
                                if broker_contract_cost:
                                    broker_contract_cost_data = json.loads(broker_contract_cost.cost_by_weight_break)

                                    rate_base = broker_contract_cost_data['CostComponents']['CostByWeightBreak'][
                                        'RateBase']
                                    rate_max = broker_contract_cost_data['CostComponents']['CostByWeightBreak'][
                                        'RateMax']

                                    wb_to_cost = {x['WeightBreakLowerBound']: x
                                                  for x in broker_contract_cost_data['CostComponents']
                                                  ['CostByWeightBreak']['Cost']}

                                    wb_to_cost_keys_reversed = sorted(list(wb_to_cost.keys()), reverse=True)

                                    wb_upper_bound = next(x for x in request_section_wb_details
                                                          if x['LevelLowerBound'] == wb)['LevelUpperBound']

                                    weight_remaining = wb_upper_bound * override_delivery_count
                                    got_partial = False
                                    total_sum = 0
                                    for cost_wb in wb_to_cost_keys_reversed:
                                        if not got_partial:
                                            if weight_remaining > cost_wb:
                                                weight_diff = weight_remaining - cost_wb
                                                total_sum += weight_diff * wb_to_cost[cost_wb]['Cost']
                                                got_partial = True
                                        else:
                                            total_sum += wb_upper_bound * wb_to_cost[cost_wb]['Cost']

                                    total_sum_or_max = min(total_sum / override_delivery_count, rate_max)

                                    wb_cost = rate_base + total_sum + additional_delivery_charge
                                    # delivery_cost[wb] = round(wb_cost, 4)
                                else:
                                    lane.is_error_state = True
                                    lane.error_messages.append(
                                        "Broker Contract Cost does not exist for Destination Terminal Service Level")

                            delivery_cost[wb] = round(wb_cost * unit_factor, 4)

                        lane.delivery_cost = delivery_cost
                        if debug_logging:
                            logging.info(
                                f'LaneID {lane.lane_id} between {lane.origin_terminal_id}-{lane.destination_terminal_id} - SameDay Delivery Cost {colored(delivery_cost,"yellow")}')

        logging.info(f'*** Done Calculating Delivery Cost ***')

    def calculate_margin(self, debug_logging=False):
        logging.info(f'*** Starting Calculating Margins ***')

        profit_factor = settings.PROFIT_FACTOR
        interline_service_pickup_margin = settings.INTERLINE_SERVICE_PICKUP_MARGIN
        interline_service_delivery_margin = settings.INTERLINE_SERVICE_DELIVERY_MARGIN
        interline_pickup_minimum = settings.INTERLINE_PICKUP_MINIMUM
        interline_delivery_minimum = settings.INTERLINE_DELIVERY_MINIMUM
        interline_at_pickup = settings.INTERLINE_AT_PICKUP
        interline_at_delivery = settings.INTERLINE_AT_DELIVERY

        credit_card_margin = 0.025 if self.request_data.request_information.is_paying_by_credit_card else 0
        extended_payment_margin = self.request_data.request_information.extended_payment_terms_margin / \
            100 if self.request_data.request_information.is_extended_payment else 0

        currency_id = self.request_data.request_information.currency_id or 1
        currency_cad_to_usd = self.currency_exchange[0].cad_to_usd
        currency_usd_to_cad = self.currency_exchange[0].usd_to_cad

        revenue_commitment = 0
        if self.request_data.request_profile.shipments and self.request_data.request_profile.shipments != '[]':
            shipment_data = json.loads(self.request_data.request_profile.shipments)

            revenue_commitment = 12 * sum([int(x['CommitmentPerMonth']) for x in shipment_data])

        for request_section in self.section_data:
            request_section_weight_breaks = json.loads(request_section.weight_break_details)

            # Get the lane_cost_weight_break_lower_bound to use for bisect_right -1 splitting.
            lane_cost_weight_break_lower_bounds = [
                x.weight_break_lower_bound
                for x in self.lane_cost_weight_break_levels
                if x.service_offering_id == request_section.sub_service_level.service_level.service_offering_id]
            lane_cost_weight_break_lower_bounds.sort()

            for request_section_lane in request_section.requestsectionlane_list:
                if request_section_lane.is_error_state:
                    continue

                if request_section_lane.is_lane_group:
                    lanes_list = [y
                                  for x in request_section_lane.requestsectionlanepricingpoint_list
                                  for y in x.lanes_list
                                  if not x.is_error_state]
                else:
                    lanes_list = request_section_lane.lanes_list

                cost_override_margin_multiplier_data = None
                if request_section_lane.cost_override_margin and request_section_lane.cost_override_margin != '[]':
                    cost_override_margin_multiplier_data = json.loads(request_section_lane.cost_override_margin)

                for lane in lanes_list:
                    if lane.is_error_state:
                        continue

                    if lane.lanecost_list:
                        cost = json.loads(lane.lanecost_list[0].cost)
                        minimum_cost = float(lane.lanecost_list[0].minimum_cost)
                        # maximum_cost =  # Not yet implemented

                        if request_section.sub_service_level.service_level.service_offering.service_offering_name == "Freight":
                            wb_total_costs = {}
                            wb_margin_costs = {}
                            wb_engine_rate = {}
                            for wb in lane.weight_break_density:
                                # Check error state if one weight break fails so we don't continue
                                if lane.is_error_state:
                                    # import pdb
                                    # pdb.set_trace()
                                    continue

                                matched_wb = next((x for x in request_section_weight_breaks
                                                   if x['LevelLowerBound'] == wb), None)

                                matched_lane_cost_wb = next(
                                    (x for x in self.lane_cost_weight_break_levels
                                     if x.weight_break_lower_bound ==
                                     lane_cost_weight_break_lower_bounds
                                     [bisect_right(lane_cost_weight_break_lower_bounds,
                                                   wb) - 1] and x.service_offering_id
                                     == request_section.sub_service_level.service_level.service_offering_id),
                                    None)

                                # Data Validation
                                if not matched_wb:
                                    lane.is_error_state = True
                                    lane.error_messages.append("Weight Break not matched")
                                    continue

                                if not matched_lane_cost_wb:
                                    lane.is_error_state = True
                                    lane.error_messages.append("Lane Cost Weight Break not matched")
                                    continue

                                if str(matched_lane_cost_wb.weight_break_level_id) not in cost:
                                    lane.is_error_state = True
                                    lane.error_messages.append(
                                        f"Lane Cost does not have cost for Weight Break {matched_lane_cost_wb.weight_break_level_id}")
                                    continue

                                if matched_wb['IsMin']:
                                    logging.info('IS MIN')
                                    engine_rate = minimum_cost + interline_pickup_minimum + interline_delivery_minimum
                                    margin_cost = 0
                                elif matched_wb['IsMax']:
                                    logging.info('IS MAX')
                                    # cost = cost.maximum_cost <-- Use this when we implement maximum cost in PreCosting
                                    engine_rate = 999  # TODO: This...
                                    margin_cost = 0
                                else:
                                    cost_by_wb = float(cost[str(matched_lane_cost_wb.weight_break_level_id)])
                                    pickup_cost_by_wb = cost_by_wb  # Add condition for Interliner when that is in scope here
                                    delivery_cost_by_wb = cost_by_wb

                                    # import pdb; pdb.set_trace()

                                    cost_override_margin_multiplier = 0
                                    if cost_override_margin_multiplier_data:
                                        if str(wb) in cost_override_margin_multiplier_data:
                                            cost_override_margin_multiplier = cost_override_margin_multiplier_data[str(
                                                wb)] / 100
                                        else:
                                            cost_override_margin_multiplier = cost_override_margin_multiplier_data[wb] / 100

                                    margin_cost_transit = (
                                        (float(cost_override_margin_multiplier) +
                                         credit_card_margin + extended_payment_margin + cost_by_wb) *
                                        ((lane.line_haul_cost[wb]) + (lane.dock_cost[wb])))
                                    margin_cost_pickup = (
                                        (float(cost_override_margin_multiplier) +
                                         credit_card_margin + extended_payment_margin +
                                         pickup_cost_by_wb) * lane.pickup_cost[wb])  # + @PickupCost.Cost
                                    margin_cost_delivery = (
                                        (float(cost_override_margin_multiplier) +
                                            credit_card_margin + extended_payment_margin +
                                            delivery_cost_by_wb) * lane.delivery_cost[wb])

                                    margin_cost = margin_cost_transit + margin_cost_pickup + margin_cost_delivery

                                    engine_rate = (lane.line_haul_cost[wb] +
                                                   lane.dock_cost[wb] +
                                                   lane.pickup_cost[wb] +
                                                   lane.delivery_cost[wb] +
                                                   margin_cost
                                                   )

                                total_cost = engine_rate / profit_factor

                                if currency_id != 1:
                                    total_cost = total_cost * currency_cad_to_usd

                                wb_total_costs[wb] = round(total_cost, 4)
                                wb_margin_costs[wb] = round(margin_cost, 4)
                                wb_engine_rate[wb] = round(engine_rate, 4)

                            lane.margin_cost = wb_margin_costs
                            lane.total_cost = wb_total_costs
                            lane.engine_rate = wb_engine_rate
                            if debug_logging:
                                logging.info(
                                    f'LaneID {lane.lane_id} between {lane.origin_terminal_id}-{lane.destination_terminal_id} - Freight Margin {colored(wb_margin_costs,"yellow")} Total Cost {colored(wb_total_costs, "yellow")}')

                        elif request_section.sub_service_level.service_level.service_offering.service_offering_name == "SameDay":

                            # if not revenue_commitment:
                            #     lane.is_error_state = True
                            #     lane.error_messages.append("No Revenue Commitment data on Request")
                            #     import pdb; pdb.set_trace()
                            #     continue

                            matched_lane_cost_wb = next(
                                (x for x in self.lane_cost_weight_break_levels
                                 if x.weight_break_lower_bound ==
                                 lane_cost_weight_break_lower_bounds
                                 [bisect_right(lane_cost_weight_break_lower_bounds,
                                               revenue_commitment) - 1] and x.service_offering_id
                                 == request_section.sub_service_level.service_level.service_offering_id),
                                None)

                            if not matched_lane_cost_wb:
                                lane.is_error_state = True
                                lane.error_messages.append("Lane Cost Weight Break not matched")
                                # import pdb
                                # pdb.set_trace()
                                continue

                            if str(matched_lane_cost_wb.weight_break_level_id) not in cost:
                                lane.is_error_state = True
                                lane.error_messages.append(
                                    f"Lane Cost does not have cost for Weight Break {matched_lane_cost_wb.weight_break_level_id}")
                                # import pdb
                                # pdb.set_trace()
                                continue

                            cost_by_wb = float(cost[str(matched_lane_cost_wb.weight_break_level_id)])

                            wb_total_costs = {}
                            wb_margin_costs = {}
                            wb_engine_rate = {}
                            previous_wb_costed_rate = 0
                            for wb in lane.weight_break_density:
                                # Check error state if one weight break fails so we don't continue
                                if lane.is_error_state:
                                    continue

                                matched_wb = next((x for x in request_section_weight_breaks
                                                   if x['LevelLowerBound'] == wb), None)

                                pickup_cost_by_wb = cost_by_wb  # Add condition for Interliner when that is in scope here
                                delivery_cost_by_wb = cost_by_wb

                                cost_override_margin_multiplier = 0
                                if cost_override_margin_multiplier_data:
                                    if str(wb) in cost_override_margin_multiplier_data:
                                        cost_override_margin_multiplier = cost_override_margin_multiplier_data[str(wb)]
                                    else:
                                        cost_override_margin_multiplier = cost_override_margin_multiplier_data[wb]

                                margin_cost_transit = (
                                    (float(cost_override_margin_multiplier) +
                                        credit_card_margin + extended_payment_margin + cost_by_wb) *
                                    ((lane.line_haul_cost[wb]) + (lane.dock_cost[wb])))
                                margin_cost_pickup = (
                                    (float(cost_override_margin_multiplier) + credit_card_margin +
                                     extended_payment_margin + pickup_cost_by_wb) * lane.pickup_cost[wb])
                                margin_cost_delivery = (
                                    (float(cost_override_margin_multiplier) +
                                     credit_card_margin + extended_payment_margin +
                                     delivery_cost_by_wb) * lane.delivery_cost[wb])

                                margin_cost = margin_cost_transit + margin_cost_pickup + margin_cost_delivery

                                costed_rate = (lane.line_haul_cost[wb] +
                                               lane.dock_cost[wb] +
                                               lane.pickup_cost[wb] +
                                               lane.delivery_cost[wb] +
                                               margin_cost
                                               )

                                if matched_wb['IsMin'] or matched_wb['IsMax']:
                                    engine_rate = ((costed_rate - previous_wb_costed_rate) /
                                                   (matched_wb['LevelUpperBound'] - matched_wb['LevelLowerBound']))

                                    # import pdb
                                    # pdb.set_trace()

                                else:
                                    engine_rate = costed_rate

                                total_cost = engine_rate / profit_factor
                                # TODO: Change to check InMix/IsMax flag for static cost vs per lb calc.

                                if currency_id != 1:
                                    total_cost = total_cost * currency_cad_to_usd

                                wb_total_costs[wb] = round(total_cost, 4)
                                wb_margin_costs[wb] = round(margin_cost, 4)
                                wb_engine_rate[wb] = round(engine_rate, 4)

                                previous_wb_costed_rate = costed_rate

                            lane.margin_cost = wb_margin_costs
                            lane.total_cost = wb_total_costs
                            lane.engine_rate = wb_engine_rate
                            if debug_logging:
                                logging.info(
                                    f'LaneID {lane.lane_id} between {lane.origin_terminal_id}-{lane.destination_terminal_id} - SameDay Margin {wb_margin_costs} Total Cost {wb_total_costs}')

                    else:
                        lane.is_error_state = True
                        lane.error_messages.append("LaneCost info does not exist")

        logging.info(f'*** Done Calculating Margins ***')

    def calculate_fak_rate(self, debug_logging=False):
        logging.info(f'*** Starting Calculating FAK Rates ***')

        ltl_rate_ship_request_list = []
        pricing_point_dict = {}

        for request_section in self.section_data:
            for request_section_lane in request_section.requestsectionlane_list:
                if request_section_lane.is_error_state:
                    continue

                # FAK Rates only computed for pricing points
                if request_section_lane.is_lane_group:
                    for pricing_point in request_section_lane.requestsectionlanepricingpoint_list:
                        if pricing_point.is_error_state:
                            continue

                        if not pricing_point.lanes_list:
                            continue

                        origin_country_id = request_section_lane.set_origin_country_id
                        destination_country_id = request_section_lane.set_destination_country_id

                        pricing_point_dict[pricing_point.request_section_lane_pricing_point_id] = pricing_point

                        # Hardcoded mapping of Country to RateWare codes
                        # Only supports CAN and USA
                        rw_origin_country_code = 'CAN' if origin_country_id == 1 else 'USA'
                        rw_destination_country_code = 'CAN' if destination_country_id == 1 else 'USA'

                        rw_origin_postal_code = pricing_point.set_origin_postal_code_name
                        rw_destination_postal_code = pricing_point.set_destination_postal_code_name
                        rw_origin_postal_code = rw_origin_postal_code.replace('-', '').replace(' ', '')
                        rw_destination_postal_code = rw_destination_postal_code.replace('-', '').replace(' ', '')

                        for lane in pricing_point.lanes_list:
                            lane.fak_rate = {}

                            if not request_section.rate_base or not request_section.rate_base.is_active:
                                lane.is_error_state = True
                                lane.error_messages.append("Rate Base does not exist or is Inactive")
                                continue
                            else:
                                rw_rate_name = request_section.rate_base.rate_base_name
                                rw_rate_description = request_section.rate_base.description
                                rw_rate_effective_date = request_section.rate_base.effective_date.strftime('%Y%m%d')
                                rw_rate_product_number = request_section.rate_base.product_number
                                rw_rate_release = request_section.rate_base.release

                            if not request_section.override_class or not request_section.override_class.is_active:
                                lane.is_error_state = True
                                lane.error_messages.append("Freight Class does not exist or is Inactive")
                                continue
                            else:
                                rw_freight_class = request_section.override_class.freight_class_name

                            # TODO: Testing Data
                            # rw_destination_country_code = 'CAN'
                            # rw_destination_postal_code = 'E1A7P5'
                            # rw_origin_country_code = 'USA'
                            # rw_origin_postal_code = '20505'
                            # rw_freight_class = 50

                            for wb in lane.weight_break_density:
                                ltl_rate_ship_request = {
                                    'LTL_Surcharge': None,
                                    'TL_Surcharge': None,
                                    'destinationCity': None,
                                    'destinationCountry': rw_destination_country_code,
                                    'destinationPostalCode': rw_destination_postal_code,
                                    'destinationState': None,
                                    'details': [],
                                    'discountApplication': None,
                                    'mcDiscount': None,
                                    'orgDestToGateWayPointFlag': None,
                                    'originCity': None,
                                    'originCountry': rw_origin_country_code,
                                    'originPostalCode': rw_origin_postal_code,
                                    'originState': None,
                                    'rateAdjustmentFactor': None,
                                    'shipmentDateCCYYMMDD': rw_rate_effective_date,
                                    'shipmentID': pricing_point.request_section_lane_pricing_point_id,
                                    'stopAlternationWeight': None,
                                    'surchargeApplication': None,
                                    'tariffName': rw_rate_name,
                                    'useDiscounts': None,
                                    'useSingleShipmentCharges': None,
                                    'userMinimumChargeFloor': None,
                                    'weightBreak_Discount_1': None,
                                    'weightBreak_Discount_2': None,
                                    'weightBreak_Discount_3': None,
                                    'weightBreak_Discount_4': None,
                                    'weightBreak_Discount_5': None,
                                    'weightBreak_Discount_6': None,
                                    'weightBreak_Discount_7': None,
                                    'weightBreak_Discount_8': None,
                                    'weightBreak_Discount_9': None,
                                    'weightBreak_Discount_10': None,
                                    'weightBreak_Discount_11': None
                                }

                                rw_wb_details = {
                                    'nmfcClass': rw_freight_class,
                                    'weight': 1 if wb == 0 else wb
                                }

                                ltl_rate_ship_request['details'].append(rw_wb_details)
                                ltl_rate_ship_request_list.append(ltl_rate_ship_request)

        rate_responses = ltl_rate_shipment_multiple(ltl_rate_ship_request_list)
        error_lookup = {}

        if rate_responses:
            # TODO: Add check if we send a pricing point to RateWare but it is not contained in the response.

            for rate_response in rate_responses:
                pricing_point_id = rate_response['shipmentID']
                error_code = rate_response['errorCode']
                wb = int(rate_response['details']['LTLResponseDetail'][0]['weight'])
                wb = 0 if wb == 1 else wb
                rate = rate_response['details']['LTLResponseDetail'][0]['rate']

                pricing_point = pricing_point_dict[int(pricing_point_id)]
                if not pricing_point.lanes_list:
                    continue
                lane = pricing_point.lanes_list[0]

                if error_code and error_code != '0':
                    if error_code not in error_lookup:
                        error_lookup[error_code] = error_code_lookup(error_code)

                    # Errors on the weight break level clears all other weight breaks
                    lane.fak_rate = {}

                    # Check for Rateware errors, so that multiple weight breaks having the same errors does not cause multiple error messages.
                    if not hasattr(lane, 'is_rateware_error_state'):
                        lane.is_error_state = True
                        lane.is_rateware_error_state = True
                        lane.error_messages.append(
                            f"Rateware Error {error_lookup[error_code]['code']} Description: {error_lookup[error_code]['description']} Resolution: {error_lookup[error_code]['resolution']}")
                    continue

                # Save WB to Lane
                unit_factor = pricing_point.request_section_lane.request_section.unit_factor
                lane.fak_rate[wb] = round(float(Decimal(rate) / 100 * unit_factor), 4)
        else:
            if debug_logging:
                if ltl_rate_ship_request_list == []:
                    logging.info(f'No data returned from RateWare due to no Pricing Points to rate')
                else:
                    logging.info(f'No data returned from RateWare for request')

        if debug_logging:
            for request_section in self.section_data:
                for request_section_lane in request_section.requestsectionlane_list:
                    # FAK Rates only computed for pricing points
                    if request_section_lane.is_lane_group:
                        for pricing_point in request_section_lane.requestsectionlanepricingpoint_list:
                            for lane in pricing_point.lanes_list:

                                logging.info(
                                    f'PricingPointID {pricing_point.request_section_lane_pricing_point_id} between {lane.origin_terminal_id}-{lane.destination_terminal_id} - FAK Rate {colored(lane.fak_rate,"yellow")}')

        logging.info(f'*** Done Calculating FAK Rates ***')

    def calculate_splits_all(self, debug_logging=False):
        logging.info(f'*** Starting Calculating SplitsAll ***')

        for request_section in self.section_data:
            if request_section.sub_service_level.service_level.pricing_type != 'US-LTL':
                continue

            cnxn = pyodbc_connection()
            cursor = cnxn.cursor()
            for request_section_lane in request_section.requestsectionlane_list:
                if request_section_lane.is_lane_group:
                    for pricing_point in request_section_lane.requestsectionlanepricingpoint_list:

                        origin_postal_code = pricing_point.origin_postal_code_name.replace(' ', '')
                        destination_postal_code = pricing_point.destination_postal_code_name.replace(' ', '')
                        # TODO: Temporary values
                        gateway_terminal_temp = 'E7J2B4'
                        revenue = 1000

                        cursor.execute("SELECT * FROM [dbo].[getD83SPLIT] (?, ?, ?, ?)",
                                       origin_postal_code,
                                       destination_postal_code,
                                       gateway_terminal_temp,
                                       revenue)

                        raw_data = cursor.fetchone()

                        if raw_data:
                            pricing_point.splits_all = json.dumps(
                                {"orig": float(raw_data[0]), "dest": float(raw_data[1])})

                        if debug_logging:
                            logging.info(
                                f'PricingPointID {pricing_point.request_section_lane_pricing_point_id} - SplitsAll {colored(pricing_point.splits_all,"yellow")}')

        logging.info(f'*** Done Calculating SplitsAll ***')

    def calculate_profitability(self, debug_logging=False):
        logging.info(f'*** Starting Profitability ***')

        for request_section in self.section_data:
            if request_section.sub_service_level.service_level.pricing_type != 'US-LTL':
                continue

            request_section_weight_breaks = json.loads(request_section.weight_break_details)

            for request_section_lane in request_section.requestsectionlane_list:
                request_section_lane.set_profitability = {}

                # Load and convert to int keys
                customer_discount_json = json.loads(request_section_lane.customer_discount)
                partner_discount_json = json.loads(request_section_lane.partner_discount)
                customer_discount = {int(x): customer_discount_json[x] for x in customer_discount_json}
                partner_discount = {int(x): partner_discount_json[x] for x in partner_discount_json}

                # Only evaluate Lane Group (Pricing Points)
                if request_section_lane.is_lane_group:
                    # Determine Pricing Point Usage Percentage
                    total_usage_percentage = sum(
                        float(x.splits_all_usage_percentage)
                        for x in request_section_lane.requestsectionlanepricingpoint_list)
                    total_usage_percentage_count = len(request_section_lane.requestsectionlanepricingpoint_list)

                    for pricing_point in request_section_lane.requestsectionlanepricingpoint_list:
                        if not pricing_point.lanes_list:
                            continue

                        if not pricing_point.splits_all_usage_percentage or float(
                                pricing_point.splits_all_usage_percentage) == 0:
                            usage_percentage = (100 - total_usage_percentage) / total_usage_percentage_count
                        else:
                            usage_percentage = float(pricing_point.splits_all_usage_percentage)

                        if request_section_lane.set_origin_country_id == 2:
                            partner_split = json.loads(pricing_point.splits_all)['orig']
                        elif request_section_lane.set_origin_country_id == 1:
                            partner_split = json.loads(pricing_point.splits_all)['dest']

                        for lane in pricing_point.lanes_list:
                            if lane.is_error_state:
                                continue

                            if total_usage_percentage > 100:
                                lane.is_error_state = True
                                lane.error_messages.append(
                                    "Total Usage Percentages for Pricing Points under Lane exceeds 100 Percent")
                                continue

                            if not request_section_lane.set_profitability:
                                request_section_lane.set_profitability = {
                                    x: 0 for x in lane.weight_break_density.keys()}

                            pp_profitability = {}
                            for wb in lane.weight_break_density:
                                matched_wb = next((x for x in request_section_weight_breaks
                                                   if x['LevelLowerBound'] == wb), None)

                                if matched_wb['IsMin']:
                                    logging.info('IS MIN')
                                    pp_prof = 0
                                elif matched_wb['IsMax']:
                                    logging.info('IS MAX')
                                    pp_prof = 0
                                else:
                                    fak_rate = lane.fak_rate[wb] if wb in lane.fak_rate else 0
                                    pp_prof = (
                                        ((100 - customer_discount[wb]) / 100 * fak_rate) -
                                        ((100 - partner_discount[wb]) / 100 * fak_rate *
                                         partner_split) - (lane.engine_rate[wb])) / lane.engine_rate[wb] * 100

                                    # import pdb; pdb.set_trace()

                                pp_profitability[wb] = round(pp_prof, 4)
                                request_section_lane.set_profitability[wb] += (pp_prof * (usage_percentage / 100))

                            pricing_point.set_profitability = json.dumps(pp_profitability)

                            if debug_logging:
                                logging.info(
                                    f'  LaneID {lane.lane_id} between {lane.origin_terminal_id}-{lane.destination_terminal_id} - Profitability {pricing_point.set_profitability}')

                    # Round
                    for wb in request_section_lane.set_profitability.keys():
                        request_section_lane.set_profitability[wb] = round(
                            request_section_lane.set_profitability[wb], 4)
                    request_section_lane.set_profitability = json.dumps(request_section_lane.set_profitability)

                    if debug_logging:
                        logging.info(
                            f'Request Section LaneID {request_section_lane.request_section_lane_id} Profitability {request_section_lane.set_profitability}')

        logging.info(f'*** Done Profitability ***')

    def calculate_rates(self, debug_logging=False):
        logging.info(f'*** Starting Determine Rate ***')

        class RateColor(Enum):
            USER_MODIFIED = 0
            ENGINE_RATE_USED = 1
            COMMITMENT_RATE_USED = 2
            PUBLISHED_RATE_USED = 3

        class WeightBreakRate():
            def __init__(self):
                self.cost = 0
                self.colour_code = None

                self.line_haul_cost = 0
                self.dock_cost = 0
                self.pickup_cost = 0
                self.delivery_cost = 0
                self.margin = 0
                self.accessorials = 0
                self.total_cost = 0

        is_new_business = self.request_data.request_information.is_new_business or False
        request_type = self.request_data.request_information.request_type.request_type_name
        is_speed_sheet = self.request_data.uni_type == 'SPEEDSHEET'

        for request_section in self.section_data:
            request_section.weight_break_details

            for request_section_lane in request_section.requestsectionlane_list:

                if request_section_lane.is_error_state:
                    continue

                # Get all lanes in either a pricing point or request lane
                if request_section_lane.is_lane_group:
                    lanes_list = [(x, y) for x
                                  in request_section_lane.requestsectionlanepricingpoint_list
                                  for y in x.lanes_list]
                    is_pricing_point = True
                else:
                    lanes_list = [(request_section_lane, request_section_lane.lanes_list[0])
                                  ] if request_section_lane.lanes_list else []
                    is_pricing_point = False

                # import pdb
                # pdb.set_trace()

                # Next calculate the Costs for each lane
                for lane_pair in lanes_list:
                    lane_parent = lane_pair[0]
                    lane = lane_pair[1]

                    # Handle error state lanes, do not process
                    if lane.is_error_state:
                        lane_return = {
                            "error_state": lane.is_error_state,
                            "error_date": str(date.today()),
                            "error_messages": lane.error_messages
                        }

                        # import pdb; pdb.set_trace()

                        lane_parent.workflow_errors = json.dumps(lane_return)

                        # import pdb
                        # pdb.set_trace()

                        if debug_logging:
                            if is_pricing_point:
                                logging.info(
                                    f'Pricing Point of LaneID {lane.lane_id} between {lane.origin_terminal_id}-{lane.destination_terminal_id} has error: {lane_parent.workflow_errors}')
                            else:
                                logging.info(
                                    f'Lane of LaneID {lane.lane_id} between {lane.origin_terminal_id}-{lane.destination_terminal_id} has error: {lane_parent.workflow_errors}')
                    else:
                        if lane.weight_break_density:
                            wb_rates = {}
                            wb_cost = {}
                            wb_cost_speed_sheet = {}

                            commitment_rates = json.loads(request_section_lane.commitment)
                            for wb in lane.weight_break_density:
                                cost = lane.engine_rate[wb]
                                colour_id = RateColor.ENGINE_RATE_USED

                                if is_new_business or request_type == "Commitment":
                                    # Determine if we need to compare engine rate to commitment or published rate

                                    if is_speed_sheet:
                                        # Do not use commitment or published rates if SpeedSheet
                                        wb_cost_speed_sheet[wb] = round(
                                            cost * self.SPEED_SHEET_PROFIT_MARGIN_MULTIPLIER, 4)
                                    else:
                                        # CompareRates

                                        commitment_cost = 0
                                        if wb in commitment_rates:
                                            commitment_cost = commitment_rates[wb]
                                        if str(wb) in commitment_rates:
                                            commitment_cost = commitment_rates[str(wb)]

                                        if commitment_cost > 0 and commitment_cost > cost:
                                            cost = commitment_cost
                                            colour_id = RateColor.COMMITMENT_RATE_USED

                                    pass
                                elif not is_new_business and request_type != "Commitment":
                                    # Determine if we only need to embed rate with updated accessorial values

                                    # import pdb
                                    # pdb.set_trace()

                                    # EmbedRates
                                    pass

                                wb_rate = WeightBreakRate()
                                wb_rate.cost = cost
                                wb_rate.colour_code = colour_id.value
                                wb_rate.line_haul_cost = lane.line_haul_cost[wb]
                                wb_rate.pickup_cost = lane.pickup_cost[wb]
                                wb_rate.delivery_cost = lane.delivery_cost[wb]
                                wb_rate.dock_cost = lane.dock_cost[wb]
                                wb_rate.margin = lane.margin_cost[wb]
                                wb_rate.total_cost = lane.total_cost[wb]

                                wb_rates[wb] = wb_rate.__dict__
                                wb_cost[wb] = cost

                            # Only commit the WB that are send to be calculated, use existing data for the rest.
                            if not self.rating_filters_calculate_all:
                                # Get current rates in system
                                current_pricing_rates = json.loads(lane_parent.pricing_rates or '{}')
                                if request_section.sub_service_level.service_level.pricing_type == 'US-LTL' or is_pricing_point:
                                    current_pricing_costs = json.loads(lane_parent.dr_rate or lane_parent.dr_rate_clear)
                                else:
                                    current_pricing_costs = json.loads(
                                        lane_parent.customer_rate or lane_parent.customer_rate_clear)

                                # Overwrite engine rates with existing rates for WB that do not need to be rated.
                                if is_pricing_point:
                                    # Use weight break filters for parent lane
                                    request_section_lane_id = lane_parent.request_section_lane.request_section_lane_id
                                    filter_wb_json = self.rating_filters_request_lane_wb[request_section_lane_id]
                                else:
                                    filter_wb_json = self.rating_filters_request_lane_wb[lane_parent.request_section_lane_id]

                                # If WB does not need to be rated, replace with existing values
                                for wb in wb_rates:
                                    if wb not in filter_wb_json:
                                        wb_rates[wb] = current_pricing_rates[wb] if wb in current_pricing_rates else None
                                        wb_cost[wb] = round(
                                            float(
                                                current_pricing_costs[wb] if wb in current_pricing_costs
                                                else current_pricing_costs[str(wb)] if str(wb) in current_pricing_costs
                                                else 0
                                            ), 4)

                            # import pdb; pdb.set_trace()

                            # Speed sheet multiple rates by Speed Sheet Profit Factor
                            if is_speed_sheet:
                                wb_cost_speed_sheet = {}
                                for wb in wb_cost:
                                    wb_cost_speed_sheet[wb] = round(
                                        wb_cost[wb] * self.SPEED_SHEET_PROFIT_MARGIN_MULTIPLIER, 4)

                            # Assign data
                            lane_parent.pricing_rates = json.dumps(wb_rates)
                            if debug_logging:
                                logging.info(
                                    f'LaneID {lane.lane_id} between {lane.origin_terminal_id}-{lane.destination_terminal_id} - Cost {wb_rates}')

                            # Write data to Lane Parent (Request Lane or Request Lane Pricing Point) record
                            if is_pricing_point:
                                lane_parent.dr_rate = json.dumps(wb_cost)

                                if hasattr(lane_parent, 'set_profitability') and lane_parent.set_profitability:
                                    lane_parent.profitability = lane_parent.set_profitability
                                if hasattr(request_section_lane, 'set_profitability') and request_section_lane.set_profitability:
                                    request_section_lane.profitability = request_section_lane.set_profitability
                            else:
                                if is_speed_sheet:
                                    lane_parent.commitment = json.dumps(wb_cost_speed_sheet)

                                if request_section.sub_service_level.service_level.pricing_type == 'US-LTL':
                                    lane_parent.dr_rate = json.dumps(wb_cost)
                                else:
                                    lane_parent.customer_rate = json.dumps(wb_cost)

                        # Add computed FAK Rates to Request Lane Pricing Point
                        if hasattr(lane, 'fak_rate'):
                            lane_parent.fak_rate = json.dumps(lane.fak_rate)

        # import pdb
        # pdb.set_trace()
        logging.info(f'*** Done Determine Rate ***')

    # TODO: Atmoic Transaction
    def save_data(self, debug_logging=False):
        logging.info(f'*** Starting Save Data ***')

        pricing_point_save_list = []
        request_section_lane_save_list = []

        for request_section in self.section_data:
            request_section_lanes = request_section.requestsectionlane_list
            request_section_lanes_pricing_points = [y
                                                    for x in request_section.requestsectionlane_list
                                                    for y in x.requestsectionlanepricingpoint_list]

            # # Version Up
            # for lane in request_section_lanes:
            #     lane.version_num += 1
            # for pricing_point in request_section_lanes_pricing_points:
            #     pricing_point.version_num += 1

            logging.info(f"Summary Of Request Section {request_section.request_section_id}")
            logging.info(f"    Request Section Lanes: {len(request_section_lanes)}")
            logging.info(f"        Errors: {len([x for x in request_section_lanes if x.workflow_errors])}")
            logging.info(f"    Request Section Pricing Points: {len(request_section_lanes_pricing_points)}")
            logging.info(
                f"        Errors: {len([x for x in request_section_lanes_pricing_points if x.workflow_errors])}")

            # import pdb
            # pdb.set_trace()

            for request_section_lane in request_section.requestsectionlane_list:
                if request_section_lane.is_lane_group:
                    for pricing_point in request_section_lane.requestsectionlanepricingpoint_list:
                        logging.info(
                            f'Adding Lane {request_section_lane.request_section_lane_id} - Pricing Point {pricing_point.request_section_lane_pricing_point_id}')
                        pricing_point_save_list.append(pricing_point)

                    logging.info(f'Adding Lane {request_section_lane.request_section_lane_id}')
                    request_section_lane_save_list.append(request_section_lane)
                else:
                    logging.info(f'Adding Lane {request_section_lane.request_section_lane_id}')
                    request_section_lane_save_list.append(request_section_lane)

        # Save
        logging.info(f"Running Bulk Save - {len(request_section_lane_save_list)} - Request Section Lanes")
        self.run_bulk_save(request_section_lane_save_list, update_fields=[
                           'profitability', 'dr_rate', 'customer_rate', 'pricing_rates', 'workflow_errors', 'commitment'])

        logging.info(f"Running Bulk Save - {len(pricing_point_save_list)} - Pricing Points")
        self.run_bulk_save(pricing_point_save_list, update_fields=[
                           'profitability', 'dr_rate', 'fak_rate', 'splits_all', 'pricing_rates', 'workflow_errors'])

        logging.info(f"Saving RequestInformation")
        self.request_data.request_information.save()

        logging.info(f'*** Done Save Data ***')

    def run_bulk_save(self, entities, update_fields):
        BULK_SAVE_BATCH_SIZE = 150
        # entities_chunks = [entities[i * BULK_SAVE_BATCH_SIZE: (i + 1) * BULK_SAVE_BATCH_SIZE]
        #                    for i in range((len(entities) + BULK_SAVE_BATCH_SIZE - 1) // BULK_SAVE_BATCH_SIZE)]

        # for chunk in entities_chunks:
        logging.info(f"     Saving {len(entities)} records")
        update_instance_history_bulk(entities, globals(), batch_size=BULK_SAVE_BATCH_SIZE, update_fields=update_fields)
