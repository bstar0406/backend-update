import io
import json
import logging
import pdb
import openpyxl

from django.db import connection, transaction
from django.db.models import Count, Prefetch
from django.http import JsonResponse, HttpResponse
from rest_framework import generics, mixins, status, views, viewsets
from rest_framework.decorators import (action, api_view,
                                       authentication_classes,
                                       permission_classes)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

import pac.pre_costing.queries as queries
from core.authentication import AzureActiveDirectoryAuthentication
from core.permissions import IsAuthorized
from pac.helpers.connections import pyodbc_connection
from pac.helpers.functions import delete_instance
from pac.helpers.mixins import (ArchiveMixin, BatchCreateUpdateMixin,
                                BatchDeleteMixin, BatchUpdateMixin,
                                GetQuerySetMixin, RetrieveHistoryMixin,
                                RevertVersionMixin, UnarchiveMixin)
from pac.models import (City, CityHistory, Country, CountryHistory, Province,
                        ProvinceHistory, Terminal, WeightBreakHeader)
from pac.pre_costing.models import (BrokerContractCost,
                                    CurrencyExchange, DockRoute,
                                    Lane, LaneCost,
                                    LaneRoute,
                                    LegCost, SpeedSheet, TerminalCost,
                                    TerminalServicePoint,
                                    TerminalServicePointHistory, GriReview)
from pac.pre_costing.serializers import (
    BrokerContractCostSerializer,
    BrokerContractDetailPanelSerializer, CityHistorySerializer, CitySerializer,
    CountryHistorySerializer, CountrySerializer, CrossDockRoutesDashboardSeriaizer,
    CrossDockRoutesDetailPanelSerializer, CurrencyExchangeDashboardSerializer,
    CurrencyExchangeSerializer, DockCostsDashboardSerializer,
    DockCostsDetailPanelSerializer,
    DockRouteDashboardCreateSerializer, DockRouteSerializer,
    LaneCostDashboardCreateUpdateSerializer,
    LaneCostDestinationTerminalSerializer, LaneCostOriginTerminalSerializer,
    LaneCostSerializer, LaneRouteDashboardCreateSerializer,
    LaneRouteSerializer, LaneSerializer,
    LegCostDashboardCreateUpdateSerializer,
    LegCostDestinationTerminalSerializer, LegCostOriginTerminalSerializer,
    LegCostSerializer, LinehaulCostsDashboardSerializer,
    LinehaulLaneCostsDashboardSerializer,
    LinehaulLaneCostsDetailPanelSerializer,
    LinehaulLaneRoutesDashboardSerializer,
    LinehaulLaneRoutesDetailPanelSerializer,
    LinehaulLegCostsDashboardSerializer, LinehaulLegCostsDetailPanelSerializer,
    PointsExtraMilesDashboardSerializer, PointsExtraMilesDetailPanelSerializer,
    ProvinceHistorySerializer,
    ProvinceSerializer, SpeedSheetDashboardSerializer,
    SpeedSheetSerializer, TerminalCostSerializer, TerminalSerializer, TerminalServicePointSerializer,
    WeightBreakHeaderDashboardCreateSerializer,
    WeightBreakHeaderDetailPanelSerializer, WeightBreakHeaderSerializer, GriReviewSerializer)


class CountryViewSet(viewsets.ModelViewSet, ArchiveMixin, UnarchiveMixin, GetQuerySetMixin, BatchUpdateMixin,
                     BatchDeleteMixin):
    serializer_class = CountrySerializer
    queryset = Country.objects.all()
    lookup_field = 'country_id'

    def get_queryset(self):
        return GetQuerySetMixin.get_queryset(self)

    def perform_destroy(self, instance):
        delete_instance(instance)

    @action(methods=['patch'], detail=True)
    def archive(self, request, *args, **kwargs):
        return super().archive(request)

    @action(methods=['patch'], detail=True)
    def unarchive(self, request, *args, **kwargs):
        return super().unarchive(request)

    @action(methods=['put'], detail=False, url_path='batch-update')
    def batch_update(self, request, *args, **kwargs):
        return super().batch_update(request, *args, **kwargs)

    @action(methods=['put'], detail=False)
    def batch_delete(self, request, *args, **kwargs):
        return super().batch_delete(request, *args, **kwargs)


class ProvinceViewSet(viewsets.ModelViewSet, ArchiveMixin, UnarchiveMixin, GetQuerySetMixin, BatchUpdateMixin):
    serializer_class = ProvinceSerializer
    queryset = Province.objects.all()
    lookup_field = 'province_id'

    def get_queryset(self):
        return GetQuerySetMixin.get_queryset(self)

    def perform_destroy(self, instance):
        delete_instance(instance)

    @action(methods=['patch'], detail=True)
    def archive(self, request, *args, **kwargs):
        return super().archive(request)

    @action(methods=['patch'], detail=True)
    def unarchive(self, request, *args, **kwargs):
        return super().unarchive(request)

    @action(methods=['put'], detail=False, url_path='batch-update')
    def batch_update(self, request, *args, **kwargs):
        return super().batch_update(request, *args, **kwargs)


class CityViewSet(viewsets.ModelViewSet, ArchiveMixin, UnarchiveMixin, GetQuerySetMixin, BatchUpdateMixin):
    serializer_class = CitySerializer
    queryset = City.objects.all()
    lookup_field = 'city_id'

    def get_queryset(self):
        return GetQuerySetMixin.get_queryset(self)

    def perform_destroy(self, instance):
        delete_instance(instance)

    @action(methods=['patch'], detail=True)
    def archive(self, request, *args, **kwargs):
        return super().archive(request)

    @action(methods=['patch'], detail=True)
    def unarchive(self, request, *args, **kwargs):
        return super().unarchive(request)

    @action(methods=['put'], detail=False, url_path='batch-update')
    def batch_update(self, request, *args, **kwargs):
        return super().batch_update(request, *args, **kwargs)


