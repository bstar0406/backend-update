import json
import random

from django.test import TestCase
from django.urls import reverse
from model_bakery import baker
from rest_framework.test import APIClient, APITestCase
from unittest import skip

# from pac.models import (City, CostCalculationMethod,
#                         CostCalculationMethodHistory, Country, Region,
#                         ServicePoint, Terminal, WeightBreakHeader)
from pac.models import (City, Country, Region,
                        ServicePoint, Terminal, WeightBreakHeader)
from pac.pre_costing.models import (BrokerContractCost, CurrencyExchange,
                                    DockRoute, Lane, LaneCost, LaneRoute,
                                    LegCost, LegCostHistory, Province,
                                    ServiceLevel, ServiceMode, ServiceOffering,
                                    SpeedSheet, TerminalCost,
                                    TerminalServicePoint, Unit)
from pac.pre_costing.serializers import (BrokerContractCostSerializer,
                                         CurrencyExchangeSerializer,
                                         DockRouteSerializer,
                                         LaneCostSerializer,
                                         LaneRouteSerializer, LaneSerializer,
                                         LegCostSerializer,
                                         SpeedSheetSerializer,
                                         TerminalCostSerializer,
                                         TerminalSerializer,
                                         TerminalServicePointSerializer,
                                         UnitSerializer,
                                         WeightBreakHeaderSerializer)
from pac.pre_costing.views import TerminalCostViewSet


