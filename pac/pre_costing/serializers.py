import json

from rest_framework import serializers

from pac.models import (City, CityHistory, Country, CountryHistory, Province,
                        ProvinceHistory, Region, ServiceOffering, Terminal, WeightBreakHeader)
from pac.pre_costing.models import (BrokerContractCost,
                                    BrokerContractCostHistory,
                                    CurrencyExchange, CurrencyExchangeHistory,
                                    DockRoute, DockRouteHistory, Lane,
                                    LaneCost, LaneCostHistory,
                                    LaneCostWeightBreakLevel, LaneRoute, LaneRouteHistory, LegCost,
                                    LegCostHistory, RequestLog, SpeedSheet,
                                    SpeedSheetHistory, TerminalCost,
                                    TerminalCostHistory,
                                    TerminalCostWeightBreakLevel,
                                    TerminalServicePoint,
                                    TerminalServicePointHistory, Unit, GriReview)


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = "__all__"
        read_only_fields = ['is_active', 'is_inactive_viewable', 'country_id']


class CountryRegularSerializer(serializers.Serializer):
    country_id = serializers.IntegerField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    country_name = serializers.CharField(max_length=50, read_only=True)
    country_code = serializers.CharField(max_length=2, read_only=True)


class ProvinceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Province
        fields = "__all__"
        read_only_fields = ['is_active', 'is_inactive_viewable', 'province_id']


class ProvinceRegularSerializer(serializers.Serializer):
    province_id = serializers.IntegerField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    province_name = serializers.CharField(read_only=True)
    province_code = serializers.CharField(read_only=True)
    region = serializers.CharField(read_only=True)


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = "__all__"
        read_only_fields = ['is_active', 'is_inactive_viewable', 'city_id']


class CityRegularSerializer(serializers.Serializer):
    city_id = serializers.IntegerField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    city_name = serializers.CharField(max_length=50, read_only=True)
    province = serializers.PrimaryKeyRelatedField(read_only=True)


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = "__all__"
        read_only_fields = ['is_active', 'is_inactive_viewable', 'region_id']


class RegionRegularSerializer(serializers.Serializer):
    region_id = serializers.IntegerField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    region_name = serializers.CharField(max_length=50, read_only=True)
    region_code = serializers.CharField(max_length=4, read_only=True)
    country = serializers.CharField(read_only=True)


class TerminalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Terminal
        fields = "__all__"
        read_only_fields = ['is_inactive_viewable', 'terminal_id']


class TerminalCostSerializer(serializers.ModelSerializer):
    class Meta:
        model = TerminalCost
        fields = "__all__"
        read_only_fields = ['is_inactive_viewable', 'terminal_cost_id']


class LaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lane
        fields = "__all__"
        read_only_fields = ['lane_id']


class DockRouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = DockRoute
        fields = "__all__"
        read_only_fields = ['dock_route_id']


class LaneRouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = LaneRoute
        fields = "__all__"
        read_only_fields = ['lane_route_id']


class LaneCostSerializer(serializers.ModelSerializer):
    class Meta:
        model = LaneCost
        fields = "__all__"
        read_only_fields = ['lane_cost_id']


class LegCostSerializer(serializers.ModelSerializer):
    class Meta:
        model = LegCost
        fields = "__all__"
        read_only_fields = ['leg_cost_id']


class BrokerContractCostSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrokerContractCost
        fields = "__all__"
        read_only_fields = ['broker_contract_cost_id']


class CurrencyExchangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurrencyExchange
        fields = "__all__"
        read_only_fields = ['currency_exchange_id',
                            'is_active', 'is_inactive_viewable']


class SpeedSheetSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpeedSheet
        fields = "__all__"
        read_only_fields = ['speed_sheet_id',
                            'is_active', 'is_inactive_viewable']


class TerminalServicePointSerializer(serializers.ModelSerializer):
    class Meta:
        model = TerminalServicePoint
        fields = "__all__"
        read_only_fields = ['terminal_service_point_id',
                            'is_active', 'is_inactive_viewable']


class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = "__all__"
        read_only_fields = ['unit_id', 'is_active', 'is_inactive_viewable']


class WeightBreakHeaderSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeightBreakHeader
        fields = "__all__"
        read_only_fields = ['weight_break_header_id']


class LaneCostWeightBreakLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = LaneCostWeightBreakLevel
        fields = "__all__"
        read_only_fields = ['weight_break_level_id',
                            'is_active', 'is_inactive_viewable']


class TerminalCostWeightBreakLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = TerminalCostWeightBreakLevel
        fields = "__all__"
        read_only_fields = ['weight_break_level_id',
                            'is_active', 'is_inactive_viewable']


class TerminalRegularSerializer(serializers.Serializer):
    terminal_id = serializers.IntegerField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    terminal_code = serializers.CharField(max_length=3, read_only=True)
    terminal_name = serializers.CharField(max_length=40, read_only=True)
    city = serializers.PrimaryKeyRelatedField(read_only=True)
    region = serializers.PrimaryKeyRelatedField(read_only=True)


class ServiceOfferingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceOffering
        fields = "__all__"
        read_only_fields = ['is_active',
                            'is_inactive_viewable', 'service_offering_id']


class ServiceOfferingRegularSerializer(serializers.Serializer):
    service_offering_id = serializers.IntegerField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    service_offering_name = serializers.CharField(
        max_length=50, read_only=True)


class CountryBulkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        exclude = ['is_active', 'country_id']


class ProvinceBulkSerializer(serializers.ModelSerializer):
    region_code = serializers.CharField(max_length=4)

    class Meta:
        model = Province
        exclude = ['is_active', 'province_id', 'region_id']


class CityBulkSerializer(serializers.ModelSerializer):
    province_code = serializers.CharField(max_length=2)

    class Meta:
        model = City
        exclude = ['is_active', 'city_id', 'province_id']


class CountryHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CountryHistory
        fields = "__all__"


class ProvinceHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProvinceHistory
        fields = "__all__"


class CityHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CityHistory
        fields = "__all__"


class RequestLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestLog
        fields = "__all__"


