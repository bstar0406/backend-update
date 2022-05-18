import json
import logging
from rest_framework import generics, mixins, status, views, viewsets
from rest_framework.response import Response
from pac.helpers.connections import pyodbc_connection
import pac.pre_costing.queries as queries
from pac.pre_costing.line_haul_costs.lane_api import LaneAPI
from core.schemas import DashboardRequestSchema, buildFilterSchema
from core.app_view import AppView

# updating rows of LineHaul Lane Costs
class LaneCostsAPI(AppView):
    PRIMARY_TABLE = 'dbo.LaneCost'
    PRIMARY_KEY = 'lc.LaneCostID'
    AUDIT_COLUMNS = ['Cost', 'MinimumCost', 'LaneCostID', 'LaneVersionID']
    AUDIT_VALUES = ['Cost', 'MinimumCost', 'LaneCostID', 'LaneID']
    COLUMN_MAPPING = {
        "OriginTerminalCode": {"filterType": "textFilters", "sortColumn": 'O.TerminalCode', "filter": " AND O.TerminalCode LIKE '%{0}%' "},
        "OriginProvinceCode": {"filterType": "idFilters","sortColumn": 'O.ProvinceCode', "filter": " AND O.ProvinceID IN ({0}) "},
        "OriginRegionCode": {"filterType": "idFilters","sortColumn": 'O.RegionCode', "filter": " AND O.RegionID IN ({0}) "},
        "DestinationTerminalCode": {"filterType": "textFilters", "sortColumn": 'd.TerminalCode', "filter": " AND d.TerminalCode LIKE '%{0}%' "},
        "DestinationProvinceCode": {"filterType": "idFilters","sortColumn": 'd.ProvinceCode', "filter": " AND d.ProvinceID IN ({0}) "},
        "DestinationRegionCode": {"filterType": "idFilters","sortColumn": 'd.RegionCode', "filter": " AND d.RegionID IN ({0}) "},
        "StatusID": {"filterType": "idFilters", "sortColumn": 'lc.IsActive',
            "filter": """ AND (CASE WHEN lc.IsInactiveViewable = 0 THEN 3 ELSE CASE WHEN lc.IsActive = 0 THEN 2 ELSE 1 END
                END) IN ({0}) """},
        "SubServiceLevelCode": {"filterType": "idFilters", "sortColumn": "ssl.SubServiceLevelCode",
                                         "filter": """ AND ssl.SubServiceLevelID IN ({0}) """},
        "UpdatedOn": {"sortColumn": "lch.UpdatedOn", "filter": " "}
    }
    schema = buildFilterSchema(COLUMN_MAPPING)
    GET_FILTERED_QUERY = queries.LANE_COSTS_REDUCED_DASHBOARD
    UPDATE_FIELDS = [{'fieldName': 'Cost', 'type': 'string'},
        {'fieldName': 'MinimumCost', 'type': 'number'}]
    INSERT_FIELDS = [
        {'fieldName': 'LaneID', 'type': 'number'},
        {'fieldName': 'MinimumCost', 'type': 'number'},
        {'fieldName': 'Cost', 'type': 'string'}
    ]
    def prepare_filter(self, data, kwargs):
        service_offering_id = kwargs.get("service_offering_id")
        self.GET_FILTERED_QUERY = self.GET_FILTERED_QUERY.format(service_offering_id=service_offering_id)
        return data

    def prepare_bulk_update(self, data, kwargs):
        update_rows = data.get('records')
        cleaned_rows = []
        if len(update_rows) > 0:
            for row in update_rows:
                # pack the cost values back into a JSON string
                values = row.get('data')
                costs = {}
                minimum = 0
                for fieldName in values:
                    if fieldName != 'MinimumCost':
                        costs[fieldName] = values.get(fieldName)
                    else:
                        minimum = values.get(fieldName)
                row['data'] = {'MinimumCost': minimum, 'Cost': json.dumps(costs)}
        data['records'] = update_rows
        return data

    def prepare_bulk_insert(self, data, kwargs):
        # check for duplicates first
        duplicateQuery = """SELECT count(*) FROM dbo.LaneCost WHERE LaneID = {laneId}"""
        laneExistsQuery = """SELECT L.LaneID
                            FROM dbo.Lane L
                            WHERE L.DestinationTerminalID = {dId} AND L.OriginTerminalID = {oId}
                            AND L.SubServiceLevelID = {ssl} """
        if len(data) > 0:
            conn = pyodbc_connection() # get a connection and start a transaction in case multiple operations are needed
            self.conn = conn
            for row in data:
                laneExistsQuery = laneExistsQuery.format(
                                    dId=row.get('DestinationTerminalID'),
                                    oId=row.get('OriginTerminalID'),
                                    ssl=row.get('SubServiceLevelID'))
                cursor = conn.cursor()
                cursor.execute(laneExistsQuery)
                get_lane_id = cursor.fetchone()
                lane_id = get_lane_id[0] if get_lane_id else None
                if lane_id is None: # add the lane
                    new_lane = LaneAPI()
                    new_lane.conn = conn
                    got_lane_ids = new_lane.bulk_insert([row], kwargs)
                    new_lane_id = -1
                    if got_lane_ids is not None:
                        new_lane_id = int(got_lane_ids[0])
                        row['LaneID'] = new_lane_id # add the new LaneID
                    else:
                        return None
                else:
                    row['LaneID'] =lane_id # add the existing LaneID

                duplicateQuery = duplicateQuery.format(laneId = row.get('LaneID'))
                cursor.execute(duplicateQuery)
                countValue = (cursor.fetchone())[0]
                if countValue is not None and countValue > 0: # laneCost already exists, so fail out
                    logging.error(f"Attempted to create duplicate LaneCost on Lane: {row.get('LaneID')}")
                    return f"Attempted to create duplicate LaneCost on Lane: {row.get('LaneID')}"
                else: # clean up the row
                    row['Cost'] = json.dumps({}) # if not a duplicate, add in the default costs
                    row['MinimumCost'] = 0

        return data