class PreCostingMockTest(APITestCase):

    def setUp(self):
        self.client = APIClient()

    def test_dock_costs_dashboard(self):
        service_offering = baker.make(ServiceOffering, service_offering_id=1)
        baker.make(TerminalCost, _quantity=5,
                   service_offering=service_offering)

        response = self.client.get(
            reverse('dockcosts-dashboard', kwargs={"service_offering_id": service_offering.service_offering_id}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 5)

    def test_terminal_cost_batch_update(self):
        terminal_cost = baker.make(TerminalCost, cost=json.dumps({"test": 0}))
        payload = []
        for i in range(5):
            terminal_cost.cost = json.dumps({"test": i})
            payload.append(TerminalCostSerializer(terminal_cost).data)

        response = self.client.put(
            reverse('terminal-cost-batch-update'), payload, format='json')
        terminal_cost = TerminalCost.objects.get(
            terminal_cost_id=terminal_cost.terminal_cost_id)

        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(json.loads(terminal_cost.cost)["test"], 0)
        self.assertEqual(json.loads(terminal_cost.cost)["test"], 4)

        payload = [TerminalCostSerializer(
            terminal_cost).data for i in range(2)]
        del payload[0]["terminal_cost_id"]

        response = self.client.put(
            reverse('terminal-cost-batch-update'), payload, format='json')

        self.assertEqual(response.status_code, 400)

    def test_metadata(self):
        data_models = {"countries", "provinces", "cities", "regions",
                       "terminals", "service_offerings", "cost_calculation_methods"}

        response = self.client.get(reverse('metadata'))
        self.assertEqual(response.status_code, 200)

        response_data_models = response.data.keys()
        self.assertFalse(data_models.difference(response_data_models))

    def test_dock_costs_detail_panel(self):
        terminal_cost = baker.make(TerminalCost, cost="{}")

        for i in range(5):
            terminal_cost.save()

        response = self.client.get(reverse(
            'dockcosts-panel', kwargs={"terminal_cost_id": terminal_cost.terminal_cost_id}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["terminal_cost_id"], terminal_cost.terminal_cost_id)
        self.assertEqual(len(response.data["terminal_cost_history"]), 6)

    def test_dock_costs_dashboard_batch_update(self):
        terminal_cost = baker.make(TerminalCost, cost=json.dumps({"test": 0}))
        terminal = baker.make(Terminal, terminal_name="0")
        payload = {"terminals": [], "terminal_costs": []}

        for i in range(5):
            terminal_cost.cost = json.dumps({"test": i})
            payload["terminal_costs"].append(
                TerminalCostSerializer(terminal_cost).data)
            terminal.terminal_name = str(i)
            terminal.is_active = False
            payload["terminals"].append(TerminalSerializer(terminal).data)

        response = self.client.put(
            reverse('dockcosts-dashboard-batch-update'), payload, format='json')

        terminal_cost = TerminalCost.objects.get(
            terminal_cost_id=terminal_cost.terminal_cost_id)
        terminal = Terminal.objects.get(terminal_id=terminal.terminal_id)

        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(json.loads(terminal_cost.cost)["test"], 0)
        self.assertEqual(json.loads(terminal_cost.cost)["test"], 4)
        self.assertNotEqual(terminal.terminal_name, str(0))
        self.assertEqual(terminal.terminal_name, str(4))
        self.assertEqual(terminal.is_active, False)

        payload = {"terminals": [], "terminal_costs": [TerminalCostSerializer(
            terminal_cost).data for i in range(2)]}
        del payload["terminal_costs"][0]["terminal_cost_id"]

        response = self.client.put(
            reverse('dockcosts-dashboard-batch-update'), payload, format='json')

        self.assertEqual(response.status_code, 400)

    def test_cross_dock_routes_dashboard(self):
        service_offering = baker.make(ServiceOffering, service_offering_id=1)
        service_level = baker.make(
            ServiceLevel, service_offering=service_offering)
        for i in range(5):
            lane = baker.make(Lane)
            baker.make(DockRoute, service_level=service_level, lane=lane)

        response = self.client.get(reverse(
            'dock-route-dashboard', kwargs={"service_offering_id": service_offering.service_offering_id}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 5)

    def test_cross_dock_routes_detail_pane(self):
        dock_route = baker.make(DockRoute)

        response = self.client.get(
            reverse('dock-route-panel', kwargs={"dock_route_id": dock_route.dock_route_id}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["dock_route_id"], dock_route.dock_route_id)

    def test_dock_route_batch_update(self):
        dock_route = baker.make(DockRoute, route_legs=json.dumps({"test": 0}))
        payload = []
        for i in range(5):
            dock_route.route_legs = json.dumps({"test": i})
            payload.append(DockRouteSerializer(dock_route).data)

        response = self.client.put(
            reverse('dock-route-batch-update'), payload, format='json')
        dock_route = DockRoute.objects.get(
            dock_route_id=dock_route.dock_route_id)

        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(json.loads(dock_route.route_legs)["test"], 0)
        self.assertEqual(json.loads(dock_route.route_legs)["test"], 4)

        payload = [DockRouteSerializer(
            dock_route).data for i in range(2)]
        del payload[0]["dock_route_id"]

        response = self.client.put(
            reverse('dock-route-batch-update'), payload, format='json')

        self.assertEqual(response.status_code, 400)

    def test_dock_route_create(self):
        service_level = baker.make(ServiceLevel)
        lane = baker.make(Lane)
        lane_json = LaneSerializer(lane).data
        dock_route = baker.prepare(
            DockRoute, route_legs=str(random.randint(0, 9999)), service_level=service_level)

        payload = DockRouteSerializer(dock_route).data
        payload["lane"] = {k: v for k, v in lane_json.items() if k in (
            "origin_terminal", "destination_terminal")}

        response = self.client.post(
            reverse('dock-route-list'), payload, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.data["service_level_id"], dock_route.service_level_id)
        self.assertEqual(Lane.objects.filter(
            origin_terminal=response.data["origin_terminal_id"], destination_terminal=response.data["destination_terminal_id"]).first().pk, lane.pk)

        dock_route = baker.prepare(
            DockRoute, route_legs=str(random.randint(0, 9999)), service_level=service_level)
        origin_terminal = baker.make(Terminal)
        destination_terminal = baker.make(Terminal)

        payload = DockRouteSerializer(dock_route).data
        payload["lane"] = {"origin_terminal": origin_terminal.pk,
                           "destination_terminal": destination_terminal.pk}

        self.assertFalse(Lane.objects.filter(**payload["lane"]).exists())

        response = self.client.post(
            reverse('dock-route-list'), payload, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.data["service_level_id"], dock_route.service_level_id)
        self.assertTrue(Lane.objects.filter(**payload["lane"]).exists())

    def test_dock_route_archive(self):
        dock_route = baker.make(DockRoute)

        response = self.client.patch(
            reverse('dock-route-archive', kwargs={"dock_route_id": dock_route.dock_route_id}))

        dock_route = DockRoute.objects.filter(
            dock_route_id=dock_route.dock_route_id).first()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(dock_route.is_active, False)
        self.assertEqual(dock_route.is_inactive_viewable, True)

        dock_route = baker.make(DockRoute, is_inactive_viewable=False)

        response = self.client.patch(
            reverse('dock-route-archive', kwargs={"dock_route_id": dock_route.dock_route_id}))

        self.assertEqual(response.status_code, 404)

    def test_dock_route_unarchive(self):
        dock_route = baker.make(DockRoute, is_active=False)

        response = self.client.patch(
            reverse('dock-route-unarchive', kwargs={"dock_route_id": dock_route.dock_route_id}))

        dock_route = DockRoute.objects.filter(
            dock_route_id=dock_route.dock_route_id).first()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(dock_route.is_active, True)
        self.assertEqual(dock_route.is_inactive_viewable, True)

        dock_route = baker.make(
            DockRoute, is_inactive_viewable=False, is_active=False)

        response = self.client.patch(
            reverse('dock-route-unarchive', kwargs={"dock_route_id": dock_route.dock_route_id}))

        self.assertEqual(response.status_code, 404)

        dock_route = baker.make(DockRoute)

        response = self.client.patch(
            reverse('dock-route-unarchive', kwargs={"dock_route_id": dock_route.dock_route_id}))

        self.assertEqual(response.status_code, 404)

    def test_dock_route_delete(self):
        dock_route = baker.make(DockRoute)

        response = self.client.delete(reverse(
            'dock-route-detail', kwargs={"dock_route_id": dock_route.dock_route_id}))

        dock_route = DockRoute.objects.filter(
            dock_route_id=dock_route.dock_route_id).first()

        self.assertEqual(response.status_code, 204)
        self.assertEqual(dock_route.is_active, False)
        self.assertEqual(dock_route.is_inactive_viewable, False)

        dock_route = baker.make(DockRoute, is_inactive_viewable=False)

        response = self.client.delete(reverse(
            'dock-route-detail', kwargs={"dock_route_id": dock_route.dock_route_id}))

        self.assertEqual(response.status_code, 404)

    def test_linehaul_lane_routes_dashboard(self):
        service_offering = baker.make(ServiceOffering, service_offering_id=1)
        service_level = baker.make(
            ServiceLevel, service_offering=service_offering)
        for i in range(5):
            lane = baker.make(Lane)
            baker.make(LaneRoute, service_level=service_level, lane=lane)

        response = self.client.get(reverse(
            'lane-route-dashboard', kwargs={"service_offering_id": service_offering.service_offering_id}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 5)

    def test_linehaul_lane_routes_detail_pane(self):
        lane_route = baker.make(LaneRoute)

        response = self.client.get(
            reverse('lane-route-panel', kwargs={"lane_route_id": lane_route.lane_route_id}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["lane_route_id"], lane_route.lane_route_id)

    def test_lane_route_batch_update(self):
        lane_route = baker.make(LaneRoute, route_legs=json.dumps({"test": 0}))
        payload = []
        for i in range(5):
            lane_route.route_legs = json.dumps({"test": i})
            payload.append(LaneRouteSerializer(lane_route).data)

        response = self.client.put(
            reverse('lane-route-batch-update'), payload, format='json')
        lane_route = LaneRoute.objects.get(
            lane_route_id=lane_route.lane_route_id)

        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(json.loads(lane_route.route_legs)["test"], 0)
        self.assertEqual(json.loads(lane_route.route_legs)["test"], 4)

        payload = [LaneRouteSerializer(
            lane_route).data for i in range(2)]
        del payload[0]["lane_route_id"]

        response = self.client.put(
            reverse('lane-route-batch-update'), payload, format='json')

        self.assertEqual(response.status_code, 400)

    def test_lane_route_create(self):
        service_level = baker.make(ServiceLevel)
        lane = baker.make(Lane)
        lane_json = LaneSerializer(lane).data
        lane_route = baker.prepare(
            LaneRoute, route_legs=str(random.randint(0, 9999)), service_level=service_level)

        payload = LaneRouteSerializer(lane_route).data
        payload["lane"] = {k: v for k, v in lane_json.items() if k in (
            "origin_terminal", "destination_terminal")}

        response = self.client.post(
            reverse('lane-route-list'), payload, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.data["service_level_id"], lane_route.service_level_id)
        self.assertEqual(Lane.objects.filter(
            origin_terminal=response.data["origin_terminal_id"], destination_terminal=response.data["destination_terminal_id"]).first().pk, lane.pk)

        lane_route = baker.prepare(
            LaneRoute, route_legs=str(random.randint(0, 9999)), service_level=service_level)
        origin_terminal = baker.make(Terminal)
        destination_terminal = baker.make(Terminal)

        payload = LaneRouteSerializer(lane_route).data
        payload["lane"] = {"origin_terminal": origin_terminal.pk,
                           "destination_terminal": destination_terminal.pk}

        self.assertFalse(Lane.objects.filter(**payload["lane"]).exists())

        response = self.client.post(
            reverse('lane-route-list'), payload, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.data["service_level_id"], lane_route.service_level_id)
        self.assertTrue(Lane.objects.filter(**payload["lane"]).exists())

    def test_lane_route_archive(self):
        lane_route = baker.make(LaneRoute)

        response = self.client.patch(
            reverse('lane-route-archive', kwargs={"lane_route_id": lane_route.lane_route_id}))

        lane_route = LaneRoute.objects.filter(
            lane_route_id=lane_route.lane_route_id).first()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(lane_route.is_active, False)
        self.assertEqual(lane_route.is_inactive_viewable, True)

        lane_route = baker.make(LaneRoute, is_inactive_viewable=False)

        response = self.client.patch(
            reverse('lane-route-archive', kwargs={"lane_route_id": lane_route.lane_route_id}))

        self.assertEqual(response.status_code, 404)

    def test_lane_route_unarchive(self):
        lane_route = baker.make(LaneRoute, is_active=False)

        response = self.client.patch(
            reverse('lane-route-unarchive', kwargs={"lane_route_id": lane_route.lane_route_id}))

        lane_route = LaneRoute.objects.filter(
            lane_route_id=lane_route.lane_route_id).first()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(lane_route.is_active, True)
        self.assertEqual(lane_route.is_inactive_viewable, True)

        lane_route = baker.make(
            LaneRoute, is_inactive_viewable=False, is_active=False)

        response = self.client.patch(
            reverse('lane-route-unarchive', kwargs={"lane_route_id": lane_route.lane_route_id}))

        self.assertEqual(response.status_code, 404)

        lane_route = baker.make(LaneRoute)

        response = self.client.patch(
            reverse('lane-route-unarchive', kwargs={"lane_route_id": lane_route.lane_route_id}))

        self.assertEqual(response.status_code, 404)

    def test_lane_route_delete(self):
        lane_route = baker.make(LaneRoute)

        response = self.client.delete(reverse(
            'lane-route-detail', kwargs={"lane_route_id": lane_route.lane_route_id}))

        lane_route = LaneRoute.objects.filter(
            lane_route_id=lane_route.lane_route_id).first()

        self.assertEqual(response.status_code, 204)
        self.assertEqual(lane_route.is_active, False)
        self.assertEqual(lane_route.is_inactive_viewable, False)

        lane_route = baker.make(LaneRoute, is_inactive_viewable=False)

        response = self.client.delete(reverse(
            'lane-route-detail', kwargs={"lane_route_id": lane_route.lane_route_id}))

        self.assertEqual(response.status_code, 404)

    def test_linehaul_lane_costs_dashboard(self):
        service_offering = baker.make(ServiceOffering)
        lane = baker.make(Lane)
        for i in range(5):
            service_level = baker.make(
                ServiceLevel, service_offering=service_offering)
            lane_route = baker.make(
                LaneRoute, lane=lane, service_level=service_level)
            lane_cost = baker.make(
                LaneCost, service_level=service_level, lane=lane)

        response = self.client.get(reverse(
            'lane-cost-dashboard', kwargs={"service_offering_id": service_offering.service_offering_id}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 5)

    def test_linehaul_leg_costs_dashboard(self):
        service_offering = baker.make(ServiceOffering)
        lane = baker.make(Lane)
        for i in range(5):
            service_level = baker.make(
                ServiceLevel, service_offering=service_offering)
            lane_route = baker.make(
                LaneRoute, lane=lane, service_level=service_level)
            leg_cost = baker.make(
                LegCost, service_level=service_level, lane=lane)

        response = self.client.get(reverse(
            'leg-cost-dashboard', kwargs={"service_offering_id": service_offering.service_offering_id}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 5)

    def test_linehaul_lane_costs_detail_panel(self):
        service_offering = baker.make(ServiceOffering)
        lane = baker.make(Lane)
        service_level = baker.make(
            ServiceLevel, service_offering=service_offering)
        lane_route = baker.make(
            LaneRoute, lane=lane, service_level=service_level)
        lane_cost = baker.make(
            LaneCost, service_level=service_level, lane=lane)

        for i in range(5):
            lane_cost.save()

        response = self.client.get(reverse(
            'lane-cost-panel', kwargs={"lane_cost_id": lane_cost.lane_cost_id}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["lane_cost_history"]), 6)

    def test_linehaul_leg_costs_detail_panel(self):
        leg_cost = baker.make(LegCost)

        for i in range(5):
            leg_cost.save()

        response = self.client.get(reverse(
            'leg-cost-panel', kwargs={"leg_cost_id": leg_cost.leg_cost_id}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["leg_cost_history"]), 6)

    def test_linehaul_lane_leg_cost_batch_create_update(self):
        # Create by passing lane id for lane that does exist

        service_level = baker.make(ServiceLevel)
        service_mode = baker.make(ServiceMode)
        lane = baker.make(Lane)
        lane_cost = baker.prepare(
            LaneCost, service_level=service_level, lane=lane, cost=json.dumps({"test": 0}))
        leg_cost = baker.prepare(
            LegCost, service_level=service_level, service_mode=service_mode, lane=lane, cost=json.dumps({"test": 0}))

        payload = {"leg_costs": [LegCostSerializer(
            leg_cost).data], "lane_costs": [LaneCostSerializer(lane_cost).data]}

        response = self.client.post(
            reverse('linehaul-batch-create-update'), payload, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(LegCost.objects.all()), 1)
        self.assertEqual(len(LaneCost.objects.all()), 1)

        # Create by passing origin and destination terminal for lane that doesn't exist

        service_level = baker.make(ServiceLevel)
        service_mode = baker.make(
            ServiceMode, service_mode_id=random.randint(0, 9999))
        lane_cost = baker.prepare(
            LaneCost, service_level=service_level, cost=json.dumps({"test": 0}))
        leg_cost = baker.prepare(
            LegCost, service_level=service_level, service_mode=service_mode, cost=json.dumps({"test": 0}))

        origin_terminal = baker.make(Terminal)
        destination_terminal = baker.make(Terminal)

        leg_cost_payload = LegCostSerializer(leg_cost).data
        lane_cost_payload = LaneCostSerializer(lane_cost).data
        leg_cost_payload["lane"] = {"origin_terminal": origin_terminal.pk,
                                    "destination_terminal": destination_terminal.pk}
        lane_cost_payload["lane"] = {"origin_terminal": origin_terminal.pk,
                                     "destination_terminal": destination_terminal.pk}
        payload = {"leg_costs": [leg_cost_payload],
                   "lane_costs": [lane_cost_payload]}

        self.assertFalse(Lane.objects.filter(
            **lane_cost_payload["lane"]).exists())

        response = self.client.post(
            reverse('linehaul-batch-create-update'), payload, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Lane.objects.filter(
            **lane_cost_payload["lane"]).exists())

        # Update by passing lane id for lane that does exist

        service_level = baker.make(ServiceLevel)
        service_mode = baker.make(ServiceMode)
        lane = baker.make(Lane)
        lane_cost = baker.make(
            LaneCost, service_level=service_level, lane=lane, cost=json.dumps({"test": 0}))
        leg_cost = baker.make(
            LegCost, service_level=service_level, service_mode=service_mode, lane=lane, cost=json.dumps({"test": 0}))

        payload = {"leg_costs": [], "lane_costs": []}
        for i in range(5):
            leg_cost.cost = json.dumps({"test": i})
            lane_cost.cost = json.dumps({"test": i})
            payload["leg_costs"].append(LegCostSerializer(leg_cost).data)
            payload["lane_costs"].append(LaneCostSerializer(lane_cost).data)

        lane_cost = LaneCost.objects.filter(pk=lane_cost.pk).first()
        leg_cost = LegCost.objects.filter(pk=leg_cost.pk).first()

        self.assertEqual(json.loads(lane_cost.cost)["test"], 0)
        self.assertEqual(json.loads(leg_cost.cost)["test"], 0)

        response = self.client.post(
            reverse('linehaul-batch-create-update'), payload, format='json')

        lane_cost = LaneCost.objects.filter(pk=lane_cost.pk).first()
        leg_cost = LegCost.objects.filter(pk=leg_cost.pk).first()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(lane_cost.cost)["test"], 4)
        self.assertEqual(json.loads(leg_cost.cost)["test"], 4)

        # Update by passing origin and terminal destination for lane that doesn't exist

        service_level = baker.make(ServiceLevel)
        service_mode = baker.make(
            ServiceMode, service_mode_id=random.randint(0, 9999))
        lane_cost = baker.make(
            LaneCost, service_level=service_level, cost=json.dumps({"test": 0}))
        leg_cost = baker.make(
            LegCost, service_level=service_level, service_mode=service_mode, cost=json.dumps({"test": 0}))

        origin_terminal = baker.make(Terminal)
        destination_terminal = baker.make(Terminal)

        payload = {"leg_costs": [], "lane_costs": []}
        for i in range(5):
            leg_cost.cost = json.dumps({"test": i})
            lane_cost.cost = json.dumps({"test": i})
            leg_cost_data = LegCostSerializer(leg_cost).data
            leg_cost_data.update({"lane": {"origin_terminal": origin_terminal.pk,
                                           "destination_terminal": destination_terminal.pk}})
            lane_cost_data = LaneCostSerializer(lane_cost).data
            lane_cost_data.update({"lane": {"origin_terminal": origin_terminal.pk,
                                            "destination_terminal": destination_terminal.pk}})
            payload["leg_costs"].append(leg_cost_data)
            payload["lane_costs"].append(lane_cost_data)

        self.assertFalse(Lane.objects.filter(
            **{"origin_terminal": origin_terminal.pk, "destination_terminal": destination_terminal.pk}).exists())

        lane_cost = LaneCost.objects.filter(pk=lane_cost.pk).first()
        leg_cost = LegCost.objects.filter(pk=leg_cost.pk).first()

        self.assertEqual(json.loads(lane_cost.cost)["test"], 0)
        self.assertEqual(json.loads(leg_cost.cost)["test"], 0)

        response = self.client.post(
            reverse('linehaul-batch-create-update'), payload, format='json')

        lane_cost = LaneCost.objects.filter(pk=lane_cost.pk).first()
        leg_cost = LegCost.objects.filter(pk=leg_cost.pk).first()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Lane.objects.filter(
            **{"origin_terminal": origin_terminal.pk, "destination_terminal": destination_terminal.pk}).exists())
        self.assertEqual(json.loads(lane_cost.cost)["test"], 4)
        self.assertEqual(json.loads(leg_cost.cost)["test"], 4)

    def test_lane_cost_batch_update(self):
        lane_cost = baker.make(LaneCost, cost=json.dumps({"test": 0}))
        payload = []
        for i in range(5):
            lane_cost.cost = json.dumps({"test": i})
            payload.append(LaneCostSerializer(lane_cost).data)

        response = self.client.put(
            reverse('lane-cost-batch-update'), payload, format='json')
        lane_cost = LaneCost.objects.get(
            lane_cost_id=lane_cost.lane_cost_id)

        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(json.loads(lane_cost.cost)["test"], 0)
        self.assertEqual(json.loads(lane_cost.cost)["test"], 4)

        payload = [LaneCostSerializer(
            lane_cost).data for i in range(2)]
        del payload[0]["lane_cost_id"]

        response = self.client.put(
            reverse('lane-cost-batch-update'), payload, format='json')

        self.assertEqual(response.status_code, 400)

    def test_lane_cost_create(self):
        service_level = baker.make(ServiceLevel)
        lane = baker.make(Lane)
        lane_cost = baker.prepare(
            LaneCost, cost=str(random.randint(0, 9999)), service_level=service_level, lane=lane)

        payload = LaneCostSerializer(lane_cost).data

        response = self.client.post(
            reverse('lane-cost-list'), payload, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["cost"], lane_cost.cost)

    def test_lane_cost_archive(self):
        lane_cost = baker.make(LaneCost)

        response = self.client.patch(
            reverse('lane-cost-archive', kwargs={"lane_cost_id": lane_cost.lane_cost_id}))

        lane_cost = LaneCost.objects.filter(
            lane_cost_id=lane_cost.lane_cost_id).first()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(lane_cost.is_active, False)
        self.assertEqual(lane_cost.is_inactive_viewable, True)

        lane_cost = baker.make(LaneCost, is_inactive_viewable=False)

        response = self.client.patch(
            reverse('lane-cost-archive', kwargs={"lane_cost_id": lane_cost.lane_cost_id}))

        self.assertEqual(response.status_code, 404)

    def test_lane_cost_unarchive(self):
        lane_cost = baker.make(LaneCost, is_active=False)

        response = self.client.patch(
            reverse('lane-cost-unarchive', kwargs={"lane_cost_id": lane_cost.lane_cost_id}))

        lane_cost = LaneCost.objects.filter(
            lane_cost_id=lane_cost.lane_cost_id).first()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(lane_cost.is_active, True)
        self.assertEqual(lane_cost.is_inactive_viewable, True)

        lane_cost = baker.make(
            LaneCost, is_inactive_viewable=False, is_active=False)

        response = self.client.patch(
            reverse('lane-cost-unarchive', kwargs={"lane_cost_id": lane_cost.lane_cost_id}))

        self.assertEqual(response.status_code, 404)

        lane_cost = baker.make(LaneCost)

        response = self.client.patch(
            reverse('lane-cost-unarchive', kwargs={"lane_cost_id": lane_cost.lane_cost_id}))

        self.assertEqual(response.status_code, 404)

    def test_lane_cost_delete(self):
        lane_cost = baker.make(LaneCost)

        response = self.client.delete(reverse(
            'lane-cost-detail', kwargs={"lane_cost_id": lane_cost.lane_cost_id}))

        lane_cost = LaneCost.objects.filter(
            lane_cost_id=lane_cost.lane_cost_id).first()

        self.assertEqual(response.status_code, 204)
        self.assertEqual(lane_cost.is_active, False)
        self.assertEqual(lane_cost.is_inactive_viewable, False)

        lane_cost = baker.make(LaneCost, is_inactive_viewable=False)

        response = self.client.delete(reverse(
            'lane-cost-detail', kwargs={"lane_cost_id": lane_cost.lane_cost_id}))

        self.assertEqual(response.status_code, 404)

    def test_leg_cost_batch_update(self):
        leg_cost = baker.make(LegCost, cost=json.dumps({"test": 0}))
        payload = []
        for i in range(5):
            leg_cost.cost = json.dumps({"test": i})
            payload.append(LegCostSerializer(leg_cost).data)

        response = self.client.put(
            reverse('leg-cost-batch-update'), payload, format='json')
        leg_cost = LegCost.objects.get(
            leg_cost_id=leg_cost.leg_cost_id)

        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(json.loads(leg_cost.cost)["test"], 0)
        self.assertEqual(json.loads(leg_cost.cost)["test"], 4)

        payload = [LegCostSerializer(
            leg_cost).data for i in range(2)]
        del payload[0]["leg_cost_id"]

        response = self.client.put(
            reverse('leg-cost-batch-update'), payload, format='json')

        self.assertEqual(response.status_code, 400)

    def test_leg_cost_create(self):
        service_level = baker.make(ServiceLevel)
        service_mode = baker.make(ServiceMode)
        lane = baker.make(Lane)
        leg_cost = baker.prepare(
            LegCost, cost=str(random.randint(0, 9999)), service_level=service_level, service_mode=service_mode, lane=lane)

        payload = LegCostSerializer(leg_cost).data

        response = self.client.post(
            reverse('leg-cost-list'), payload, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["cost"], leg_cost.cost)

    def test_leg_cost_archive(self):
        leg_cost = baker.make(LegCost)

        response = self.client.patch(
            reverse('leg-cost-archive', kwargs={"leg_cost_id": leg_cost.leg_cost_id}))

        leg_cost = LegCost.objects.filter(
            leg_cost_id=leg_cost.leg_cost_id).first()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(leg_cost.is_active, False)
        self.assertEqual(leg_cost.is_inactive_viewable, True)

        leg_cost = baker.make(LegCost, is_inactive_viewable=False)

        response = self.client.patch(
            reverse('leg-cost-archive', kwargs={"leg_cost_id": leg_cost.leg_cost_id}))

        self.assertEqual(response.status_code, 404)

    def test_leg_cost_unarchive(self):
        leg_cost = baker.make(LegCost, is_active=False)

        response = self.client.patch(
            reverse('leg-cost-unarchive', kwargs={"leg_cost_id": leg_cost.leg_cost_id}))

        leg_cost = LegCost.objects.filter(
            leg_cost_id=leg_cost.leg_cost_id).first()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(leg_cost.is_active, True)
        self.assertEqual(leg_cost.is_inactive_viewable, True)

        leg_cost = baker.make(
            LegCost, is_inactive_viewable=False, is_active=False)

        response = self.client.patch(
            reverse('leg-cost-unarchive', kwargs={"leg_cost_id": leg_cost.leg_cost_id}))

        self.assertEqual(response.status_code, 404)

        leg_cost = baker.make(LegCost)

        response = self.client.patch(
            reverse('leg-cost-unarchive', kwargs={"leg_cost_id": leg_cost.leg_cost_id}))

        self.assertEqual(response.status_code, 404)

    def test_leg_cost_delete(self):
        leg_cost = baker.make(LegCost)

        response = self.client.delete(reverse(
            'leg-cost-detail', kwargs={"leg_cost_id": leg_cost.leg_cost_id}))

        leg_cost = LegCost.objects.filter(
            leg_cost_id=leg_cost.leg_cost_id).first()

        self.assertEqual(response.status_code, 204)
        self.assertEqual(leg_cost.is_active, False)
        self.assertEqual(leg_cost.is_inactive_viewable, False)

        leg_cost = baker.make(LegCost, is_inactive_viewable=False)

        response = self.client.delete(reverse(
            'leg-cost-detail', kwargs={"leg_cost_id": leg_cost.leg_cost_id}))

        self.assertEqual(response.status_code, 404)

    @skip("CostCalculationMethod Model does not exist")
    def test_versioning(self):
        cost_calculation_method = baker.make(
            CostCalculationMethod, cost_calculation_method_id=random.randint(0, 9999))
        leg_cost = baker.make(LegCost, cost=json.dumps(
            [{"CostCalculationMethodID": cost_calculation_method.pk}]))

        for i in range(5):
            leg_cost.save()

        cost_calculation_method_latest_history_version = CostCalculationMethodHistory.objects.filter(
            cost_calculation_method=cost_calculation_method, is_latest_version=True).first()
        leg_cost_latest_history_version = LegCostHistory.objects.filter(
            leg_cost=leg_cost, is_latest_version=True).first()

        self.assertTrue("CostCalculationMethodVersionID" in json.loads(
            leg_cost_latest_history_version.cost)[0])
        self.assertNotEqual(json.loads(
            leg_cost_latest_history_version.cost)[0]["CostCalculationMethodVersionID"], cost_calculation_method.pk)
        self.assertEqual(json.loads(
            leg_cost_latest_history_version.cost)[0]["CostCalculationMethodVersionID"], cost_calculation_method_latest_history_version.pk)

    def test_broker_contract_dashboard(self):
        service_offering = baker.make(ServiceOffering, service_offering_id=1)
        service_level = baker.make(
            ServiceLevel, service_offering=service_offering)
        baker.make(BrokerContractCost, _quantity=5,
                   service_level=service_level)

        response = self.client.get(reverse('broker-contract-cost-dashboard', kwargs={
                                   "service_offering_id": service_offering.service_offering_id}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 5)

    def test_broker_contract_detail_panel(self):
        broker_contract_cost = baker.make(
            BrokerContractCost, cost_by_weight_break="{}")

        for i in range(5):
            broker_contract_cost.save()

        response = self.client.get(reverse(
            'broker-contract-cost-panel', kwargs={"broker_contract_cost_id": broker_contract_cost.broker_contract_cost_id}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["broker_contract_cost_id"], broker_contract_cost.broker_contract_cost_id)
        self.assertEqual(len(response.data["broker_contract_cost_history"]), 6)

    def test_broker_contract_cost_batch_update(self):
        broker_contract_cost = baker.make(
            BrokerContractCost, cost_by_weight_break=json.dumps({"test": 0}))
        payload = []
        for i in range(5):
            broker_contract_cost.cost_by_weight_break = json.dumps({"test": i})
            payload.append(BrokerContractCostSerializer(
                broker_contract_cost).data)

        response = self.client.put(
            reverse('broker-contract-cost-batch-update'), payload, format='json')
        broker_contract_cost = BrokerContractCost.objects.get(
            broker_contract_cost_id=broker_contract_cost.broker_contract_cost_id)

        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(json.loads(
            broker_contract_cost.cost_by_weight_break)["test"], 0)
        self.assertEqual(json.loads(
            broker_contract_cost.cost_by_weight_break)["test"], 4)

        payload = [BrokerContractCostSerializer(
            broker_contract_cost).data for i in range(2)]
        del payload[0]["broker_contract_cost_id"]

        response = self.client.put(
            reverse('broker-contract-cost-batch-update'), payload, format='json')

        self.assertEqual(response.status_code, 400)

    def test_broker_contract_cost_create(self):
        terminal = baker.make(Terminal)
        service_level = baker.make(ServiceLevel)
        broker_contract_cost = baker.prepare(
            BrokerContractCost, cost_by_weight_break=str(random.randint(0, 9999)), service_level=service_level, terminal=terminal)

        payload = BrokerContractCostSerializer(broker_contract_cost).data

        response = self.client.post(
            reverse('broker-contract-cost-list'), payload, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.data["cost_by_weight_break"], broker_contract_cost.cost_by_weight_break)

    def test_broker_contract_cost_archive(self):
        broker_contract_cost = baker.make(BrokerContractCost)

        response = self.client.patch(
            reverse('broker-contract-cost-archive', kwargs={"broker_contract_cost_id": broker_contract_cost.broker_contract_cost_id}))

        broker_contract_cost = BrokerContractCost.objects.filter(
            broker_contract_cost_id=broker_contract_cost.broker_contract_cost_id).first()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(broker_contract_cost.is_active, False)
        self.assertEqual(broker_contract_cost.is_inactive_viewable, True)

        broker_contract_cost = baker.make(
            BrokerContractCost, is_inactive_viewable=False)

        response = self.client.patch(
            reverse('broker-contract-cost-archive', kwargs={"broker_contract_cost_id": broker_contract_cost.broker_contract_cost_id}))

        self.assertEqual(response.status_code, 404)

    def test_broker_contract_cost_unarchive(self):
        broker_contract_cost = baker.make(BrokerContractCost, is_active=False)

        response = self.client.patch(
            reverse('broker-contract-cost-unarchive', kwargs={"broker_contract_cost_id": broker_contract_cost.broker_contract_cost_id}))

        broker_contract_cost = BrokerContractCost.objects.filter(
            broker_contract_cost_id=broker_contract_cost.broker_contract_cost_id).first()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(broker_contract_cost.is_active, True)
        self.assertEqual(broker_contract_cost.is_inactive_viewable, True)

        broker_contract_cost = baker.make(
            BrokerContractCost, is_inactive_viewable=False, is_active=False)

        response = self.client.patch(
            reverse('broker-contract-cost-unarchive', kwargs={"broker_contract_cost_id": broker_contract_cost.broker_contract_cost_id}))

        self.assertEqual(response.status_code, 404)

        broker_contract_cost = baker.make(BrokerContractCost)

        response = self.client.patch(
            reverse('broker-contract-cost-unarchive', kwargs={"broker_contract_cost_id": broker_contract_cost.broker_contract_cost_id}))

        self.assertEqual(response.status_code, 404)

    def test_broker_contract_cost_delete(self):
        broker_contract_cost = baker.make(BrokerContractCost)

        response = self.client.delete(reverse(
            'broker-contract-cost-detail', kwargs={"broker_contract_cost_id": broker_contract_cost.broker_contract_cost_id}))

        broker_contract_cost = BrokerContractCost.objects.filter(
            broker_contract_cost_id=broker_contract_cost.broker_contract_cost_id).first()

        self.assertEqual(response.status_code, 204)
        self.assertEqual(broker_contract_cost.is_active, False)
        self.assertEqual(broker_contract_cost.is_inactive_viewable, False)

        broker_contract_cost = baker.make(
            BrokerContractCost, is_inactive_viewable=False)

        response = self.client.delete(reverse(
            'broker-contract-cost-detail', kwargs={"broker_contract_cost_id": broker_contract_cost.broker_contract_cost_id}))

        self.assertEqual(response.status_code, 404)

    def test_currency_exchange_dashboard(self):
        currency_exchange = baker.make(CurrencyExchange)

        for i in range(5):
            currency_exchange.save()

        response = self.client.get(reverse('currency-exchange-dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["currency_exchange_history"]), 6)

    def test_currency_exchange_batch_update(self):
        currency_exchange = baker.make(
            CurrencyExchange, cad_to_usd=0)
        payload = []
        for i in range(5):
            currency_exchange.cad_to_usd = i
            payload.append(CurrencyExchangeSerializer(currency_exchange).data)

        response = self.client.put(
            reverse('currency-exchange-batch-update'), payload, format='json')
        currency_exchange = CurrencyExchange.objects.get(
            currency_exchange_id=currency_exchange.currency_exchange_id)

        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(currency_exchange.cad_to_usd, 0)
        self.assertEqual(currency_exchange.cad_to_usd, 4)

        payload = [CurrencyExchangeSerializer(
            currency_exchange).data for i in range(2)]
        del payload[0]["currency_exchange_id"]

        response = self.client.put(
            reverse('currency-exchange-batch-update'), payload, format='json')

        self.assertEqual(response.status_code, 400)

    def test_speed_sheet_dashboard(self):
        service_offering = baker.make(ServiceOffering, service_offering_id=1)
        speed_sheet = baker.make(SpeedSheet, service_offering=service_offering)

        for i in range(5):
            speed_sheet.save()

        response = self.client.get(reverse(
            'speed-sheet-dashboard', kwargs={"service_offering_id": service_offering.service_offering_id}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["speed_sheet_history"]), 6)

    def test_speed_sheet_batch_update(self):
        speed_sheet = baker.make(
            SpeedSheet, margin=0)
        payload = []
        for i in range(5):
            speed_sheet.margin = i
            payload.append(SpeedSheetSerializer(speed_sheet).data)

        response = self.client.put(
            reverse('speed-sheet-batch-update'), payload, format='json')
        speed_sheet = SpeedSheet.objects.get(
            speed_sheet_id=speed_sheet.speed_sheet_id)

        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(speed_sheet.margin, 0)
        self.assertEqual(speed_sheet.margin, 4)

        payload = [SpeedSheetSerializer(
            speed_sheet).data for i in range(2)]
        del payload[0]["speed_sheet_id"]

        response = self.client.put(
            reverse('speed-sheet-batch-update'), payload, format='json')

        self.assertEqual(response.status_code, 400)

    def test_points_extra_miles_dashboard(self):
        city = baker.make(City)
        terminal = baker.make(Terminal, city=city)
        province = baker.make(Province)
        for i in range(20):
            service_point = baker.make(ServicePoint, province=province)
            base_service_point = baker.make(ServicePoint, province=province)
            baker.make(TerminalServicePoint, terminal=terminal,
                       service_point=service_point, base_service_point=base_service_point)

        response = self.client.get(reverse(
            'terminal-service-point-dashboard', kwargs={"terminal_id": terminal.terminal_id}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 20)

    def test_points_extra_miles_detail_panel(self):
        terminal_service_point = baker.make(TerminalServicePoint)

        for i in range(5):
            terminal_service_point.save()

        response = self.client.get(reverse('terminal-service-point-panel', kwargs={
                                   "terminal_service_point_id": terminal_service_point.terminal_service_point_id}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["terminal_service_point_id"],
                         terminal_service_point.terminal_service_point_id)
        self.assertEqual(
            len(response.data["terminal_service_point_history"]), 6)

    def test_terminal_service_point_batch_update(self):
        terminal_service_point = baker.make(
            TerminalServicePoint, extra_miles=0)
        payload = []
        for i in range(5):
            terminal_service_point.extra_miles = i
            payload.append(TerminalServicePointSerializer(
                terminal_service_point).data)

        response = self.client.put(
            reverse('terminal-service-point-batch-update'), payload, format='json')
        terminal_service_point = TerminalServicePoint.objects.get(
            terminal_service_point_id=terminal_service_point.terminal_service_point_id)

        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(terminal_service_point.extra_miles, 0)
        self.assertEqual(terminal_service_point.extra_miles, 4)

        payload = [TerminalServicePointSerializer(
            terminal_service_point).data for i in range(2)]
        del payload[0]["terminal_service_point_id"]

        response = self.client.put(
            reverse('terminal-service-point-batch-update'), payload, format='json')

        self.assertEqual(response.status_code, 400)

    def test_lane_cost_origin_terminal(self):
        service_level = baker.make(ServiceLevel)
        for i in range(5):
            origin_terminal = baker.make(Terminal)
            lane = baker.make(Lane, origin_terminal=origin_terminal)
            lane_cost = baker.make(
                LaneCost, service_level=service_level, lane=lane)

        response = self.client.get(reverse(
            'lane-cost-origin', kwargs={"service_level_id": service_level.service_level_id}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 5)

    def test_lane_cost_destination_terminal(self):
        service_level = baker.make(ServiceLevel)
        origin_terminal = baker.make(Terminal)
        for i in range(5):
            lane = baker.make(Lane, origin_terminal=origin_terminal)
            lane_cost = baker.make(
                LaneCost, service_level=service_level, lane=lane)

        response = self.client.get(reverse(
            'lane-cost-destination', kwargs={"service_level_id": service_level.service_level_id, "origin_terminal_id": origin_terminal.terminal_id}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 5)

    def test_leg_cost_origin_terminal(self):
        service_level = baker.make(ServiceLevel)
        for i in range(5):
            origin_terminal = baker.make(Terminal)
            lane = baker.make(Lane, origin_terminal=origin_terminal)
            leg_cost = baker.make(
                LegCost, service_level=service_level, lane=lane)

        response = self.client.get(reverse(
            'leg-cost-origin', kwargs={"service_level_id": service_level.service_level_id}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 5)

    def test_leg_cost_destination_terminal(self):
        service_level = baker.make(ServiceLevel)
        origin_terminal = baker.make(Terminal)
        for i in range(5):
            lane = baker.make(Lane, origin_terminal=origin_terminal)
            lane_cost = baker.make(
                LegCost, service_level=service_level, lane=lane)

        response = self.client.get(reverse(
            'leg-cost-destination', kwargs={"service_level_id": service_level.service_level_id, "origin_terminal_id": origin_terminal.terminal_id}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 5)

    def test_weight_break_header_create(self):
        service_level = baker.make(ServiceLevel)
        unit = baker.make(Unit)
        unit_json = UnitSerializer(unit).data
        weight_break_header = baker.prepare(
            WeightBreakHeader, levels=str(random.randint(0, 9999)), service_level=service_level)

        payload = WeightBreakHeaderSerializer(weight_break_header).data
        payload["unit"] = {k: v for k, v in unit_json.items() if k in (
            "unit_name", "unit_symbol", "unit_type")}

        response = self.client.post(
            reverse('weight-break-header-list'), payload, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["levels"], weight_break_header.levels)
        self.assertEqual(Unit.objects.filter(
            **response.data["unit"]).first().pk, unit.pk)

        service_level = baker.make(ServiceLevel)
        weight_break_header = baker.prepare(
            WeightBreakHeader, levels=str(random.randint(0, 9999)), service_level=service_level)

        payload = WeightBreakHeaderSerializer(weight_break_header).data
        unit = baker.prepare(Unit)

        payload["unit"] = {"unit_name": unit.unit_name,
                           "unit_symbol": unit.unit_symbol, "unit_type": unit.unit_type}

        self.assertFalse(Unit.objects.filter(**payload["unit"]).exists())

        response = self.client.post(
            reverse('weight-break-header-list'), payload, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["levels"], weight_break_header.levels)
        self.assertTrue(Unit.objects.filter(**payload["unit"]).exists())

    def test_weight_break_header_batch_update(self):
        weight_break_header = baker.make(
            WeightBreakHeader, levels=json.dumps({"test": 0}))
        payload = []
        for i in range(5):
            weight_break_header.levels = json.dumps({"test": i})
            payload.append(WeightBreakHeaderSerializer(
                weight_break_header).data)

        response = self.client.put(
            reverse('weight-break-header-batch-update'), payload, format='json')
        weight_break_header = WeightBreakHeader.objects.get(
            weight_break_header_id=weight_break_header.weight_break_header_id)

        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(json.loads(weight_break_header.levels)["test"], 0)
        self.assertEqual(json.loads(weight_break_header.levels)["test"], 4)

        payload = [WeightBreakHeaderSerializer(
            weight_break_header).data for i in range(2)]
        del payload[0]["weight_break_header_id"]

        response = self.client.put(
            reverse('weight-break-header-batch-update'), payload, format='json')

        self.assertEqual(response.status_code, 400)

    def test_weight_break_header_batch_create_update(self):
        weight_break_header = baker.make(
            WeightBreakHeader, levels=json.dumps({"test": 0}))
        payload = []
        for i in range(5):
            weight_break_header.levels = json.dumps({"test": i})
            payload.append(WeightBreakHeaderSerializer(
                weight_break_header).data)

        response = self.client.post(
            reverse('weight-break-header-batch-create-update'), payload, format='json')
        weight_break_header = WeightBreakHeader.objects.get(
            weight_break_header_id=weight_break_header.weight_break_header_id)

        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(json.loads(weight_break_header.levels)["test"], 0)
        self.assertEqual(json.loads(weight_break_header.levels)["test"], 4)

        payload = [WeightBreakHeaderSerializer(
            weight_break_header).data for i in range(2)]
        del payload[0]["weight_break_header_id"]

        response = self.client.post(
            reverse('weight-break-header-batch-create-update'), payload, format='json')

        self.assertEqual(response.status_code, 400)

    def test_weight_break_header_detail_panel(self):
        weight_break_header = baker.make(WeightBreakHeader, levels="{}")

        for i in range(5):
            weight_break_header.save()

        response = self.client.get(reverse(
            'weight-break-header-panel', kwargs={"weight_break_header_id": weight_break_header.weight_break_header_id}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["weight_break_header_id"], weight_break_header.weight_break_header_id)