class DockCostsDashboardSerializer(serializers.ModelSerializer):
    terminal_id = serializers.SerializerMethodField()
    terminal_code = serializers.SerializerMethodField()
    terminal_is_active = serializers.SerializerMethodField()
    city_id = serializers.SerializerMethodField()
    city_name = serializers.SerializerMethodField()
    province_id = serializers.SerializerMethodField()
    province_code = serializers.SerializerMethodField()
    region_id = serializers.SerializerMethodField()
    region_name = serializers.SerializerMethodField()
    service_offering_id = serializers.SerializerMethodField()
    cost = serializers.SerializerMethodField()
    updated_on = serializers.SerializerMethodField()

    def get_terminal_id(self, obj):
        return obj.terminal_id

    def get_terminal_code(self, obj):
        return obj.terminal.terminal_code

    def get_terminal_is_active(self, obj):
        return obj.terminal.is_active

    def get_city_id(self, obj):
        return obj.terminal.city_id

    def get_city_name(self, obj):
        return obj.terminal.city.city_name

    def get_province_id(self, obj):
        return obj.terminal.city.province_id

    def get_province_code(self, obj):
        return obj.terminal.city.province.province_code

    def get_region_id(self, obj):
        return obj.terminal.region_id

    def get_region_name(self, obj):
        return obj.terminal.region.region_name

    def get_service_offering_id(self, obj):
        return obj.service_offering_id

    def get_cost(self, obj):
        return json.loads(obj.cost)

    def get_updated_on(self, obj):
        terminal_cost_latest_history_version = TerminalCostHistory.objects.filter(
            terminal_cost=obj, is_latest_version=True).first()
        if terminal_cost_latest_history_version:
            return terminal_cost_latest_history_version.updated_on

    class Meta:
        model = TerminalCost
        fields = ['terminal_cost_id', 'terminal_id', 'terminal_code', 'terminal_is_active', 'city_id', 'city_name',
                  'province_id', 'province_code',
                  'region_id', 'region_name', 'service_offering_id', 'cost', 'is_intra_region_movement_enabled',
                  'intra_region_movement_factor', 'is_active', 'updated_on']


class DockCostsDetailPanelSerializer(serializers.ModelSerializer):
    terminal_id = serializers.SerializerMethodField()
    terminal_code = serializers.SerializerMethodField()
    terminal_cost_history = serializers.SerializerMethodField()
    updated_on = serializers.SerializerMethodField()

    def get_terminal_id(self, obj):
        return obj.terminal_id

    def get_terminal_code(self, obj):
        return obj.terminal.terminal_code

    def get_updated_on(self, obj):
        terminal_cost_latest_history_version = TerminalCostHistory.objects.filter(
            terminal_cost=obj, is_latest_version=True).first()
        if terminal_cost_latest_history_version:
            return terminal_cost_latest_history_version.updated_on

    def get_terminal_cost_history(self, obj):
        terminal_cost_history = TerminalCostHistory.objects.filter(
            terminal_cost=obj)
        return DockCostsDetailPanelHistorySerializer(terminal_cost_history, many=True).data

    class Meta:
        model = TerminalCost
        fields = ['terminal_cost_id', 'terminal_id', 'terminal_code',
                  'updated_on', 'terminal_cost_history', 'is_active']


class DockCostsDetailPanelHistorySerializer(serializers.ModelSerializer):
    cost = serializers.SerializerMethodField()

    def get_cost(self, obj):
        return json.loads(obj.cost)

    class Meta:
        model = TerminalCostHistory
        fields = ['terminal_cost_version_id', 'cost', 'version_num',
                  'is_latest_version', 'updated_on', 'is_active']


class CrossDockRoutesDashboardSeriaizer(serializers.ModelSerializer):
    origin_terminal_id = serializers.SerializerMethodField()
    origin_terminal_code = serializers.SerializerMethodField()
    origin_province_id = serializers.SerializerMethodField()
    origin_province_code = serializers.SerializerMethodField()
    origin_region_id = serializers.SerializerMethodField()
    origin_region_code = serializers.SerializerMethodField()
    destination_terminal_id = serializers.SerializerMethodField()
    destination_terminal_code = serializers.SerializerMethodField()
    destination_province_id = serializers.SerializerMethodField()
    destination_province_code = serializers.SerializerMethodField()
    destination_region_code = serializers.SerializerMethodField()
    destination_region_id = serializers.SerializerMethodField()
    service_level_id = serializers.SerializerMethodField()
    service_level_code = serializers.SerializerMethodField()
    updated_on = serializers.SerializerMethodField()

    def get_origin_terminal_id(self, obj):
        return obj.lane.origin_terminal_id

    def get_origin_terminal_code(self, obj):
        return obj.lane.origin_terminal.terminal_code

    def get_origin_province_id(self, obj):
        return obj.lane.origin_terminal.city.province_id

    def get_origin_province_code(self, obj):
        return obj.lane.origin_terminal.city.province.province_code

    def get_origin_region_id(self, obj):
        return obj.lane.origin_terminal.region_id

    def get_origin_region_code(self, obj):
        return obj.lane.origin_terminal.region.region_code

    def get_destination_terminal_id(self, obj):
        return obj.lane.destination_terminal_id

    def get_destination_terminal_code(self, obj):
        return obj.lane.destination_terminal.terminal_code

    def get_destination_province_id(self, obj):
        return obj.lane.destination_terminal.city.province_id

    def get_destination_province_code(self, obj):
        return obj.lane.destination_terminal.city.province.province_code

    def get_destination_region_id(self, obj):
        return obj.lane.destination_terminal.region_id

    def get_destination_region_code(self, obj):
        return obj.lane.destination_terminal.region.region_code

    def get_service_level_id(self, obj):
        return obj.lane.sub_service_level.service_level.service_level_id

    def get_service_level_code(self, obj):
        return obj.lane.sub_service_level.service_level.service_level_code

    def get_updated_on(self, obj):
        dock_route_latest_history_version = DockRouteHistory.objects.filter(
            is_latest_version=True, dock_route=obj).first()
        if dock_route_latest_history_version:
            return dock_route_latest_history_version.updated_on

    class Meta:
        model = DockRoute
        fields = ['dock_route_id', 'origin_terminal_id', 'origin_terminal_code', 'origin_province_id',
                  'origin_province_code', 'origin_region_id', 'origin_region_code', 'destination_terminal_id',
                  'destination_terminal_code',
                  'destination_province_id', 'destination_province_code', 'destination_region_code',
                  'destination_region_id', 'service_level_id', 'service_level_code', 'updated_on', 'is_active']