class TerminalViewSet(viewsets.ModelViewSet, ArchiveMixin, UnarchiveMixin, GetQuerySetMixin, BatchUpdateMixin):
    serializer_class = TerminalSerializer
    queryset = Terminal.objects.all()
    lookup_field = 'terminal_id'

    def get_queryset(self):
        return GetQuerySetMixin.get_queryset(self)

    def perform_destroy(self, instance):
        delete_instance(instance)

    @action(methods=['patch'], detail=True)
    def archive(self, request, *args, **kwargs):
        return super().archive(request)

    @action(methods=['patch'], detail=True)
    def unarchive(self, request, *args, **kwargs):
        return super().unarchive(request)

    @action(methods=['put'], detail=False, url_path='batch-update')
    def batch_update(self, request, *args, **kwargs):
        return super().batch_update(request, *args, **kwargs)


class TerminalCostViewSet(viewsets.ModelViewSet, ArchiveMixin, UnarchiveMixin, GetQuerySetMixin, BatchUpdateMixin):
    serializer_class = TerminalCostSerializer
    queryset = TerminalCost.objects.all()
    lookup_field = 'terminal_cost_id'

    def get_queryset(self):
        return GetQuerySetMixin.get_queryset(self)

    def perform_destroy(self, instance):
        delete_instance(instance)

    @action(methods=['patch'], detail=True)
    def archive(self, request, *args, **kwargs):
        return super().archive(request)

    @action(methods=['patch'], detail=True)
    def unarchive(self, request, *args, **kwargs):
        return super().unarchive(request)

    @action(methods=['put'], detail=False, url_path='batch-update')
    def batch_update(self, request, *args, **kwargs):
        return super().batch_update(request, *args, **kwargs)


class DockRouteViewSet(viewsets.ModelViewSet, ArchiveMixin, UnarchiveMixin, GetQuerySetMixin, BatchUpdateMixin):
    serializer_class = DockRouteSerializer
    queryset = DockRoute.objects.all()
    lookup_field = 'dock_route_id'

    def get_queryset(self):
        return GetQuerySetMixin.get_queryset(self)

    def get_serializer_class(self):
        action_serializers = {"create": DockRouteDashboardCreateSerializer}
        if self.action in action_serializers:
            return action_serializers[self.action]
        return super().get_serializer_class()

    def perform_destroy(self, instance):
        delete_instance(instance)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        instance = self.get_queryset().filter(
            **{self.lookup_field: response.data[self.lookup_field]}).first()
        serializer = CrossDockRoutesDashboardSeriaizer(instance)
        response.data = serializer.data
        return response

    @action(methods=['patch'], detail=True)
    def archive(self, request, *args, **kwargs):
        return super().archive(request)

    @action(methods=['patch'], detail=True)
    def unarchive(self, request, *args, **kwargs):
        return super().unarchive(request)

    @action(methods=['put'], detail=False, url_path='batch-update')
    def batch_update(self, request, *args, **kwargs):
        return super().batch_update(request, *args, **kwargs)


class LaneRouteViewSet(viewsets.ModelViewSet, ArchiveMixin, UnarchiveMixin, GetQuerySetMixin, BatchUpdateMixin):
    serializer_class = LaneRouteSerializer
    queryset = LaneRoute.objects.all()
    lookup_field = 'lane_route_id'

    def get_queryset(self):
        return GetQuerySetMixin.get_queryset(self)

    def get_serializer_class(self):
        action_serializers = {"create": LaneRouteDashboardCreateSerializer}
        if self.action in action_serializers:
            return action_serializers[self.action]
        return super().get_serializer_class()

    def perform_destroy(self, instance):
        delete_instance(instance)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        instance = self.get_queryset().filter(
            **{self.lookup_field: response.data[self.lookup_field]}).first()
        serializer = LinehaulLaneRoutesDashboardSerializer(instance)
        response.data = serializer.data
        return response

    @action(methods=['patch'], detail=True)
    def archive(self, request, *args, **kwargs):
        return super().archive(request)

    @action(methods=['patch'], detail=True)
    def unarchive(self, request, *args, **kwargs):
        return super().unarchive(request)

    @action(methods=['put'], detail=False, url_path='batch-update')
    def batch_update(self, request, *args, **kwargs):
        return super().batch_update(request, *args, **kwargs)


class LaneCostViewSet(viewsets.ModelViewSet, ArchiveMixin, UnarchiveMixin, GetQuerySetMixin, BatchUpdateMixin):
    serializer_class = LaneCostSerializer
    queryset = LaneCost.objects.all()
    lookup_field = 'lane_cost_id'

    def get_queryset(self):
        return GetQuerySetMixin.get_queryset(self)

    def perform_destroy(self, instance):
        delete_instance(instance)

    @action(methods=['patch'], detail=True)
    def archive(self, request, *args, **kwargs):
        return super().archive(request)

    @action(methods=['patch'], detail=True)
    def unarchive(self, request, *args, **kwargs):
        return super().unarchive(request)

    @action(methods=['put'], detail=False, url_path='batch-update')
    def batch_update(self, request, *args, **kwargs):
        return super().batch_update(request, *args, **kwargs)


class LegCostViewSet(viewsets.ModelViewSet, ArchiveMixin, UnarchiveMixin, GetQuerySetMixin, BatchUpdateMixin):
    serializer_class = LegCostSerializer
    queryset = LegCost.objects.all()
    lookup_field = 'leg_cost_id'

    def get_queryset(self):
        return GetQuerySetMixin.get_queryset(self)

    def perform_destroy(self, instance):
        delete_instance(instance)

    @action(methods=['patch'], detail=True)
    def archive(self, request, *args, **kwargs):
        return super().archive(request)

    @action(methods=['patch'], detail=True)
    def unarchive(self, request, *args, **kwargs):
        return super().unarchive(request)

    @action(methods=['put'], detail=False, url_path='batch-update')
    def batch_update(self, request, *args, **kwargs):
        return super().batch_update(request, *args, **kwargs)


