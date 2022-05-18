import json
import logging
from pac.helpers.connections import pyodbc_connection
from core.schemas import DashboardRequestSchema, buildFilterSchema
from core.app_view import AppView

# updating rows of LineHaul Lane Costs
class LaneAPI(AppView):
    PRIMARY_TABLE = 'dbo.Lane'
    PRIMARY_KEY = 'l.LaneID'
    AUDIT_COLUMNS = ['SubServiceLevelVersionID', 'OriginTerminalVersionID',
     'DestinationTerminalVersionID', 'IsHeadhaul', 'LaneID']
    AUDIT_VALUES = ['SubServiceLevelID', 'OriginTerminalID', 'DestinationTerminalID', 'IsHeadhaul', 'LaneID']
    COLUMN_MAPPING = { }

    UPDATE_FIELDS = [{'fieldName': 'IsHeadhaul', 'type': 'number'},]
    INSERT_FIELDS = [
        {'fieldName': 'SubServiceLevelID', 'type': 'number'},
        {'fieldName': 'OriginTerminalID', 'type': 'number'},
        {'fieldName': 'DestinationTerminalID', 'type': 'number'},
        {'fieldName': 'IsHeadhaul', 'type': 'number'},
    ]