class CrossDockRoutesDetailPanelSerializer(serializers.ModelSerializer):
    origin_terminal_id = serializers.SerializerMethodField()
    origin_terminal_code = serializers.SerializerMethodField()
    destination_terminal_id = serializers.SerializerMethodField()
    destination_terminal_code = serializers.SerializerMethodField()
    service_level_id = serializers.SerializerMethodField()
    service_level_code = serializers.SerializerMethodField()
    route_legs = serializers.SerializerMethodField()
    updated_on = serializers.SerializerMethodField()

    def get_origin_terminal_id(self, obj):
        return obj.lane.origin_terminal_id

    def get_origin_terminal_code(self, obj):
        return obj.lane.origin_terminal.terminal_code

    def get_destination_terminal_id(self, obj):
        return obj.lane.destination_terminal_id

    def get_destination_terminal_code(self, obj):
        return obj.lane.destination_terminal.terminal_code

    def get_service_level_id(self, obj):
        return obj.lane.sub_service_level.service_level.service_level_id

    def get_service_level_code(self, obj):
        return obj.lane.sub_service_level.service_level.service_level_code

    def get_route_legs(self, obj):
        return json.loads(obj.route_legs)

    def get_updated_on(self, obj):
        dock_route_latest_history_version = DockRouteHistory.objects.filter(
            is_latest_version=True, dock_route=obj).first()
        if dock_route_latest_history_version:
            return dock_route_latest_history_version.updated_on

    class Meta:
        model = DockRoute
        fields = ['is_exclude_destination', 'is_exclude_source', 'dock_route_id', 'origin_terminal_id',
                  'origin_terminal_code', 'destination_terminal_id',
                  'destination_terminal_code', 'service_level_id', 'service_level_code', 'route_legs', 'updated_on',
                  'is_active']


class LinehaulLaneRoutesDashboardSerializer(serializers.ModelSerializer):
    origin_terminal_id = serializers.SerializerMethodField()
    origin_terminal_code = serializers.SerializerMethodField()
    origin_province_id = serializers.SerializerMethodField()
    origin_province_code = serializers.SerializerMethodField()
    origin_region_id = serializers.SerializerMethodField()
    origin_region_code = serializers.SerializerMethodField()
    destination_terminal_id = serializers.SerializerMethodField()
    destination_terminal_code = serializers.SerializerMethodField()
    destination_province_id = serializers.SerializerMethodField()
    destination_province_code = serializers.SerializerMethodField()
    destination_region_code = serializers.SerializerMethodField()
    destination_region_id = serializers.SerializerMethodField()
    service_level_id = serializers.SerializerMethodField()
    service_level_code = serializers.SerializerMethodField()
    updated_on = serializers.SerializerMethodField()

    def get_origin_terminal_id(self, obj):
        return obj.lane.origin_terminal_id

    def get_origin_terminal_code(self, obj):
        return obj.lane.origin_terminal.terminal_code

    def get_origin_province_id(self, obj):
        return obj.lane.origin_terminal.city.province_id

    def get_origin_province_code(self, obj):
        return obj.lane.origin_terminal.city.province.province_code

    def get_origin_region_id(self, obj):
        return obj.lane.origin_terminal.region_id

    def get_origin_region_code(self, obj):
        return obj.lane.origin_terminal.region.region_code

    def get_destination_terminal_id(self, obj):
        return obj.lane.destination_terminal_id

    def get_destination_terminal_code(self, obj):
        return obj.lane.destination_terminal.terminal_code

    def get_destination_province_id(self, obj):
        return obj.lane.destination_terminal.city.province_id

    def get_destination_province_code(self, obj):
        return obj.lane.destination_terminal.city.province.province_code

    def get_destination_region_id(self, obj):
        return obj.lane.destination_terminal.region_id

    def get_destination_region_code(self, obj):
        return obj.lane.destination_terminal.region.region_code

    def get_service_level_id(self, obj):
        return obj.lane.sub_service_level.service_level.service_level_id

    def get_service_level_code(self, obj):
        return obj.lane.sub_service_level.service_level.service_level_code

    def get_updated_on(self, obj):
        lane_route_latest_history_version = LaneRouteHistory.objects.filter(
            is_latest_version=True, lane_route=obj).first()
        if lane_route_latest_history_version:
            return lane_route_latest_history_version.updated_on

    class Meta:
        model = LaneRoute
        fields = ['lane_route_id', 'origin_terminal_id', 'origin_terminal_code', 'origin_province_id',
                  'origin_province_code', 'origin_region_id', 'origin_region_code', 'destination_terminal_id',
                  'destination_terminal_code',
                  'destination_province_id', 'destination_province_code', 'destination_region_code',
                  'destination_region_id', 'service_level_id', 'service_level_code', 'is_headhaul', 'updated_on',
                  'is_active']


class LinehaulLaneRoutesDetailPanelSerializer(serializers.ModelSerializer):
    origin_terminal_id = serializers.SerializerMethodField()
    origin_terminal_code = serializers.SerializerMethodField()
    destination_terminal_id = serializers.SerializerMethodField()
    destination_terminal_code = serializers.SerializerMethodField()
    service_level_id = serializers.SerializerMethodField()
    service_level_code = serializers.SerializerMethodField()
    route_legs = serializers.SerializerMethodField()
    updated_on = serializers.SerializerMethodField()
    is_headhaul = serializers.SerializerMethodField()

    def get_origin_terminal_id(self, obj):
        return obj.lane.origin_terminal_id

    def get_origin_terminal_code(self, obj):
        return obj.lane.origin_terminal.terminal_code

    def get_destination_terminal_id(self, obj):
        return obj.lane.destination_terminal_id

    def get_destination_terminal_code(self, obj):
        return obj.lane.destination_terminal.terminal_code

    def get_service_level_id(self, obj):
        return obj.lane.sub_service_level.service_level.service_level_id

    def get_service_level_code(self, obj):
        return obj.lane.sub_service_level.service_level.service_level_code

    def get_is_headhaul(self, obj):
        return obj.lane.is_headhaul

    def get_route_legs(self, obj):
        return json.loads(obj.route_legs)

    def get_updated_on(self, obj):
        lane_route_latest_history_version = LaneRouteHistory.objects.filter(
            is_latest_version=True, lane_route=obj).first()
        if lane_route_latest_history_version:
            return lane_route_latest_history_version.updated_on

    class Meta:
        model = LaneRoute
        fields = ['lane_route_id', 'origin_terminal_id', 'origin_terminal_code', 'destination_terminal_id',
                  'destination_terminal_code', 'service_level_id', 'service_level_code', 'route_legs', 'is_headhaul',
                  'updated_on', 'is_active']