class BrokerContractCostViewSet(viewsets.ModelViewSet, ArchiveMixin, UnarchiveMixin, GetQuerySetMixin,
                                BatchUpdateMixin):
    serializer_class = BrokerContractCostSerializer
    queryset = BrokerContractCost.objects.all()
    lookup_field = 'broker_contract_cost_id'

    def get_queryset(self):
        return GetQuerySetMixin.get_queryset(self)

    def perform_destroy(self, instance):
        delete_instance(instance)

    @action(methods=['patch'], detail=True)
    def archive(self, request, *args, **kwargs):
        return super().archive(request)

    @action(methods=['patch'], detail=True)
    def unarchive(self, request, *args, **kwargs):
        return super().unarchive(request)

    @action(methods=['put'], detail=False, url_path='batch-update')
    def batch_update(self, request, *args, **kwargs):
        return super().batch_update(request, *args, **kwargs)
        

class TerminalServicePointViewSet(viewsets.GenericViewSet, mixins.UpdateModelMixin, BatchUpdateMixin):
    serializer_class = TerminalServicePointSerializer
    queryset = TerminalServicePoint.objects.all()
    lookup_field = 'terminal_service_point_id'

    def get_queryset(self):
        return GetQuerySetMixin.get_queryset(self)

    @action(methods=['put'], detail=False, url_path='batch-update')
    def batch_update(self, request, *args, **kwargs):
        return super().batch_update(request, *args, **kwargs)


class SpeedSheetViewSet(viewsets.GenericViewSet, mixins.UpdateModelMixin, BatchUpdateMixin):
    serializer_class = SpeedSheetSerializer
    queryset = SpeedSheet.objects.all()
    lookup_field = 'speed_sheet_id'

    def get_queryset(self):
        return GetQuerySetMixin.get_queryset(self)

    @action(methods=['put'], detail=False, url_path='batch-update')
    def batch_update(self, request, *args, **kwargs):
        return super().batch_update(request, *args, **kwargs)


class WeightBreakHeaderViewSet(viewsets.GenericViewSet, mixins.UpdateModelMixin, mixins.CreateModelMixin,
                               BatchUpdateMixin, BatchCreateUpdateMixin):
    serializer_class = WeightBreakHeaderSerializer
    queryset = WeightBreakHeader.objects.all()
    lookup_field = 'weight_break_header_id'

    def get_queryset(self):
        return GetQuerySetMixin.get_queryset(self)

    def get_serializer_class(self):
        action_serializers = {
            "create": WeightBreakHeaderDashboardCreateSerializer}
        if self.action in action_serializers:
            return action_serializers[self.action]
        return super().get_serializer_class()

    @action(methods=['put'], detail=False, url_path='batch-update')
    def batch_update(self, request, *args, **kwargs):
        return super().batch_update(request, *args, **kwargs)

    @action(methods=['post'], detail=False, url_path='batch-create-update')
    def batch_create_update(self, request, *args, **kwargs):
        return super().batch_create_update(request, *args, **kwargs)


class CountryHistoryRetrieveViewSet(RetrieveHistoryMixin, viewsets.GenericViewSet):
    serializer_class = CountryHistorySerializer
    queryset = CountryHistory.objects.all()
    lookup_field = 'country_id'

    def get(self, request, *args, **kwargs):
        return self.retrieve_history(request, *args, **kwargs)


class CityHistoryRetrieveViewSet(RetrieveHistoryMixin, viewsets.GenericViewSet):
    serializer_class = CityHistorySerializer
    queryset = CityHistory.objects.all()
    lookup_field = 'city_id'

    def get(self, request, *args, **kwargs):
        return self.retrieve_history(request, *args, **kwargs)


class ProvinceHistoryRetrieveViewSet(RetrieveHistoryMixin, viewsets.GenericViewSet):
    serializer_class = ProvinceHistorySerializer
    queryset = ProvinceHistory.objects.all()
    lookup_field = 'province_id'

    def get(self, request, *args, **kwargs):
        return self.retrieve_history(request, *args, **kwargs)


class CountryRevertVersionView(generics.GenericAPIView, RevertVersionMixin, generics.mixins.CreateModelMixin):
    serializer_class = CountrySerializer
    queryset = Country.objects.filter(is_active=True)
    lookup_field = 'country_id'

    def patch(self, request, *args, **kwargs):
        return self.revert_version(request, CountryHistory, *args, **kwargs)


class CityRevertVersionView(generics.GenericAPIView, RevertVersionMixin):
    serializer_class = CitySerializer
    queryset = City.objects.filter(is_active=True)
    lookup_field = 'city_id'

    def patch(self, request, city_id=None, version_num=None, *args, **kwargs):
        return self.revert_version(request, CityHistory, *args, **kwargs)


class ProvinceRevertVersionView(generics.GenericAPIView, RevertVersionMixin):
    serializer_class = ProvinceSerializer
    queryset = Province.objects.filter(is_active=True)
    lookup_field = 'province_id'

    def patch(self, request, *args, **kwargs):
        return self.revert_version(request, ProvinceHistory, *args, **kwargs)


class DockCostsDashboardView(generics.ListAPIView):
    serializer_class = DockCostsDashboardSerializer
    queryset = TerminalCost.objects.filter(is_inactive_viewable=True)
    lookup_field = "service_offering_id"

    def get_queryset(self):
        return self.queryset.filter(**{self.lookup_field: self.kwargs[self.lookup_field]})


class DockCostsDetailPanelView(generics.RetrieveAPIView):
    serializer_class = DockCostsDetailPanelSerializer
    queryset = TerminalCost.objects.filter(is_inactive_viewable=True)
    lookup_field = "terminal_cost_id"

    def get_queryset(self):
        return self.queryset.filter(**{self.lookup_field: self.kwargs[self.lookup_field]})


