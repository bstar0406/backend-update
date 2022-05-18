import logging
import copy

def buildFilterSchema (columnMapping):
    idNames = []
    textIdNames = []
    textNames = []
    for columnName in columnMapping:
        column = columnMapping.get(columnName)
        if column.get('filterType') == 'idFilters':
            idNames.append(columnName)
        if column.get('filterType') == 'textIdFilters':
            textIdNames.append(columnName)
        if column.get('filterType') == 'textFilters':
            textNames.append(columnName)
    tempSchema = copy.deepcopy(DashboardRequestSchema)
    tempSchema.get('properties').get('idFilters').get('items').get('properties').get('fieldName').update({'enum': idNames})
    tempSchema.get('properties').get('textIdFilters').get('items').get('properties').get('fieldName').update({'enum': textIdNames})
    tempSchema.get('properties').get('textFilters').get('items').get('properties').get('fieldName').update({'enum': textNames})
    return tempSchema

def buildUpdateSchema (columns):
    tempSchema = copy.deepcopy(BulkUpdateSchema)
    for column in columns:
        if column['type'] == 'string':
            tempSchema.get('records').get('items').get('properties').get('data').get('properties').update({column['fieldName']: {"type": "string"} })
        else:
            tempSchema.get('records').get('items').get('properties').get('data').get('properties').update({column['fieldName']: {"type": "number"} })
    return tempSchema
    #TODO: apply required fields to the schema as well

def buildInsertSchema (columns):
    tempSchema = copy.deepcopy(BulkInsertSchema)
    for column in columns:
        if column['type'] == 'string':
            tempSchema.get('items').get('properties').get('data').get('properties').update({column['fieldName']: {"type": "string"} })
        else:
            tempSchema.get('items').get('properties').get('data').get('properties').update({column['fieldName']: {"type": "number"} })
    return tempSchema

DashboardRequestSchema = {
    "type": "object",
    "properties": {
        "idFilters": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "fieldName": {"type": "string", "enum":
                        ["customer_name", "service_level_code", "sales_representative_name", "pricing_analyst_name",
                        "business_type_name", "request_status_type_name", "priority", "approvals_completed"]},
                    "ids": {"type": "array", "items": {"type": "number"} }
                }
            }
        },
        "textIdFilters": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "fieldName": {"type": "string", "enum":
                        ["customer_name", "business_type_name", "sales_representative_name", "pricing_analyst_name",
                        "business_type_name", "request_status_type_name"]},
                    "ids": {"type": "array", "items": {"type": "string"} }
                }
            }
        },
        "textFilters": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "fieldName": {"type": "string", "enum": ["request_code", "account_number"]},
                    "filterText": {"type": "string"}
                }
            }
        },
        "sort": {
            "type": "object",
            "properties": {
                "sortField": {"type": "string"},
                "sortDirection": {"type": "string", "enum": ["ASC", "DESC"]},
            }
        },
        "pageNumber": {"type": "number"},
        "pageSize": {"type": "number"},
        "totalRows": {"type": "number"},
    },
    "required": ["sort", "pageNumber", "pageSize"]
}

BulkUpdateSchema = {
    "records": {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "id": {"type": "number"},
                "idField": {"type": "string"},
                "data": {"type": "object", "properties": {} }
             }
        }
    }
}
BulkInsertSchema = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "data": {"type": "object", "properties": {} }
         }
    }
}