class LinehaulCostsDashboardSerializer(serializers.ModelSerializer):
    origin_terminal_id = serializers.SerializerMethodField()
    origin_terminal_code = serializers.SerializerMethodField()
    origin_province_id = serializers.SerializerMethodField()
    origin_province_code = serializers.SerializerMethodField()
    origin_region_id = serializers.SerializerMethodField()
    origin_region_code = serializers.SerializerMethodField()
    destination_terminal_id = serializers.SerializerMethodField()
    destination_terminal_code = serializers.SerializerMethodField()
    destination_province_id = serializers.SerializerMethodField()
    destination_province_code = serializers.SerializerMethodField()
    destination_region_code = serializers.SerializerMethodField()
    destination_region_id = serializers.SerializerMethodField()
    lanes = serializers.SerializerMethodField()
    legs = serializers.SerializerMethodField()

    def get_origin_terminal_id(self, obj):
        return obj.origin_terminal_id

    def get_origin_terminal_code(self, obj):
        return obj.origin_terminal.terminal_code

    def get_origin_province_id(self, obj):
        return obj.origin_terminal.city.province_id

    def get_origin_province_code(self, obj):
        return obj.origin_terminal.city.province.province_code

    def get_origin_region_id(self, obj):
        return obj.origin_terminal.region_id

    def get_origin_region_code(self, obj):
        return obj.origin_terminal.region.region_code

    def get_destination_terminal_id(self, obj):
        return obj.destination_terminal_id

    def get_destination_terminal_code(self, obj):
        return obj.destination_terminal.terminal_code

    def get_destination_province_id(self, obj):
        return obj.destination_terminal.city.province_id

    def get_destination_province_code(self, obj):
        return obj.destination_terminal.city.province.province_code

    def get_destination_region_id(self, obj):
        return obj.destination_terminal.region_id

    def get_destination_region_code(self, obj):
        return obj.destination_terminal.region.region_code

    def get_lanes(self, obj):
        lane_cost = LaneCost.objects.filter(
            lane=obj, lane__sub_service_level__service_level__service_offering_id=self.context["service_offering_id"],
            is_inactive_viewable=True)
        if lane_cost:
            return LinehaulLaneCostsDashboardSerializer(lane_cost, many=True).data
        return []

    def get_legs(self, obj):
        leg_cost = LegCost.objects.filter(
            lane=obj, lane__sub_service_level__service_level__service_offering_id=self.context["service_offering_id"],
            is_inactive_viewable=True)
        if leg_cost:
            return LinehaulLegCostsDashboardSerializer(leg_cost, many=True).data
        return []

    class Meta:
        model = Lane
        fields = ['lane_id', 'origin_terminal_id', 'origin_terminal_code', 'origin_province_id', 'origin_province_code',
                  'origin_region_id', 'origin_region_code', 'destination_terminal_id',
                  'destination_terminal_code', 'destination_province_id', 'destination_province_code',
                  'destination_region_code', 'destination_region_id', 'lanes', 'legs', 'is_active']


class LinehaulLaneCostsDashboardSerializer(serializers.ModelSerializer):
    lane_id = serializers.SerializerMethodField()
    origin_terminal_id = serializers.SerializerMethodField()
    origin_terminal_code = serializers.SerializerMethodField()
    origin_province_id = serializers.SerializerMethodField()
    origin_province_code = serializers.SerializerMethodField()
    origin_region_id = serializers.SerializerMethodField()
    origin_region_code = serializers.SerializerMethodField()
    destination_terminal_id = serializers.SerializerMethodField()
    destination_terminal_code = serializers.SerializerMethodField()
    destination_province_id = serializers.SerializerMethodField()
    destination_province_code = serializers.SerializerMethodField()
    destination_region_code = serializers.SerializerMethodField()
    destination_region_id = serializers.SerializerMethodField()
    service_level_id = serializers.SerializerMethodField()
    service_level_code = serializers.SerializerMethodField()
    cost = serializers.SerializerMethodField()
    updated_on = serializers.SerializerMethodField()
    is_headhaul = serializers.SerializerMethodField()

    def get_lane_id(self, obj):
        return obj.lane_id

    def get_origin_terminal_id(self, obj):
        return obj.lane.origin_terminal_id

    def get_origin_terminal_code(self, obj):
        return obj.lane.origin_terminal.terminal_code

    def get_origin_province_id(self, obj):
        return obj.lane.origin_terminal.city.province_id

    def get_origin_province_code(self, obj):
        return obj.lane.origin_terminal.city.province.province_code

    def get_origin_region_id(self, obj):
        return obj.lane.origin_terminal.region_id

    def get_origin_region_code(self, obj):
        return obj.lane.origin_terminal.region.region_code

    def get_destination_terminal_id(self, obj):
        return obj.lane.destination_terminal_id

    def get_destination_terminal_code(self, obj):
        return obj.lane.destination_terminal.terminal_code

    def get_destination_province_id(self, obj):
        return obj.lane.destination_terminal.city.province_id

    def get_destination_province_code(self, obj):
        return obj.lane.destination_terminal.city.province.province_code

    def get_destination_region_id(self, obj):
        return obj.lane.destination_terminal.region_id

    def get_destination_region_code(self, obj):
        return obj.lane.destination_terminal.region.region_code

    def get_service_level_id(self, obj):
        return obj.lane.sub_service_level.service_level.service_level_id

    def get_service_level_code(self, obj):
        return obj.lane.sub_service_level.service_level.service_level_code

    def get_cost(self, obj):
        return json.loads(obj.cost)

    def get_updated_on(self, obj):
        lane_cost_latest_history_version = LaneCostHistory.objects.filter(
            is_latest_version=True, lane_cost=obj).first()
        if lane_cost_latest_history_version:
            return lane_cost_latest_history_version.updated_on

    def get_is_headhaul(self, obj):
        return obj.lane.is_headhaul

    class Meta:
        model = LaneCost
        fields = ['lane_cost_id', 'lane_id', 'origin_terminal_id', 'origin_terminal_code', 'origin_province_id',
                  'origin_province_code', 'origin_region_id', 'origin_region_code', 'destination_terminal_id',
                  'destination_terminal_code', 'destination_province_id', 'destination_province_code',
                  'destination_region_code', 'destination_region_id', 'is_active', 'lane_cost_id', 'service_level_id',
                  'service_level_code', 'cost', 'updated_on', 'is_headhaul', 'is_active']