# updating rows of LineHaul leg Costs
class LegCostsAPI(AppView):
    PRIMARY_TABLE = 'dbo.LegCost'
    PRIMARY_KEY = 'lc.LegCostID'
    AUDIT_COLUMNS = ['Cost', 'LaneVersionID', 'LegCostID', 'ServiceModeVersionID']
    AUDIT_VALUES = ['Cost', 'LaneID', 'LegCostID', 'ServiceModeID']
    COLUMN_MAPPING = {
        "OriginTerminalCode": {"filterType": "textFilters", "sortColumn": 'O.TerminalCode', "filter": " AND O.TerminalCode LIKE '%{0}%' "},
        "OriginProvinceCode": {"filterType": "idFilters","sortColumn": 'O.ProvinceCode', "filter": " AND O.ProvinceID IN ({0}) "},
        "OriginRegionCode": {"filterType": "idFilters","sortColumn": 'O.RegionCode', "filter": " AND O.RegionID IN ({0}) "},
        "DestinationTerminalCode": {"filterType": "textFilters", "sortColumn": 'd.TerminalCode', "filter": " AND d.TerminalCode LIKE '%{0}%' "},
        "DestinationProvinceCode": {"filterType": "idFilters","sortColumn": 'd.ProvinceCode', "filter": " AND d.ProvinceID IN ({0}) "},
        "DestinationRegionCode": {"filterType": "idFilters","sortColumn": 'd.RegionCode', "filter": " AND d.RegionID IN ({0}) "},
        "StatusID": {"filterType": "idFilters", "sortColumn": 'lc.IsActive',
            "filter": """ AND (CASE WHEN lc.IsInactiveViewable = 0 THEN 3 ELSE CASE WHEN lc.IsActive = 0 THEN 2 ELSE 1 END
                END) IN ({0}) """},
        "SubServiceLevelCode": {"filterType": "idFilters", "sortColumn": "ssl.SubServiceLevelCode",
                                         "filter": """ AND ssl.SubServiceLevelID IN ({0}) """},
        "UpdatedOn": {"sortColumn": "lch.UpdatedOn", "filter": " "}
    }
    schema = buildFilterSchema(COLUMN_MAPPING)
    GET_FILTERED_QUERY = queries.LEG_COSTS_DASHBOARD
    UPDATE_FIELDS = [{'fieldName': 'Cost', 'type': 'string'} ]
    INSERT_FIELDS = [
        {'fieldName': 'LaneID', 'type': 'number'},
        {'fieldName': 'ServiceModeID', 'type': 'number'},
        {'fieldName': 'Cost', 'type': 'string'}
    ]

    def prepare_filter(self, data, kwargs):
        service_offering_id = kwargs.get("service_offering_id")
        self.GET_FILTERED_QUERY = self.GET_FILTERED_QUERY.format(service_offering_id=service_offering_id)
        return data

    def prepare_bulk_update(self, data, kwargs):
        update_rows = data.get('records')
        if len(update_rows) > 0:
            for row in update_rows:
                # pack the cost values back into a JSON string
                values = row.get('data')
                costs = {}
                for fieldName in values:
                        costs[fieldName] = values.get(fieldName)
                row['data'] = {'Cost': json.dumps(costs)}
        data['records'] = update_rows
        return data
