import json
import logging
from rest_framework.response import Response
from pac.helpers.connections import pyodbc_connection
from core.schemas import DashboardRequestSchema, buildFilterSchema
from core.app_view import AppView


class PickupDeliveryView(AppView):
    PRIMARY_TABLE = 'dbo.BrokerContractCost'
    PRIMARY_KEY = 'bcc.BrokerContractCostID'
    AUDIT_COLUMNS = ['Cost', 'TerminalVersionID', 'SubServiceLevelVersionID']
    AUDIT_VALUES = ['Cost', 'TerminalID', 'SubServiceLevelID']
    COLUMN_MAPPING = {
        "TerminalCode": {"filterType": "textFilters", "sortColumn": 'T.TerminalCode', "filter": " AND T.TerminalCode LIKE '%{0}%' "},
        "RegionCode": {"filterType": "textFilters","sortColumn": 'R.RegionCode', "filter": " AND R.RegionCode LIKE '%{0}%' "},
        "StatusID": {"filterType": "idFilters", "sortColumn": 'bcc.IsActive',
            "filter": """ AND (CASE WHEN bcc.IsInactiveViewable = 0 THEN 3 ELSE CASE WHEN bcc.IsActive = 0 THEN 2 ELSE 1 END
                END) IN ({0}) """},
        "SubServiceLevelID": {"filterType": "idFilters", "sortColumn": '',
                                         "filter": """ AND bcc.SubServiceLevelID IN ({0}) """},
        "SubServiceLevelCode": {"filterType": "sortOnly", "sortColumn": "ssl.SubServiceLevelCode"},
        "UpdatedOn": {"sortColumn": "bcch.UpdatedOn", "filter": " "},
    }

    schema = buildFilterSchema(COLUMN_MAPPING)
    GET_FILTERED_QUERY = """{{opening_clause}}
    SELECT bcc.*, bcch.UpdatedOn, ssl.SubServiceLevelCode, sl.ServiceOfferingID,
        T.TerminalCode, T.TerminalName, C.CityName, R.RegionName, R.RegionCode, co.CountryName,
        CASE WHEN bcc.IsInactiveViewable = 0 THEN 'Deleted'
            ELSE CASE WHEN bcc.IsActive = 0 THEN 'Disabled' ELSE 'Enabled' END
        END AS Status
        FROM dbo.BrokerContractCost bcc
        INNER JOIN dbo.BrokerContractCost_History bcch ON bcch.BrokerContractCostID = bcc.BrokerContractCostID
            AND bcch.IsLatestVersion = 1
        INNER JOIN dbo.SubServiceLevel ssl ON ssl.SubServiceLevelID = bcc.SubServiceLevelID
        INNER JOIN dbo.ServiceLevel sl ON sl.ServiceLevelID = SSL.ServiceLevelID
        INNER JOIN dbo.Terminal t ON t.TerminalID = bcc.TerminalID
        INNER JOIN dbo.City c ON c.CityID = t.CityID
        INNER JOIN dbo.Region r ON r.RegionID = t.RegionID
        INNER JOIN dbo.Country co ON co.CountryID = r.CountryID
        WHERE bcc.IsInactiveViewable = 1 AND sl.ServiceOfferingID = {service_offering_id}
        {{where_clauses}}
        {{sort_clause}}
        {{page_clause}}
        {{closing_clause}}"""

    UPDATE_FIELDS = [{'fieldName': 'Cost', 'type': 'string'} ]
    INSERT_FIELDS = [
        {'fieldName': 'TerminalID', 'type': 'number'},
        {'fieldName': 'SubServiceLevelID', 'type': 'number'},
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
                values = row.get('data')
                costs = {}
                for fieldName in data:
                    costs[fieldName] = data.get(fieldName)
                row['data'] = {'Cost': json.dumps(costs)}
        data['records'] = update_rows
        return data