class LinehaulLegCostsDashboardSerializer(serializers.ModelSerializer):
    lane_id = serializers.SerializerMethodField()
    origin_terminal_id = serializers.SerializerMethodField()
    origin_terminal_code = serializers.SerializerMethodField()
    origin_province_id = serializers.SerializerMethodField()
    origin_province_code = serializers.SerializerMethodField()
    origin_region_id = serializers.SerializerMethodField()
    origin_region_code = serializers.SerializerMethodField()
    destination_terminal_id = serializers.SerializerMethodField()
    destination_terminal_code = serializers.SerializerMethodField()
    destination_province_id = serializers.SerializerMethodField()
    destination_province_code = serializers.SerializerMethodField()
    destination_region_code = serializers.SerializerMethodField()
    destination_region_id = serializers.SerializerMethodField()
    service_mode_id = serializers.SerializerMethodField()
    service_mode_code = serializers.SerializerMethodField()
    service_level_id = serializers.SerializerMethodField()
    service_level_code = serializers.SerializerMethodField()
    cost = serializers.SerializerMethodField()
    updated_on = serializers.SerializerMethodField()

    def get_lane_id(self, obj):
        return obj.lane_id

    def get_origin_terminal_id(self, obj):
        return obj.lane.origin_terminal_id

    def get_origin_terminal_code(self, obj):
        return obj.lane.origin_terminal.terminal_code

    def get_origin_province_id(self, obj):
        return obj.lane.origin_terminal.city.province_id

    def get_origin_province_code(self, obj):
        return obj.lane.origin_terminal.city.province.province_code

    def get_origin_region_id(self, obj):
        return obj.lane.origin_terminal.region_id

    def get_origin_region_code(self, obj):
        return obj.lane.origin_terminal.region.region_code

    def get_destination_terminal_id(self, obj):
        return obj.lane.destination_terminal_id

    def get_destination_terminal_code(self, obj):
        return obj.lane.destination_terminal.terminal_code

    def get_destination_province_id(self, obj):
        return obj.lane.destination_terminal.city.province_id

    def get_destination_province_code(self, obj):
        return obj.lane.destination_terminal.city.province.province_code

    def get_destination_region_id(self, obj):
        return obj.lane.destination_terminal.region_id

    def get_destination_region_code(self, obj):
        return obj.lane.destination_terminal.region.region_code

    def get_service_mode_id(self, obj):
        return obj.service_mode_id

    def get_service_mode_code(self, obj):
        return obj.service_mode.service_mode_code

    def get_service_level_id(self, obj):
        return obj.lane.sub_service_level.service_level.service_level_id

    def get_service_level_code(self, obj):
        return obj.lane.sub_service_level.service_level.service_level_code

    def get_cost(self, obj):
        return json.loads(obj.cost)

    def get_updated_on(self, obj):
        leg_cost_latest_history_version = LegCostHistory.objects.filter(
            is_latest_version=True, leg_cost=obj).first()
        if leg_cost_latest_history_version:
            return leg_cost_latest_history_version.updated_on

    class Meta:
        model = LegCost
        fields = ['leg_cost_id', 'lane_id', 'origin_terminal_id', 'origin_terminal_code', 'origin_province_id',
                  'origin_province_code', 'origin_region_id', 'origin_region_code', 'destination_terminal_id',
                  'destination_terminal_code', 'destination_province_id', 'destination_province_code',
                  'destination_region_code', 'destination_region_id', 'is_active', 'service_mode_id',
                  'service_mode_code', 'service_level_id', 'service_level_code', 'cost', 'updated_on', 'is_active']


class LinehaulLaneCostsDetailPanelSerializer(serializers.ModelSerializer):
    origin_terminal_id = serializers.SerializerMethodField()
    origin_terminal_code = serializers.SerializerMethodField()
    destination_terminal_id = serializers.SerializerMethodField()
    destination_terminal_code = serializers.SerializerMethodField()
    service_level_id = serializers.SerializerMethodField()
    service_level_code = serializers.SerializerMethodField()
    updated_on = serializers.SerializerMethodField()
    lane_cost_history = serializers.SerializerMethodField()
    is_headhaul = serializers.SerializerMethodField()

    def get_origin_terminal_id(self, obj):
        return obj.lane.origin_terminal_id

    def get_origin_terminal_code(self, obj):
        return obj.lane.origin_terminal.terminal_code

    def get_destination_terminal_id(self, obj):
        return obj.lane.destination_terminal_id

    def get_destination_terminal_code(self, obj):
        return obj.lane.destination_terminal.terminal_code

    def get_service_level_id(self, obj):
        return obj.lane.sub_service_level.service_level.service_level_id

    def get_service_level_code(self, obj):
        return obj.lane.sub_service_level.service_level.service_level_code

    def get_is_headhaul(self, obj):
        return obj.lane.is_headhaul

    def get_updated_on(self, obj):
        lane_cost_latest_history_version = LaneCostHistory.objects.filter(
            is_latest_version=True, lane_cost=obj).first()
        if lane_cost_latest_history_version:
            return lane_cost_latest_history_version.updated_on

    def get_lane_cost_history(self, obj):
        lane_cost_history = LaneCostHistory.objects.filter(lane_cost=obj)
        if lane_cost_history:
            return LinehaulLaneCostsDetailPanelHistorySerializer(lane_cost_history, many=True).data
        return []

    class Meta:
        model = LaneCost
        fields = ['lane_cost_id', 'origin_terminal_id', 'origin_terminal_code', 'destination_terminal_id',
                  'destination_terminal_code', 'service_level_id', 'service_level_code', 'is_headhaul',
                  'lane_cost_history', 'updated_on', 'is_active']


class LinehaulLaneCostsDetailPanelHistorySerializer(serializers.ModelSerializer):
    cost = serializers.SerializerMethodField()
    minimum_cost = serializers.SerializerMethodField()

    def get_cost(self, obj):
        return json.loads(obj.cost)

    def get_minimum_cost(self, obj):
        return obj.minimum_cost

    class Meta:
        model = LaneCostHistory
        fields = ['lane_cost_version_id', 'cost', 'minimum_cost', 'version_num',
                  'is_latest_version', 'updated_on', 'is_active']