class CrossDockRoutesDashboardView(generics.ListAPIView):
    serializer_class = CrossDockRoutesDashboardSeriaizer
    queryset = DockRoute.objects.filter(is_inactive_viewable=True)
    lookup_field = "service_offering_id"

    def get_queryset(self):
        queryset = self.queryset.filter(
            service_level__service_offering_id=self.kwargs[self.lookup_field]).select_related(
            'lane', 'lane__origin_terminal', 'lane__origin_terminal__city__province', 'lane__origin_terminal__region',
            'lane__destination_terminal', 'lane__destination_terminal__city__province',
            'lane__destination_terminal__region', 'service_level')
        return queryset


class CrossDockRoutesDetailPanelView(generics.RetrieveAPIView):
    serializer_class = CrossDockRoutesDetailPanelSerializer
    queryset = DockRoute.objects.filter(is_inactive_viewable=True)
    lookup_field = "dock_route_id"


class LinehaulLaneRoutesDashboardView(generics.ListAPIView):
    serializer_class = LinehaulLaneRoutesDashboardSerializer
    queryset = LaneRoute.objects.filter(is_inactive_viewable=True)
    lookup_field = "service_offering_id"

    def get_queryset(self):
        queryset = self.queryset.filter(
            lane__sub_service_level__service_level__service_offering_id=self.kwargs[self.lookup_field])
        return queryset


class LinehaulLaneRoutesDetailPanelView(generics.RetrieveAPIView):
    serializer_class = LinehaulLaneRoutesDetailPanelSerializer
    queryset = LaneRoute.objects.filter(is_inactive_viewable=True)
    lookup_field = "lane_route_id"


class TerminalServicePointDashboardPyodbcView(views.APIView):

    def get(self, request, *args, **kwargs):
        cnxn = pyodbc_connection()
        cursor = cnxn.cursor()
        query = queries.TERMINAL_SERVICE_POINT_DASHBOARD

        cursor.execute(query)
        raw_data = cursor.fetchone()
        payload = json.loads(raw_data[0]) if raw_data[0] else []

        return Response(payload, status=status.HTTP_200_OK)


class LegsForRoutesPyodbcView(views.APIView):

    def get(self, request, *args, **kwargs):
        origin_terminal_id = kwargs.get("origin_terminal_id")
        service_level_id = kwargs.get("service_level_id")
        cnxn = pyodbc_connection()
        cursor = cnxn.cursor()
        query = queries.LEGS_FOR_ROUTES.format(
            origin_terminal_id, service_level_id)

        cursor.execute(query)
        raw_data = cursor.fetchone()
        payload = json.loads(raw_data[0]) if raw_data[0] else []

        return Response(payload, status=status.HTTP_200_OK)


class LaneDestinationTerminalsPyodbcView(views.APIView):

    def get(self, request, *args, **kwargs):
        service_offering_id = kwargs.get("service_level_id")
        origin_terminal_id = kwargs.get("origin_terminal_id")
        cnxn = pyodbc_connection()
        cursor = cnxn.cursor()
        query = queries.LANES_DESTINATION_TERMINALS.format(
            service_offering_id, origin_terminal_id)

        cursor.execute(query)
        raw_data = cursor.fetchone()
        payload = json.loads(raw_data[0]) if raw_data[0] else []

        return Response(payload, status=status.HTTP_200_OK)


class LinehaulLegCostsDashboardView(generics.ListAPIView):
    serializer_class = LinehaulLegCostsDashboardSerializer
    queryset = LegCost.objects.filter(is_inactive_viewable=True)
    lookup_field = "service_offering_id"

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = self.queryset.filter(
            lane__sub_service_level__service_level__service_offering_id=self.kwargs[self.lookup_field]).select_related('lane',
                                                                                                    'lane__origin_terminal',
                                                                                                    'lane__destination_terminal',
                                                                                                    'lane__origin_terminal__city__province',
                                                                                                    'lane__destination_terminal__city__province',
                                                                                                    'lane__origin_terminal__region',
                                                                                                    'lane__destination_terminal__region',
                                                                                                    'service_level')
        return queryset


class LinehaulLaneCostsDetailPanelView(generics.RetrieveAPIView):
    serializer_class = LinehaulLaneCostsDetailPanelSerializer
    queryset = LaneCost.objects.filter(is_inactive_viewable=True)
    lookup_field = "lane_cost_id"


class LinehaulLegCostsDetailPanelView(generics.RetrieveAPIView):
    serializer_class = LinehaulLegCostsDetailPanelSerializer
    queryset = LegCost.objects.filter(is_inactive_viewable=True)
    lookup_field = "leg_cost_id"

class BrokerContractDetailPanelView(generics.RetrieveAPIView):
    serializer_class = BrokerContractDetailPanelSerializer
    queryset = BrokerContractCost.objects.filter(
        is_inactive_viewable=True).select_related('terminal', 'service_level')
    lookup_field = "broker_contract_cost_id"


class CurrencyExchangeDashboardView(views.APIView):

    def get(self, request, *args, **kwargs):
        currency_exchange = CurrencyExchange.objects.filter(
            is_inactive_viewable=True).first()
        if currency_exchange:
            return Response(CurrencyExchangeDashboardSerializer(currency_exchange).data, status=status.HTTP_200_OK)
        return Response({"status": "Unsuccesful"}, status=status.HTTP_400_BAD_REQUEST)


class SpeedSheetDashboardView(generics.RetrieveAPIView):
    serializer_class = SpeedSheetDashboardSerializer
    queryset = SpeedSheet.objects.filter(is_inactive_viewable=True)
    lookup_field = "service_offering_id"


