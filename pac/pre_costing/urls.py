from django.urls import path
from rest_framework import routers

import pac.pre_costing.views as views
import pac.pre_costing.line_haul_costs.line_haul as line_hauls
import pac.pre_costing.currency_exchange_views as ce_views
import pac.pre_costing.pickup_delivery.pickup_delivery as pickup_del

router = routers.DefaultRouter()
router.register(r'terminalcost', views.TerminalCostViewSet,
                basename='terminal-cost')
router.register(r'dockroute', views.DockRouteViewSet,
                basename='dock-route')
router.register(r'laneroute', views.LaneRouteViewSet,
                basename='lane-route')
router.register(r'lanecost', views.LaneCostViewSet,
                basename='lane-cost')
router.register(r'legcost', views.LegCostViewSet,
                basename='leg-cost')
router.register(r'brokercontractcost', views.BrokerContractCostViewSet,
                basename='broker-contract-cost')
router.register(r'speedsheet', views.SpeedSheetViewSet,
                basename='speed-sheet')
router.register(r'terminalservicepoint', views.TerminalServicePointViewSet,
                basename='terminal-service-point')
router.register(r'weightbreakheader', views.WeightBreakHeaderViewSet,
                basename='weight-break-header')

urlpatterns = [
    path(
        'country/revert/<str:country_id>/<int:version_num>/',
        views.CountryRevertVersionView.as_view(),
        name='country-revert'
    ),
    path(
        'city/revert/<str:city_id>/<int:version_num>/',
        views.CityRevertVersionView.as_view(),
        name='city-revert'
    ),
    path(
        'province/revert/<str:province_id>/<int:version_num>/',
        views.ProvinceRevertVersionView.as_view(),
        name='province-revert'
    ),
    path(
        'authentication_demo/',
        views.authentication_demo,
        name='authentication-demo'
    ),
    path(
        'dockcosts/dashboard/<int:service_offering_id>/',
        views.DockCostsDashboardView.as_view(),
        name='dockcosts-dashboard'
    ),
    path(
        'dockcosts/detail/<int:terminal_cost_id>/',
        views.DockCostsDetailPanelView.as_view(),
        name='dockcosts-panel'
    ),
    path(
        'dockcosts/dashboard/batch-update/',
        views.DockCostsBatchUpdateView.as_view(),
        name='dockcosts-dashboard-batch-update'
    ),
    path(
        'dockroute/dashboard/<int:service_offering_id>/',
        views.CrossDockRoutesDashboardPyodbcView.as_view(),
        name='dock-route-dashboard'
    ),
    path(
        'dockroute/detail/<int:dock_route_id>/',
        views.CrossDockRoutesDetailPanelView.as_view(),
        name='dock-route-panel'
    ),
    path(
        'dockroute/dashboard/batch-update/',
        views.DockRoutesBatchUpdateView.as_view(),
        name='dock-route-dashboard-batch-update'
    ),
    path(
        'laneroute/dashboard/<int:service_offering_id>/',
        views.LinehaulLaneRoutesDashboardPyodbcView.as_view(),
        name='lane-route-dashboard'
    ),
    path(
        'laneroute/dashboard/batch-update/',
        views.LaneRoutesBatchCreateUpdateView.as_view(),
        name='lane-route-dashboard-batch-update'
    ),
    path(
        'laneroute/detail/<int:lane_route_id>/',
        views.LinehaulLaneRoutesDetailPanelView.as_view(),
        name='lane-route-panel'
    ),
    path(
        'linehaul/dashboard/<int:service_offering_id>/',
        line_hauls.LaneCostsAPI.as_view(http_method_names = ['get']),
        name='linehaul-dashboard'
    ),
    path(
        'lanecost/dashboard/<int:service_offering_id>/',
        line_hauls.LaneCostsAPI.as_view(http_method_names = ['put']),
        name='lane-cost-reduced-dashboard'
    ),
    path(
        'linehaul/lanecosts/batch-update/',
        line_hauls.LaneCostsAPI.as_view(http_method_names = ['put', 'post']),
        name='lanecosts-dashboard-batch-update'
    ),
    path(
        'linehaul/legcosts/batch-update/',
        line_hauls.LegCostsAPI.as_view(),
        name='lanecosts-dashboard-batch-update'
    ),

    path(
        'legcost/dashboard/<int:service_offering_id>/',
        line_hauls.LegCostsAPI.as_view(),
        name='leg-cost-dashboard'
    ),
    path(
        'linehaul/dashboard/',
        views.LinehaulLaneLegCostBatchCreateUpdateView.as_view(),
        name='linehaul-batch-create-update'
    ),
    path(
        'lanecost/detail/<int:lane_cost_id>/',
        views.LinehaulLaneCostsDetailPanelView.as_view(),
        name='lane-cost-panel'
    ),
    path(
        'legcost/detail/<int:leg_cost_id>/',
        views.LinehaulLegCostsDetailPanelView.as_view(),
        name='leg-cost-panel'
    ),
    path(
        'legsforroutes/<int:service_level_id>/<int:origin_terminal_id>/',
        views.LegsForRoutesPyodbcView.as_view(),
        name='legs-for-routing'
    ),
    path(
        'lanecost/destination/<int:service_level_id>/<int:origin_terminal_id>/',
        views.LaneDestinationTerminalsPyodbcView.as_view(),
        name='lane-cost-destination'
    ),
    path(
        'legcost/origin/<int:service_level_id>/',
        views.LegCostOriginTerminalView.as_view(),
        name='leg-cost-origin'
    ),
    path(
        'legcost/destination/<int:service_level_id>/<int:origin_terminal_id>/',
        views.LegCostDestinationTerminalView.as_view(),
        name='leg-cost-destination'
    ),
    path(
        'pickup-delivery/dashboard/<int:service_offering_id>/',
        pickup_del.PickupDeliveryView.as_view(),
        name='broker-contract-cost-dashboard'
    ),
    path(
        'brokercontractcost/detail/<int:broker_contract_cost_id>/',
        views.BrokerContractDetailPanelView.as_view(),
        name='broker-contract-cost-panel'
    ),
    path(
        'currencyexchange/dashboard/',
        ce_views.CurrencyExchangeDashboardView.as_view(http_method_names = ['get']),
        name='currency-exchange-dashboard'
    ),
    path(
        'currencyexchange/update/',
        ce_views.CurrencyExchangeDashboardView.as_view(http_method_names = ['put']),
        name='currency-exchange-update'
    ),
    path(
        'speedsheet/dashboard/<int:service_offering_id>/',
        views.SpeedSheetDashboardView.as_view(),
        name='speed-sheet-dashboard'
    ),
    path(
        'terminalservicepoint/dashboard/',
        views.TerminalServicePointDashboardPyodbcView.as_view(),
        name='terminal-service-point-dashboard'
    ),
    path(
        'terminalservicepoint/detail/<int:terminal_service_point_id>/',
        views.PointsExtraMilesDetailPanelView.as_view(),
        name='terminal-service-point-panel'
    ),
    path(
        'weightbreakheader/detail/<int:weight_break_header_id>/',
        views.WeightBreakHeaderDetailPanelView.as_view(),
        name='weight-break-header-panel'
    ),
    path(
        'weightbreakheader/dashboard/<int:service_offering_id>/',
        views.WeightBreakHeadersDashboardPyodbcView.as_view(),
        name='weight-break-header-dashboard'
    ),
    path(
        'weightbreakheader/dashboard/level/<int:service_level_id>/',
        views.WeightBreakHeadersLevelPyodbcView.as_view(),
        name='weight-break-header-level'
    ),
    path(
        'dockroute/create/',
        views.post_dockroute_pyodbc,
        name='dockroute-create'
    ),
    path(
        'lanecostweightbreaklevel/batch-update/',
        views.post_lane_cost_weight_break_level_pyodbc,
        name='lanecostweightbreaklevel-batch-update'
    ),
    path(
        'terminalcostweightbreaklevel/batch-update/',
        views.post_terminal_cost_weight_break_level_pyodbc,
        name='terminalcostweightbreaklevel-batch-update'
    ),
    path(
        'brokercontractcostweightbreaklevel/batch-update/<int:terminal_id>/<int:service_level_id>/',
        views.post_broker_contract_cost_weight_break_level_pyodbc.as_view(),
        name='brokercontractcostweightbreaklevel-batch-update'
    ),
    path(
        'accountsearch/<int:service_level_id>/<str:account_name>/',
        views.account_search_by_name_pyodbc.as_view(),
        name='account-search-by-name'
    ),
    path(
        'citysearch/<int:province_id>/<str:city_name>/',
        views.city_search_by_name_pyodbc.as_view(),
        name='city-search-by-name'
    ),
    path(
        'servicepointsearch/<int:service_offering_id>/<str:service_point_name>/',
        views.service_point_search_by_name_pyodbc.as_view(),
        name='service-point-search-by-name'
    ),
    path(
        'gri-review/',
        views.GriReviewView.as_view(),
        name='gri-view'
    ),
    path(
        'gri-review/<int:gri_review_id>/',
        views.GriReviewView.as_view(),
        name='gri-view'
    ),
]
urlpatterns += router.urls