class LinehaulLegCostsDetailPanelSerializer(serializers.ModelSerializer):
    origin_terminal_id = serializers.SerializerMethodField()
    origin_terminal_code = serializers.SerializerMethodField()
    destination_terminal_id = serializers.SerializerMethodField()
    destination_terminal_code = serializers.SerializerMethodField()
    service_level_id = serializers.SerializerMethodField()
    service_level_code = serializers.SerializerMethodField()
    service_mode_id = serializers.SerializerMethodField()
    service_mode_code = serializers.SerializerMethodField()
    updated_on = serializers.SerializerMethodField()
    leg_cost_history = serializers.SerializerMethodField()

    def get_origin_terminal_id(self, obj):
        return obj.lane.origin_terminal_id

    def get_origin_terminal_code(self, obj):
        return obj.lane.origin_terminal.terminal_code

    def get_destination_terminal_id(self, obj):
        return obj.lane.destination_terminal_id

    def get_destination_terminal_code(self, obj):
        return obj.lane.destination_terminal.terminal_code

    def get_service_level_id(self, obj):
        return obj.lane.sub_service_level.service_level.service_level_id

    def get_service_level_code(self, obj):
        return obj.lane.sub_service_level.service_level.service_level_code

    def get_service_mode_id(self, obj):
        return obj.service_mode_id

    def get_service_mode_code(self, obj):
        return obj.service_mode.service_mode_code

    def get_updated_on(self, obj):
        leg_cost_latest_history_version = LegCostHistory.objects.filter(
            is_latest_version=True, leg_cost=obj).first()
        if leg_cost_latest_history_version:
            return leg_cost_latest_history_version.updated_on

    def get_leg_cost_history(self, obj):
        leg_cost_history = LegCostHistory.objects.filter(leg_cost=obj)
        if leg_cost_history:
            return LinehaulLegCostsDetailPanelHistorySerializer(leg_cost_history, many=True).data
        return []

    class Meta:
        model = LegCost
        fields = ['leg_cost_id', 'origin_terminal_id', 'origin_terminal_code', 'destination_terminal_id',
                  'destination_terminal_code',
                  'service_level_id', 'service_level_code', 'service_mode_id', 'service_mode_code', 'leg_cost_history',
                  'updated_on', 'is_active']


class LinehaulLegCostsDetailPanelHistorySerializer(serializers.ModelSerializer):
    cost = serializers.SerializerMethodField()

    def get_cost(self, obj):
        return json.loads(obj.cost)

    class Meta:
        model = LegCostHistory
        fields = ['leg_cost_version_id', 'cost', 'version_num',
                  'is_latest_version', 'updated_on', 'is_active']



class BrokerContractDetailPanelSerializer(serializers.ModelSerializer):
    terminal_id = serializers.SerializerMethodField()
    terminal_code = serializers.SerializerMethodField()
    service_level_id = serializers.SerializerMethodField()
    sub_service_level_id = serializers.SerializerMethodField()
    sub_service_level_code = serializers.SerializerMethodField()
    updated_on = serializers.SerializerMethodField()
    broker_contract_cost_history = serializers.SerializerMethodField()

    def get_terminal_id(self, obj):
        return obj.terminal_id

    def get_terminal_code(self, obj):
        return obj.terminal.terminal_code

    def get_service_level_id(self, obj):
        return obj.sub_service_level.service_level.service_level_id

    def get_sub_service_level_id(self, obj):
        return obj.sub_service_level.sub_service_level_id

    def get_sub_service_level_code(self, obj):
        return obj.sub_service_level.sub_service_level_code

    def get_updated_on(self, obj):
        broker_contract_cost_latest_history_version = BrokerContractCostHistory.objects.filter(
            is_latest_version=True, broker_contract_cost=obj).first()
        if broker_contract_cost_latest_history_version:
            return broker_contract_cost_latest_history_version.updated_on

    def get_broker_contract_cost_history(self, obj):
        broker_contract_cost_history = BrokerContractCostHistory.objects.filter(
            broker_contract_cost=obj)
        if broker_contract_cost_history:
            return BrokerContractDetailPanelHistorySerializer(broker_contract_cost_history, many=True).data
        return []

    class Meta:
        model = BrokerContractCost
        fields = ['broker_contract_cost_id', 'terminal_id', 'terminal_code', 'service_level_id',
                  'sub_service_level_id', 'sub_service_level_code', 'broker_contract_cost_history', 'updated_on', 'is_active']


class BrokerContractDetailPanelHistorySerializer(serializers.ModelSerializer):
    cost_by_weight_break = serializers.SerializerMethodField()

    def get_cost_by_weight_break(self, obj):
        return json.loads(obj.cost_by_weight_break)

    class Meta:
        model = BrokerContractCostHistory
        fields = ['broker_contract_cost_version_id', 'cost_by_weight_break', 'version_num',
                  'is_latest_version', 'updated_on', 'is_active']


class DockRouteDashboardCreateSerializer(serializers.ModelSerializer):
    lane = LaneSerializer()

    def create(self, validated_data):
        lane_data = validated_data.pop("lane")
        lane_instance = Lane.objects.filter(**lane_data).first()
        if not lane_instance:
            lane_instance = Lane.objects.create(**lane_data)
        dock_route = DockRoute.objects.create(
            lane=lane_instance, **validated_data)
        return dock_route

    class Meta:
        model = DockRoute
        fields = "__all__"
        read_only_fields = ['is_active',
                            'is_inactive_viewable', 'dock_route_id']


class LaneRouteDashboardCreateSerializer(serializers.ModelSerializer):
    lane = LaneSerializer()

    def create(self, validated_data):
        lane_data = validated_data.pop("lane")
        lane_instance = Lane.objects.filter(**lane_data).first()
        if not lane_instance:
            lane_instance = Lane.objects.create(**lane_data)
        lane_route = LaneRoute.objects.create(
            lane=lane_instance, **validated_data)
        return lane_route

    class Meta:
        model = LaneRoute
        fields = "__all__"
        read_only_fields = ['is_active',
                            'is_inactive_viewable', 'lane_route_id']


class LegCostDashboardCreateUpdateSerializer(serializers.ModelSerializer):
    lane = LaneSerializer()

    def create(self, validated_data):
        lane_data = validated_data.pop("lane")
        lane_instance = Lane.objects.filter(**lane_data).first()
        if not lane_instance:
            lane_instance = Lane.objects.create(**lane_data)
        leg_cost = LegCost.objects.create(
            lane=lane_instance, **validated_data)
        return leg_cost

    def update(self, instance, validated_data):
        lane_data = validated_data.pop("lane")
        lane_instance = Lane.objects.filter(**lane_data).first()
        if not lane_instance:
            lane_instance = Lane.objects.create(**lane_data)
        validated_data["lane"] = lane_instance
        return super().update(instance, validated_data)

    class Meta:
        model = LegCost
        fields = "__all__"
        read_only_fields = ['is_active',
                            'is_inactive_viewable', 'leg_cost_id']


class LaneCostDashboardCreateUpdateSerializer(serializers.ModelSerializer):
    lane = LaneSerializer()

    def create(self, validated_data):
        lane_data = validated_data.pop("lane")
        lane_instance = Lane.objects.filter(**lane_data).first()
        if not lane_instance:
            lane_instance = Lane.objects.create(**lane_data)
        lane_cost = LaneCost.objects.create(
            lane=lane_instance, **validated_data)
        return lane_cost

    def update(self, instance, validated_data):
        lane_data = validated_data.pop("lane")
        lane_instance = Lane.objects.filter(**lane_data).first()
        if not lane_instance:
            lane_instance = Lane.objects.create(**lane_data)
        validated_data["lane"] = lane_instance
        return super().update(instance, validated_data)

    class Meta:
        model = LaneCost
        fields = "__all__"
        read_only_fields = ['is_active',
                            'is_inactive_viewable', 'lane_cost_id']