class PointsExtraMilesDashboardView(generics.ListAPIView):
    serializer_class = PointsExtraMilesDashboardSerializer
    queryset = TerminalServicePoint.objects.filter(is_inactive_viewable=True).select_related('terminal',
                                                                                             'service_point',
                                                                                             'service_point__province',
                                                                                             'base_service_point',
                                                                                             'base_service_point__province').prefetch_related(
        Prefetch('terminalservicepointhistory_set',
                 queryset=TerminalServicePointHistory.objects.filter(is_latest_version=True)))


class PointsExtraMilesDetailPanelView(generics.RetrieveAPIView):
    serializer_class = PointsExtraMilesDetailPanelSerializer
    queryset = TerminalServicePoint.objects.filter(is_inactive_viewable=True).select_related(
        'terminal', 'service_point', 'service_point__province', 'service_point__basing_point__province')
    lookup_field = "terminal_service_point_id"


class CrossDockRoutesDashboardPyodbcView(views.APIView):

    def get(self, request, *args, **kwargs):
        service_offering_id = kwargs.get("service_offering_id")
        cnxn = pyodbc_connection()
        cursor = cnxn.cursor()
        query = queries.DOCK_ROUTES_DASHBOARD.format(service_offering_id)

        cursor.execute(query)
        raw_data = cursor.fetchone()
        payload = json.loads(raw_data[0]) if raw_data[0] else []

        return Response(payload, status=status.HTTP_200_OK)


class LinehaulLaneRoutesDashboardPyodbcView(views.APIView):

    def get(self, request, *args, **kwargs):
        service_offering_id = kwargs.get("service_offering_id")
        cnxn = pyodbc_connection()
        cursor = cnxn.cursor()
        query = queries.LANE_ROUTES_DASHBOARD.format(service_offering_id)

        cursor.execute(query)
        raw_data = cursor.fetchone()
        payload = json.loads(raw_data[0]) if raw_data[0] else []

        return Response(payload, status=status.HTTP_200_OK)