class CurrencyExchangeDashboardSerializer(serializers.ModelSerializer):
    currency_exchange_history = serializers.SerializerMethodField()

    def get_currency_exchange_history(self, obj):
        currency_exchange_history = CurrencyExchangeHistory.objects.filter(
            currency_exchange=obj)
        if currency_exchange_history:
            return CurrencyExchangeDashboardHistorySerializer(currency_exchange_history, many=True).data
        return []

    class Meta:
        model = CurrencyExchange
        fields = ['currency_exchange_id', 'cad_to_usd',
                  'usd_to_cad', 'currency_exchange_history', 'is_active']


class CurrencyExchangeDashboardHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CurrencyExchangeHistory
        fields = ['currency_exchange_version_id', 'cad_to_usd',
                  'usd_to_cad', 'version_num', 'is_latest_version', 'is_active', 'updated_on']


class SpeedSheetDashboardSerializer(serializers.ModelSerializer):
    speed_sheet_history = serializers.SerializerMethodField()

    def get_speed_sheet_history(self, obj):
        speed_sheet_history = SpeedSheetHistory.objects.filter(
            speed_sheet=obj)
        if speed_sheet_history:
            return SpeedSheetDashboardHistorySerializer(speed_sheet_history, many=True).data
        return []

    class Meta:
        model = SpeedSheet
        fields = ['speed_sheet_id', 'margin',
                  'max_density', 'min_density', 'service_offering', 'speed_sheet_history', 'is_active']


class SpeedSheetDashboardHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SpeedSheetHistory
        fields = ['speed_sheet_version_id', 'margin', 'max_density', 'min_density',
                  'service_offering_version', 'version_num', 'is_latest_version', 'is_active', 'updated_on']


class PointsExtraMilesDashboardSerializer(serializers.ModelSerializer):
    terminal_id = serializers.SerializerMethodField()
    terminal_code = serializers.SerializerMethodField()
    service_point_id = serializers.SerializerMethodField()
    service_point_name = serializers.SerializerMethodField()
    service_point_province_id = serializers.SerializerMethodField()
    service_point_province_code = serializers.SerializerMethodField()
    base_service_point_id = serializers.SerializerMethodField()
    base_service_point_name = serializers.SerializerMethodField()
    base_service_point_province_id = serializers.SerializerMethodField()
    base_service_point_province_code = serializers.SerializerMethodField()
    updated_on = serializers.SerializerMethodField()

    def get_terminal_id(self, obj):
        return obj.terminal_id

    def get_terminal_code(self, obj):
        return obj.terminal.terminal_code

    def get_service_point_id(self, obj):
        return obj.service_point_id

    def get_service_point_name(self, obj):
        return obj.service_point.service_point_name

    def get_service_point_province_id(self, obj):
        return obj.service_point.province_id

    def get_service_point_province_code(self, obj):
        return obj.service_point.province.province_code

    def get_base_service_point_id(self, obj):
        return obj.base_service_point_id

    def get_base_service_point_name(self, obj):
        return obj.base_service_point.service_point_name

    def get_base_service_point_province_id(self, obj):
        return obj.base_service_point.province_id

    def get_base_service_point_province_code(self, obj):
        return obj.base_service_point.province.province_code

    def get_updated_on(self, obj):
        return obj.terminalservicepointhistory_set.first().updated_on

    class Meta:
        model = TerminalServicePoint
        fields = ['terminal_service_point_id', 'terminal_id', 'terminal_code', 'service_point_id', 'service_point_name',
                  'service_point_province_id',
                  'service_point_province_code', 'base_service_point_id', 'base_service_point_name',
                  'base_service_point_province_id', 'base_service_point_province_code', 'extra_miles', 'is_active',
                  'updated_on']


class PointsExtraMilesDetailPanelSerializer(serializers.ModelSerializer):
    terminal_id = serializers.SerializerMethodField()
    terminal_code = serializers.SerializerMethodField()
    service_point_id = serializers.SerializerMethodField()
    service_point_name = serializers.SerializerMethodField()
    service_point_province_id = serializers.SerializerMethodField()
    service_point_province_code = serializers.SerializerMethodField()
    base_service_point_id = serializers.SerializerMethodField()
    base_service_point_name = serializers.SerializerMethodField()
    base_service_point_province_id = serializers.SerializerMethodField()
    base_service_point_province_code = serializers.SerializerMethodField()
    base_service_point_province_code = serializers.SerializerMethodField()
    updated_on = serializers.SerializerMethodField()
    terminal_service_point_history = serializers.SerializerMethodField()

    def get_terminal_id(self, obj):
        return obj.terminal_id

    def get_terminal_code(self, obj):
        return obj.terminal.terminal_code

    def get_service_point_id(self, obj):
        return obj.service_point_id

    def get_service_point_name(self, obj):
        return obj.service_point.service_point_name

    def get_service_point_province_id(self, obj):
        return obj.service_point.province_id

    def get_service_point_province_code(self, obj):
        return obj.service_point.province.province_code

    def get_base_service_point_id(self, obj):
        return obj.service_point.basing_point_id

    def get_base_service_point_name(self, obj):
        return obj.service_point.basing_point.basing_point_name

    def get_base_service_point_province_id(self, obj):
        return obj.service_point.basing_point.province_id

    def get_base_service_point_province_code(self, obj):
        return obj.service_point.basing_point.province.province_code

    def get_updated_on(self, obj):
        terminal_service_point_latest_history_version = TerminalServicePointHistory.objects.filter(
            is_latest_version=True, terminal_service_point=obj).first()
        if terminal_service_point_latest_history_version:
            return terminal_service_point_latest_history_version.updated_on

    def get_terminal_service_point_history(self, obj):
        terminal_service_point_history = TerminalServicePointHistory.objects.filter(
            terminal_service_point=obj)
        return PointsExtraMilesDetailPanelHistorySerializer(terminal_service_point_history, many=True).data

    class Meta:
        model = TerminalServicePoint
        fields = ['terminal_service_point_id', 'terminal_id', 'terminal_code', 'service_point_id', 'service_point_name',
                  'service_point_province_id',
                  'service_point_province_code', 'base_service_point_id', 'base_service_point_name',
                  'base_service_point_province_id', 'base_service_point_province_code',
                  'terminal_service_point_history', 'is_active', 'updated_on']


class PointsExtraMilesDetailPanelHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TerminalServicePointHistory
        fields = ['terminal_service_point_version_id', 'extra_miles',
                  'version_num', 'is_latest_version', 'is_active', 'updated_on']


class LaneCostOriginTerminalSerializer(serializers.ModelSerializer):
    origin_terminal_id = serializers.SerializerMethodField()
    origin_terminal_code = serializers.SerializerMethodField()
    origin_terminal_name = serializers.SerializerMethodField()

    def get_origin_terminal_id(self, obj):
        return obj.lane.origin_terminal_id

    def get_origin_terminal_code(self, obj):
        return obj.lane.origin_terminal.terminal_code

    def get_origin_terminal_name(self, obj):
        return obj.lane.origin_terminal.terminal_name

    class Meta:
        model = LaneCost
        fields = ['lane_cost_id', 'origin_terminal_id',
                  'origin_terminal_code', 'origin_terminal_name']


class LaneCostDestinationTerminalSerializer(serializers.ModelSerializer):
    destination_terminal_id = serializers.SerializerMethodField()
    destination_terminal_code = serializers.SerializerMethodField()
    destination_terminal_name = serializers.SerializerMethodField()

    def get_destination_terminal_id(self, obj):
        return obj.lane.destination_terminal_id

    def get_destination_terminal_code(self, obj):
        return obj.lane.destination_terminal.terminal_code

    def get_destination_terminal_name(self, obj):
        return obj.lane.destination_terminal.terminal_name

    class Meta:
        model = LaneCost
        fields = ['lane_cost_id', 'destination_terminal_id',
                  'destination_terminal_code', 'destination_terminal_name']


class LegCostOriginTerminalSerializer(serializers.ModelSerializer):
    origin_terminal_id = serializers.SerializerMethodField()
    origin_terminal_code = serializers.SerializerMethodField()
    origin_terminal_name = serializers.SerializerMethodField()

    def get_origin_terminal_id(self, obj):
        return obj.lane.origin_terminal_id

    def get_origin_terminal_code(self, obj):
        return obj.lane.origin_terminal.terminal_code

    def get_origin_terminal_name(self, obj):
        return obj.lane.origin_terminal.terminal_name

    class Meta:
        model = LegCost
        fields = ['leg_cost_id', 'origin_terminal_id',
                  'origin_terminal_code', 'origin_terminal_name']


class LegCostDestinationTerminalSerializer(serializers.ModelSerializer):
    destination_terminal_id = serializers.SerializerMethodField()
    destination_terminal_code = serializers.SerializerMethodField()
    destination_terminal_name = serializers.SerializerMethodField()
    service_mode_id = serializers.SerializerMethodField()
    service_mode_code = serializers.SerializerMethodField()
    service_mode_name = serializers.SerializerMethodField()

    def get_destination_terminal_id(self, obj):
        return obj.lane.destination_terminal_id

    def get_destination_terminal_code(self, obj):
        return obj.lane.destination_terminal.terminal_code

    def get_destination_terminal_name(self, obj):
        return obj.lane.destination_terminal.terminal_name

    def get_service_mode_id(self, obj):
        return obj.service_mode_id

    def get_service_mode_code(self, obj):
        return obj.service_mode.service_mode_code

    def get_service_mode_name(self, obj):
        return obj.service_mode.service_mode_name

    class Meta:
        model = LegCost
        fields = ['leg_cost_id', 'destination_terminal_id', 'destination_terminal_code',
                  'destination_terminal_name', 'service_mode_id', 'service_mode_code', 'service_mode_name']


class WeightBreakHeaderDashboardCreateSerializer(serializers.ModelSerializer):
    unit = UnitSerializer()

    def create(self, validated_data):
        unit_data = validated_data.pop("unit")
        unit_instance = Unit.objects.filter(**unit_data).first()
        if not unit_instance:
            unit_instance = Unit.objects.create(**unit_data)
        weight_break_header = WeightBreakHeader.objects.create(
            unit=unit_instance, **validated_data)
        return weight_break_header

    class Meta:
        model = WeightBreakHeader
        fields = "__all__"
        read_only_fields = ['is_active',
                            'is_inactive_viewable', 'weight_break_header_id']


class WeightBreakHeaderDetailPanelSerializer(serializers.ModelSerializer):
    service_level_id = serializers.SerializerMethodField()
    service_level_code = serializers.SerializerMethodField()
    service_level_name = serializers.SerializerMethodField()
    unit_id = serializers.SerializerMethodField()
    unit_name = serializers.SerializerMethodField()
    unit_symbol = serializers.SerializerMethodField()
    unit_type = serializers.SerializerMethodField()
    levels = serializers.SerializerMethodField()
    as_rating = serializers.SerializerMethodField()
    has_min = serializers.SerializerMethodField()
    has_max = serializers.SerializerMethodField()

    def get_service_level_id(self, obj):
        return obj.service_level_id

    def get_service_level_code(self, obj):
        return obj.service_level.service_level_code

    def get_service_level_name(self, obj):
        return obj.service_level.service_level_name

    def get_unit_id(self, obj):
        return obj.unit_id

    def get_unit_name(self, obj):
        return obj.unit.unit_name

    def get_unit_symbol(self, obj):
        return obj.unit.unit_symbol

    def get_unit_type(self, obj):
        return obj.unit.unit_type

    def get_levels(self, obj):
        return json.loads(obj.levels)

    def get_as_rating(self, obj):
        return obj.as_rating

    def get_has_min(self, obj):
        return obj.has_min

    def get_has_max(self, obj):
        return obj.has_max

    class Meta:
        model = WeightBreakHeader
        fields = ['weight_break_header_id', 'weight_break_header_name', 'unit_id', 'unit_name', 'unit_symbol',
                  'unit_type', 'unit_factor',
                  'maximum_value', 'as_rating', 'has_min', 'has_max', 'base_rate', 'levels', 'service_level_id',
                  'service_level_code', 'service_level_name']


class GriReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = GriReview
        fields = "__all__"

    # def create(self, validated_data):
    #     validated_data['created_by'] = self.context.get("created_by")
    #     return GriReview.objects.create(**validated_data)

    # def perform_create(self, serializer):
    #     serializer.save(created_by=self.context.get("created_by"))
    #     print('perform_create')

    def to_internal_value(self, data):
        data['created_by'] = self.context.get("created_by_id")

        return super(GriReviewSerializer, self).to_internal_value(data)