class LinehaulLaneLegCostBatchCreateUpdateView(views.APIView):

    def post(self, request, *args, **kwargs):
        leg_costs = request.data.get("leg_costs", [])
        for leg_cost in leg_costs:
            if leg_cost.get("leg_cost_id"):
                leg_cost_instance = LegCost.objects.filter(
                    leg_cost_id=leg_cost["leg_cost_id"]).first()
                if "lane" in leg_cost and isinstance(leg_cost["lane"], dict):
                    serializer = LegCostDashboardCreateUpdateSerializer(
                        leg_cost_instance, data=leg_cost, partial=True)
                else:
                    serializer = LegCostSerializer(
                        leg_cost_instance, data=leg_cost, partial=True)
            else:
                if "lane" in leg_cost and isinstance(leg_cost["lane"], dict):
                    serializer = LegCostDashboardCreateUpdateSerializer(
                        data=leg_cost)
                else:
                    serializer = LegCostSerializer(data=leg_cost)
            serializer.is_valid(raise_exception=True)
            serializer.save()

        lane_costs = request.data.get("lane_costs", [])
        for lane_cost in lane_costs:
            if lane_cost.get("lane_cost_id"):
                lane_cost_instance = LaneCost.objects.filter(
                    lane_cost_id=lane_cost["lane_cost_id"]).first()
                if "lane" in lane_cost and isinstance(lane_cost["lane"], dict):
                    serializer = LaneCostDashboardCreateUpdateSerializer(
                        lane_cost_instance, data=lane_cost, partial=True)
                else:
                    serializer = LaneCostSerializer(
                        lane_cost_instance, data=lane_cost, partial=True)
            else:
                if "lane" in lane_cost and isinstance(lane_cost["lane"], dict):
                    serializer = LaneCostDashboardCreateUpdateSerializer(
                        data=lane_cost)
                else:
                    serializer = LaneCostSerializer(data=lane_cost)
            serializer.is_valid(raise_exception=True)
            serializer.save()

        lanes = request.data.get("lanes", [])
        for lane in lanes:
            lane_instance = Lane.objects.filter(
                lane_id=lane["lane_id"]).first()
            serializer = LaneSerializer(lane_instance, data=lane, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

        if not lane_costs and not leg_costs and not lanes:
            return Response({"status": "Unsuccesful"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"status": "Success"}, status=status.HTTP_200_OK)


@api_view(["POST"])
def post_dockroute_pyodbc(request):
    data = request.data
    origin_terminal_id = data["origin_terminal_id"]
    destination_terminal_id = data["destination_terminal_id"]
    service_level_id = data["service_level_id"]
    route_legs = data["route_legs"]

    cnxn = pyodbc_connection()
    cursor = cnxn.cursor()

    cursor.execute("EXEC [dbo].[DockRoute_Insert] ?, ?, ?, ?", origin_terminal_id,
                   destination_terminal_id, service_level_id, route_legs)
    cursor.commit()

    return Response({"status": "Success"}, status=status.HTTP_200_OK)


@api_view(["POST"])
def post_lane_cost_weight_break_level_pyodbc(request):
    try:
        data = request.data
        to_be_added = data["to_be_added"]
        to_be_updated = data["to_be_updated"]
        service_offering_id = data["service_offering_id"]

        to_be_added_param_array = []
        to_be_updated_param_array = []

        cnxn = pyodbc_connection()

        if to_be_added:
            for row in to_be_added:
                weight_break_level_name = row["level_name"]
                weight_break_lower_bound = row["lower_bound"]
                to_be_added_param_array.append(
                    [service_offering_id, weight_break_level_name, weight_break_lower_bound])

            if len(to_be_added_param_array) > 0:
                cnxn.execute("EXEC [dbo].[LaneCostWeightBreakLevel_Create] ?,?",
                             to_be_added_param_array, service_offering_id)
                cnxn.commit()

        if to_be_updated:
            for row in to_be_updated:
                weight_break_level_id = row["id"]
                weight_break_level_name = row["level_name"]
                weight_break_lower_bound = row["lower_bound"]
                is_active = row["is_active"]
                to_be_updated_param_array.append(
                    [weight_break_level_id, weight_break_level_name, weight_break_lower_bound, is_active])

            if len(to_be_updated_param_array) > 0:
                cnxn.execute("EXEC [dbo].[LaneCostWeightBreakLevel_Update] ?,?",
                             to_be_updated_param_array, service_offering_id)
                cnxn.commit()

        return Response({"status": "Success"}, status=status.HTTP_200_OK)
    except Exception as e:
        logging.warning("{} {}".format(type(e).__name__, e.args))
        return Response({"status": "Failure", "error": "{} {}".format(type(e).__name__, e.args)},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
def post_terminal_cost_weight_break_level_pyodbc(request):
    try:
        data = request.data
        to_be_added = data["to_be_added"]
        to_be_updated = data["to_be_updated"]
        service_offering_id = data["service_offering_id"]

        to_be_added_param_array = []
        to_be_updated_param_array = []

        cnxn = pyodbc_connection()

        if to_be_added:
            for row in to_be_added:
                weight_break_level_name = row["level_name"]
                weight_break_lower_bound = row["lower_bound"]
                to_be_added_param_array.append(
                    [service_offering_id, weight_break_level_name, weight_break_lower_bound])

            if len(to_be_added_param_array) > 0:
                cnxn.execute("EXEC [dbo].[TerminalCostWeightBreakLevel_Create] ?,?",
                             to_be_added_param_array, service_offering_id)
                cnxn.commit()

        if to_be_updated:
            for row in to_be_updated:
                weight_break_level_id = row["id"]
                weight_break_level_name = row["level_name"]
                weight_break_lower_bound = row["lower_bound"]
                is_active = row["is_active"]
                to_be_updated_param_array.append(
                    [weight_break_level_id, weight_break_level_name, weight_break_lower_bound, is_active])

            if len(to_be_updated_param_array) > 0:
                cnxn.execute("EXEC [dbo].[TerminalCostWeightBreakLevel_Update] ?,?",
                             to_be_updated_param_array, service_offering_id)
                cnxn.commit()

        return Response({"status": "Success"}, status=status.HTTP_200_OK)
    except Exception as e:
        logging.warning("{} {}".format(type(e).__name__, e.args))
        return Response({"status": "Failure", "error": "{} {}".format(type(e).__name__, e.args)},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class post_broker_contract_cost_weight_break_level_pyodbc(views.APIView):

    def post(self, request, *args, **kwargs):
        try:
            terminal_id = kwargs.get("terminal_id")
            service_level_id = kwargs.get("service_level_id")

            data = request.data
            to_be_added = data["to_be_added"]
            to_be_updated = data["to_be_updated"]
            to_be_deleted = data["to_be_deleted"]

            to_be_added_param_array = []
            to_be_updated_param_array = []
            to_be_deleted_param_array = []

            cnxn = pyodbc_connection()

            if to_be_added:
                for row in to_be_added:
                    weight_break_level_name = row["level_name"]
                    weight_break_lower_bound = row["lower_bound"]
                    to_be_added_param_array.append(
                        [weight_break_level_name, weight_break_lower_bound])

                if len(to_be_added_param_array) > 0:
                    cnxn.execute("EXEC [dbo].[BrokerContractCost_Create] ?, ?, ?",
                                 to_be_added_param_array, terminal_id, service_level_id)
                    cnxn.commit()

            if to_be_updated:
                for row in to_be_updated:
                    weight_break_level_name = row["level_name"]
                    weight_break_lower_bound = row["lower_bound"]
                    to_be_updated_param_array.append(
                        [weight_break_level_name, weight_break_lower_bound])

                if len(to_be_updated_param_array) > 0:
                    cnxn.execute("EXEC [dbo].[BrokerContractCost_Update] ?, ?, ?",
                                 to_be_updated_param_array, terminal_id, service_level_id)
                    cnxn.commit()

            if to_be_deleted:
                for row in to_be_deleted:
                    weight_break_level_name = row["level_name"]
                    weight_break_lower_bound = row["lower_bound"]
                    to_be_deleted_param_array.append(
                        [weight_break_level_name, weight_break_lower_bound])

                if len(to_be_deleted_param_array) > 0:
                    cnxn.execute("EXEC [dbo].[BrokerContractCost_Delete] ?, ?, ?",
                                 to_be_deleted_param_array, terminal_id, service_level_id)
                    cnxn.commit()

            return Response({"status": "Success"}, status=status.HTTP_200_OK)
        except Exception as e:
            logging.warning("{} {}".format(type(e).__name__, e.args))
            return Response({"status": "Failure", "error": "{} {}".format(type(e).__name__, e.args)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class account_search_by_name_pyodbc(views.APIView):

    def get(self, request, *args, **kwargs):
        account_name = kwargs.get("account_name")
        service_level_id = kwargs.get("service_level_id")
        cnxn = pyodbc_connection()
        cursor = cnxn.cursor()
        query = queries.ACCOUNT_SEARCH_BY_NAME.format(
            service_level_id, account_name)

        cursor.execute(query)
        raw_data = cursor.fetchone()
        payload = json.loads(raw_data[0]) if raw_data[0] else []

        return Response(payload, status=status.HTTP_200_OK)


class city_search_by_name_pyodbc(views.APIView):

    def get(self, request, *args, **kwargs):
        city_name = kwargs.get("city_name")
        province_id = kwargs.get("province_id")
        cnxn = pyodbc_connection()
        cursor = cnxn.cursor()
        query = queries.CITY_SEARCH_BY_NAME.format(province_id, city_name)

        cursor.execute(query)
        raw_data = cursor.fetchone()
        payload = json.loads(raw_data[0]) if raw_data[0] else []

        return Response(payload, status=status.HTTP_200_OK)


class service_point_search_by_name_pyodbc(views.APIView):

    def get(self, request, *args, **kwargs):
        service_offering_id = kwargs.get("service_offering_id")
        service_point_name = kwargs.get("service_point_name")
        cnxn = pyodbc_connection()
        cursor = cnxn.cursor()
        query = queries.SERVICE_POINT_SEARCH_BY_NAME.format(
            service_offering_id, service_point_name)

        cursor.execute(query)
        raw_data = cursor.fetchone()
        payload = json.loads(raw_data[0]) if raw_data[0] else []

        return Response(payload, status=status.HTTP_200_OK)

@api_view(['POST'])
@authentication_classes([AzureActiveDirectoryAuthentication])
@permission_classes([IsAuthenticated, IsAuthorized])
def authentication_demo(request):
    return Response("This user is authenticated and has permissions to access this endpoint.")


class DockCostsBatchUpdateView(views.APIView):

    def put(self, request, *args, **kwargs):
        try:
            terminals = request.data.get("terminals", [])
            for terminal in terminals:
                terminal_id = terminal.get("terminal_id")
                if not terminal_id:
                    return Response(f"Terminal missing primary key: terminal_id", status=status.HTTP_400_BAD_REQUEST)
                instance = Terminal.objects.filter(
                    terminal_id=terminal_id).first()
                if not instance:
                    return Response(f"Terminal object with primary key '{terminal_id}' does not exist",
                                    status=status.HTTP_400_BAD_REQUEST)
                serializer = TerminalSerializer(
                    instance, data=terminal, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()

            terminal_costs = request.data.get("terminal_costs", [])
            for terminal_cost in terminal_costs:
                terminal_cost_id = terminal_cost.get("terminal_cost_id")
                if not terminal_cost_id:
                    return Response(f"TerminalCost missing primary key: terminal_cost_id",
                                    status=status.HTTP_400_BAD_REQUEST)
                instance = TerminalCost.objects.filter(
                    terminal_cost_id=terminal_cost_id).first()
                if not instance:
                    return Response(f"TerminalCost object with primary key '{terminal_cost_id}' does not exist",
                                    status=status.HTTP_400_BAD_REQUEST)
                serializer = TerminalCostSerializer(
                    instance, data=terminal_cost, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()

            if not terminals and not terminal_costs:
                return Response({"status": "Unsuccesful"}, status=status.HTTP_400_BAD_REQUEST)

            return Response({"status": "Success"}, status=status.HTTP_200_OK)
        except Exception as e:
            logging.warning("{} {}".format(type(e).__name__, e.args))
            return Response({"status": "Failure", "error": "{} {}".format(type(e).__name__, e.args)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LaneCostsBatchUpdateView(views.APIView):

    def put(self, request, *args, **kwargs):
        try:
            lanes = request.data.get("lanes", [])
            for lane in lanes:
                lane_id = lane.get("lane_id")
                if not lane_id:
                    return Response(f"Lane missing primary key: lane_id", status=status.HTTP_400_BAD_REQUEST)
                instance = Lane.objects.filter(lane_id=lane_id).first()
                if not instance:
                    return Response(f"Lane object with primary key '{lane_id}' does not exist",
                                    status=status.HTTP_400_BAD_REQUEST)
                serializer = LaneSerializer(
                    instance, data=lane, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()

            lane_costs = request.data.get("lane_costs", [])
            for lane_cost in lane_costs:
                lane_cost_id = lane_cost.get("lane_cost_id")
                if not lane_cost_id:
                    return Response(f"LaneCost missing primary key: lane_cost_id", status=status.HTTP_400_BAD_REQUEST)
                instance = LaneCost.objects.filter(
                    lane_cost_id=lane_cost_id).first()
                if not instance:
                    return Response(f"LaneCost object with primary key '{lane_cost_id}' does not exist",
                                    status=status.HTTP_400_BAD_REQUEST)
                serializer = LaneCostSerializer(
                    instance, data=lane_cost, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()

            if not lanes and not lane_costs:
                return Response({"status": "Unsuccesful"}, status=status.HTTP_400_BAD_REQUEST)

            return Response({"status": "Success"}, status=status.HTTP_200_OK)
        except Exception as e:
            logging.warning("{} {}".format(type(e).__name__, e.args))
            return Response({"status": "Failure", "error": "{} {}".format(type(e).__name__, e.args)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LaneRoutesBatchCreateUpdateView(views.APIView):

    @transaction.atomic
    def put(self, request, *args, **kwargs):
        lanes = request.data.get("lanes", [])
        for lane in lanes:
            lane_id = lane.get("lane_id")
            if not lane_id:
                serializer = LaneSerializer(data=lane)
            else:
                instance = Lane.objects.filter(lane_id=lane_id).first()
                if not instance:
                    return Response(f"Lane object with primary key '{lane_id}' does not exist",
                                    status=status.HTTP_400_BAD_REQUEST)
                serializer = LaneSerializer(
                    instance, data=lane, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

        lane_routes = request.data.get("lane_routes", [])
        for lane_route in lane_routes:
            lane_route_id = lane_route.get("lane_route_id")
            if not lane_route_id:
                serializer = LaneRouteSerializer(data=lane_route)
            else:
                instance = LaneRoute.objects.filter(
                    lane_route_id=lane_route_id).first()
                if not instance:
                    return Response(f"LaneRoute object with primary key '{lane_route_id}' does not exist",
                                    status=status.HTTP_400_BAD_REQUEST)
                serializer = LaneRouteSerializer(
                    instance, data=lane_route, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

        if not lanes and not lane_routes:
            return Response({"status": "Unsuccesful"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"status": "Success"}, status=status.HTTP_200_OK)


class DockRoutesBatchUpdateView(views.APIView):

    def put(self, request, *args, **kwargs):
        lanes = request.data.get("lanes", [])
        for lane in lanes:
            lane_id = lane.get("lane_id")
            if not lane_id:
                return Response(f"Lane missing primary key: lane_id", status=status.HTTP_400_BAD_REQUEST)
            instance = Lane.objects.filter(lane_id=lane_id).first()
            if not instance:
                return Response(f"Lane object with primary key '{lane_id}' does not exist",
                                status=status.HTTP_400_BAD_REQUEST)
            serializer = LaneSerializer(
                instance, data=lane, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

        dock_routes = request.data.get("dock_routes", [])
        for dock_route in dock_routes:
            dock_route_id = dock_route.get("dock_route_id")
            if not dock_route_id:
                return Response(f"DockRoute missing primary key: dock_route_id", status=status.HTTP_400_BAD_REQUEST)
            instance = DockRoute.objects.filter(
                dock_route_id=dock_route_id).first()
            if not instance:
                return Response(f"DockRoute object with primary key '{dock_route_id}' does not exist",
                                status=status.HTTP_400_BAD_REQUEST)
            serializer = DockRouteSerializer(
                instance, data=dock_route, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

        if not lanes and not dock_routes:
            return Response({"status": "Unsuccesful"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"status": "Success"}, status=status.HTTP_200_OK)


class LaneCostOriginTerminalView(generics.ListAPIView):
    serializer_class = LaneCostOriginTerminalSerializer
    lookup_field = "service_level_id"
    queryset = LaneCost.objects.filter(is_inactive_viewable=True)

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(lane__sub_service_level__service_level__service_level_id=self.kwargs['service_level_id']).select_related(
            'lane__origin_terminal')


class LaneCostDestinationTerminalView(generics.ListAPIView):
    serializer_class = LaneCostDestinationTerminalSerializer
    queryset = LaneCost.objects.filter(is_inactive_viewable=True)

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(lane__sub_service_level__service_level__service_level_id=self.kwargs['service_level_id'],
                               lane__origin_terminal_id=self.kwargs['origin_terminal_id']).select_related(
            'lane__destination_terminal')


class LegCostOriginTerminalView(generics.ListAPIView):
    serializer_class = LegCostOriginTerminalSerializer
    lookup_field = "service_level_id"
    queryset = LegCost.objects.filter(is_inactive_viewable=True)

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(lane__sub_service_level__service_level__service_level_id=self.kwargs['service_level_id']).select_related(
            'lane__origin_terminal')


class LegCostDestinationTerminalView(generics.ListAPIView):
    serializer_class = LegCostDestinationTerminalSerializer
    queryset = LegCost.objects.filter(is_inactive_viewable=True)

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(lane__sub_service_level__service_level__service_level_id=self.kwargs['service_level_id'],
                               lane__origin_terminal_id=self.kwargs['origin_terminal_id']).select_related(
            'lane__destination_terminal', 'service_mode')


class WeightBreakHeaderDetailPanelView(generics.RetrieveAPIView):
    serializer_class = WeightBreakHeaderDetailPanelSerializer
    queryset = WeightBreakHeader.objects.filter(
        is_inactive_viewable=True).select_related('service_level', 'unit')
    lookup_field = "weight_break_header_id"


class WeightBreakHeadersDashboardPyodbcView(views.APIView):

    def get(self, request, *args, **kwargs):
        service_offering_id = kwargs.get("service_offering_id")
        cnxn = pyodbc_connection()
        cursor = cnxn.cursor()
        query = queries.WEIGHT_BREAK_HEADERS_DASHBOARD.format(
            service_offering_id)

        cursor.execute(query)
        raw_data = cursor.fetchone()
        payload = json.loads(raw_data[0]) if raw_data[0] else []

        return Response(payload, status=status.HTTP_200_OK)


class WeightBreakHeadersLevelPyodbcView(views.APIView):

    def get(self, request, *args, **kwargs):
        service_level_id = kwargs.get("service_level_id")
        cnxn = pyodbc_connection()
        cursor = cnxn.cursor()
        query = queries.WEIGHT_BREAK_HEADERS_LEVEL.format(
            service_level_id)

        cursor.execute(query)
        raw_data = cursor.fetchone()
        payload = json.loads(raw_data[0]) if raw_data[0] else []

        return Response(payload, status=status.HTTP_200_OK)


class GriReviewView(views.APIView):
    def get(self, request, *args, **kwargs):
        user_id = self.request.user.user_id
        gri_review_id = kwargs.get("gri_review_id")

        try:
            if gri_review_id is not None:
                gri_review = GriReview.objects.filter(gri_review_id=gri_review_id).first()
                serializer = GriReviewSerializer(gri_review, many=False)
                return JsonResponse(serializer.data, safe=False)
            else:
                gri_reviews = GriReview.objects.all()
                serializer = GriReviewSerializer(gri_reviews, many=True)
                return JsonResponse(serializer.data, safe=False)

        except Exception as e:
            logging.warning("{} {}".format(type(e).__name__, e.args))
            return Response({"status": "Failure", "error": "{} {}".format(type(e).__name__, e.args)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, *args, **kwargs):
        try:
            dri_review_serializer = GriReviewSerializer(data=request.data,
                                                        many=False,
                                                        context={"created_by_id": request.user.user_id})
            if dri_review_serializer.is_valid():
                dri_review_serializer.save()
                return Response(dri_review_serializer.data, status=status.HTTP_200_OK)
            return Response(dri_review_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logging.warning("{} {}".format(type(e).__name__, e.args))
            return Response({"status": "Failure", "error": "{} {}".format(type(e).__name__, e.args)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, *args, **kwargs):
        try:
            gri_review_id = kwargs.get("gri_review_id")
            gri_review = GriReview.objects.filter(gri_review_id=gri_review_id).first()
            serializer = GriReviewSerializer(gri_review, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            logging.warning("{} {}".format(type(e).__name__, e.args))
            return Response({"status": "Failure", "error": "{} {}".format(type(e).__name__, e.args)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
