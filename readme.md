# Request 

### Get Request Header
- **Endpoint:** /api/request/header/<str:request_number>/
- **Method: GET**

### Get Request Header's Historical Version
- **Endpoint:** /api/request/header/<str:request_number>/history/<int:version_num>/
- **Method: GET**

### Revert to a Historical Version
- **Endpoint:** /api/request/<int:request_id>/revert/<int:version_num>/<br/>
- **Method: PUT**

### Request Editor Rights
- **Endpoint:** /api/requesteditor/
- **Method: POST**
- **Payload:**
```json
    {
    "request_number": String (Required),
    }
```
- **Description:** 
  - A Notification will be created for the user who has editor rights for the Request with given `request_number`. The message field of the Notification will be a JSON object of the following format: 
  
  ```json
    {
        "message": f"{user_instance.user_name} has requested Editor Rights of RRF {request_instance.request_code}. Please ensure that you have saved your work before clicking 'Approve' as any unsaved changes made will be lost.",
        "args": {
            "endpoint": f"requesteditor/update/{request_instance.request_id}/",
            "request_id": request_instance.request_id,
            "actions": [
                {
                    "text": "Approve",
                    "payload": {
                        "action": "Approve",
                        "current_editor": user_instance.user_id
                    },
                    "alert": {
                        "alert_name": "requestApproved",
                        "alert_data": request_instance.request_number
                    }
                },
                {
                    "text": "Decline",
                    "payload": {
                        "action": "Decline",
                        "current_editor": user_instance.user_id
                    },
                    "alert": {
                        "alert_name": "requestDeclined",
                        "alert_data": request_instance.request_number
                    }
                }
            ]
        }
    }
    ```
    
  - Call `endpoint` api/requesteditor/update/{request_id}/ as described below with `payload` depending on front-end user action "Approve" or "Decline".

### Update Request Editor Rights
- **Endpoint:** /api/requesteditor/update/{request_id}/
- **Method: PUT**
- **Payload:**
```json
    {
    "action": "Approve" or "Decline" (Required),
    "current_editor": ID (Required),
    }
```

# Request Profile

### Get Request Profile
- **Endpoint:** /api/requestprofile/<str:request_number>/
- **Method: GET**

### Get Request Profile's Historical Version
- **Endpoint:** /api/requestprofile/<str:request_number>/history/<int:version_num>/
- **Method: GET**

# Request Lane

## Request Section

### Creating/Updating Request Section
- **Endpoint:**/api/requestsection/<br/>
- **Method: PUT<br/>**
- **Notes**
    - The payload should include an object "request_sections", which is an array of the request_sections to be created or updated.
    - If each element of the array includes a request_section_id, then the request_section will be updated, otherwise,a new request_section will be creted.
    - If there is an update to a request section that invalidates the existing request_section_lanes' costs, the corresponding request_section's object must include a flag "key_field_changed", set to True, which will trigger clearing out the costs for all request_section_lanes belong to that request_section. 


### Duplicating Request Section
- **Endpoint:**/api/requestsection/<br/>
- **Method: PUT<br/>**
- **Returns** If adding lanes from the source-request-section to the destination-request-section, results in having identical or duplicate lanes, the endpoint will return "identical_lanes_not added" and "duplicate_lanes_added", the same objects returned by /api/requestsectionlane/create/, see details below.
- **Notes**
    - The same endpoint to update the request-section fields.
    - For duplicating sections, the payload must include an object "duplicate_request_sections", which is an array of [{source_section_id: .., destination_section_id: ..}] 
    - The payload must also include the "request_lane_id" associated with the source/destination sections.


## Request Section Lane

### Creating Request Section Lane 
- **Endpoint:** /api/requestsectionlane/create/<br/>
- **Method: POST<br/>**
- **Returns** A list of "identical_lanes_not added", which include the list of lanes that exactly match an origin-destination lane that is already exist in the same section. Also, a list of "duplicate_lanes_added", which shares the same basing-point with one of the existing lanes in the given section.<br/>
- **Parameters**
    - request_section_id
    - orig_group_type_id
    - orig_group_id
    - orig_point_type_id
    - orig_point_id
    - dest_group_type_id
    - dest_group_id
    - dest_point_type_id
    - dest_point_id
    - is_between

### Search Request Section Lane Points
- **Endpoint:** /api/requestsectionlane/search/points/<str:group_type>/<int:group_id>/<str:point_type>/<str:point_name>/<br/>
- **Method: GET<br/>**
- **Returns** An array with `point_id` and `point_name` fields <br/>
- **Notes**
    - group_type and point_type should be one of the point-type levels (Country, Region, Province, Terminal, Basing Point, Service Point, Postal Code)
    - group_type, point_type, and point_name should be surrounded by '' since the url is expecting strings.
    - The point_name can be an empty string '', in such case, the endpoint will retrun all points.
    - The endpoint searches for the TOP 100 matches, when the point_name is empty, it returns all the points regardless of the results count.

### Search Postal Codes based on a Request Section Lane
- **Endpoint:** /api/requestsectionlane/pricingpoint/search/origin/<int:request_section_lane_id>/<str:postal_code>/<br/>
- **Endpoint:** /api/requestsectionlane/pricingpoint/search/destination/<int:request_section_lane_id>/<str:postal_code>/<br/>
- **Method: GET<br/>**
- **Returns** Top 100 matches the postal-code string specified in the url <br/>


### Get Location Tree for a Given Request Section ID
- **Endpoint:** /api/requestsectionlane/<int:request_section_id>/<str:orig_type>/<int:orig_id>/<str:dest_type>/<int:dest_id>/<str:lane_status>/locationtree/<br/>
- **Endpoint to fetch the Staging Table:** /api/requestsectionlane/staging/<int:request_section_id>/<str:orig_type>/<int:orig_id>/<str:dest_type>/<int:dest_id>/<str:lane_status>/locationtree/<br/>
- **Method: GET**
- **Parameters:**
    - orig_type and dest_type should be one of the point-type levels (Country, Region, Province, Terminal, Basing Point, Service Point, Postal Code, Point Type) or None
    - lane_status should be New, Changed, Duplicated, DoNotMeetCommitment, or None
    - orig_type, dest_type, and lane_status, should be surrounded by '' since the url is expecting strings.
- **Returns** A payload with `orig` and `dest` fields, each of which includes multiple arrays of 
    - `countries`, 
    - `provinces`, 
    - `regions`, 
    - `basing-points`, 
    - `service-points`, 
    - `terminals`, 
    - `postal-codes`,
    - `zones`, and
    - `point-types`.


### Updating Request Section Lane
- **Endpoint:** /api/requestsectionlane/update/<br/>
- **Method: PUT<br/>**
- **Notes**
    - The payload must include the following `mandatory` parameters:
        - `request_section_id`
        - `orig_type`: if there is a filter applied on the origin level (value must be Country, Region, Province, Terminal, Basing Point, Service Point, or Postal Code), otherwise, it should be None.
        - `orig_id`: if there is a filter applied on the origin level
        - `dest_type`: and dest_id: same as orig_type and orig_id
        - `dest_id`: if there is a filter applied on the destination level
        - `lane_status`: should be New, Changed, Duplicated, DoNotMeetCommitment, or None
        - **new** `table_name`: the name of the sub table i.e. customer_rates, customer_discount, dandr_rates, etc
        - `request_section_lanes`: an optional string of array, that includes the id(s) of different request_section_lane_id(s) if the user selects specific rows to apply the update. If specified it must be in the format of a string as "[1, 2, 3, ..]"
        - **new** when the request_section_lanes belong to a table where only pricing points have costs/discounts
        then the updates apply to all pricing points under the lane 
        - **new** `pricing_points`: an optional string of array, that includes the id(s) of different pricing_point_id(s) if the user selects specific rows to apply the update. If specified it must be in the format of a string as "[1, 2, 3, ..]"
        - **new** if no `request_section_lanes` and no `pricing_points` are included then the update is applied to 
        either all lanes or all pricing points (within the filter parameters), depending on the table name.
- **To Update is_between or the cost fields**
    - `weight_break_lower_bound`: expected value is a string of array of lower bounds, e.g.,  "[0, 1000, 5000]"
    - `context_id`: this is a GUID, char(32), parameter that identifies the user context. Once the user starts to edit, the front-end will generate a GUID and send it along the parameters below to specify the edits. The same context_id should be sent with all subsequent edits until the user either applies a micro_save (by switching to a different tab) or a macro_save (by clicking the save button). If neither a micro_save nor a macro_save, then the changes will eventually be discarded.
    - `is_between`: only if a request_section_lane's is_between flag is changed true/false.
    - `operation`: only if the cost of a request_section_lane is changed. Value must be one of the following ('+', '-', '*', '/', '=').
    - `multiplier`: it is an optional parameter, but must be specified when operation is specified. It accepts a decimal(19,6) value. If a user changes a percentage, then the multiplier should be adjusted, for example a 3 % increase, should be translated to (operation: *, multiplier: 1.03).
    - `rate_table`: the name of the rate table to be updated. Value must be one od the following (commitment, customer_rate, customer_discount, dr_rate, partner_rate, partner_discount, profitability, margin, density, pickup_cost, delivery_cost, accessorials_value, accessorials_percentage, pickup_count, delivery_count, dock_adjustment). When the value is pickup_count, delivery_count, or dock_adjustment, the weight-break can be null.   
    - `micro_save`: true/false to trigger a macro version save 
    - `macro_save`: true/false to trigger a macro version save 

  **To Duplicate/Transfer a set of Lanes**
    - `is_move`: true when transfering a lane to another section, false if only duplicating a lane.
    - `destination_request_section_id` which identifies the destination request_section_id.  
 
- **To Delete a set of Lanes**
    - `is_active`: set to false to delete the specified set of lanes.

### Query Lanes with Pagination
- **Endpoint:** /api/requestsectionlane/?<str:field_1_name>=<field_2_value>&<str:field_2_name>=<field_2_value>%...<br/>
- **Method: GET<br/>**
- **Fields:** ['page', 'page_size', 'ordering','request_section_id', 'origin_province_id', 'origin_region_id', 'origin_country_id', 'origin_terminal_id', 'origin_zone_id', 'origin_basing_point_id', 'origin_city_id', 'origin_postal_code_id', 'destination_province_id',
 'destination_region_id', 'destination_country_id', 'destination_terminal_id', 'destination_zone_id', 'destination_basing_point_id', 'destination_city_id', 'is_published', 'is_edited', 'is_duplicate', 'is_between']<br/>
- **Example Endpoint:** /api/requestsectionlane/?page=1&page_size=100&request_section_id=1&origin_province_id__isnull=true&ordering=destination_postal_code_name<br/>
- **Notes:** All endpoints starting with 'destination_' or 'origin_' also have an equivalent field ending with '__isnull' that takes a Boolean value to check whether their value is Null. As an example 'origin_provice_id' has a corresponding field called 'origin_province_id__isnull' which will filter by Null values for the 'origin_province_id'<br/>
- **Ordering Fields:** These are field values that will be passed to the 'ordering' field in order to sort the results<br/> 
['origin_province_code', 'origin_region_code', 'origin_country_code', 'origin_terminal_code', 'origin_zone_name', 'origin_basing_point_name', 'origin_city_name', 'origin_postal_code_name',
 'destination_province_code', 'destination_region_code', 'destination_country_code', 'destination_terminal_code', 'destination_zone_name', 'destination_basing_point_name', 'destination_city_name', 'destination_postal_code_name']


### Viewing Request Section Lane interim changes
- **Endpoint:** /api/requestsectionlane/staging/<br/>
- **Method: GET<br/>**
- **Notes: <br/>** will work exactly similar to the pagination endpoint described above. The only difference is that the request-section-lanes data in this table is temporarily stored. To fetch the changes, filter the table for specific `request_section_id`, `context_id`, and `is_updated` = True


### Viewing Request Section Lane History
- **Endpoint:** /api/requestsectionlane/<str:request_number>/history/<int:version_num>/<br/>
- **Method: GET<br/>**
- **Notes: <br/>** will work exactly similar to the pagination endpoint described above. The only difference is that the url takes two additional parameters; the request-number, and the `macro-version-number` of the request. All other filters will work similar to the pagination endpoint.


### Reading Request Section Lane changes Count
- **Endpoint:** /api/requestsectionlane/staging/count/<int:request_section_id>/<str:context_id>/<br/>
- **Method: GET<br/>**


## Request Section Lane - Pricing Point

### Creating Request Section Lane Pricing Point
- **Endpoint:** /api/requestsectionlane/pricingpoint/create/<br/>
- **Method: POST<br/>**
- **Parameters** A "pricing_points" object which includes an array, each element in the array must include
    - request_section_lane_id
    - origin_postal_code_id
    - destination_postal_code_id

### Get Request Section Lane Pricing Point
- **Endpoint:** /api/requestsectionlane/pricingpoint/<int:request_section_lane_id>/<br/>
- **Method: GET<br/>**
- **Returns** All `active` "pricing_points" within the given `request_section_lane_id`.

### Get Request Section Lane Pricing Point History
- **Endpoint:** /api/requestsectionlane/pricingpoint/<int:request_section_lane_id>/history/<int:version_num>/<br/>
- **Method: GET<br/>**
- **Returns** All `active` "pricing_points" within the given `request_section_lane_id` and `macro-version-number`.

### Get Request Section Lane Pricing Point Staging Table
- **Endpoint:** /api/requestsectionlane/pricingpoint/<int:request_section_lane_id>/staging/<str:context_id>/<br/>
- **Method: GET<br/>**
- **Returns** All `active` "pricing_points" within the given `request_section_lane_id` and `macro-version-number`.

### Copying/Moving/Deleting Request Section Lane Pricing Point
- **Endpoint:** /api/requestsectionlane/pricingpoint/update/<br/>
- **Method: PUT<br/>**
- **Mandatory Parameters** 
    - `request_section_lane_id`: the source request_section_lane_id 
    - `request_section_lane_pricing_points`: a string represents an array of id(s) of pricing-points to be copied or moved. If an empty array '[]', the action will apply to all pricing-points in the source request_section_lane_id

- **Copying/Moving** 
    - `destination_request_section_id`
    - `destination_request_section_lane_id`
    - `is_move`: false for copy, and true fro move.

- **Deleting** 
    - `is_active`: falsee

### Updating rates of Request Section Lane Pricing Point
- **Endpoint:** /api/requestsectionlane/pricingpoint/update/rate/<br/>
- **Method: PUT<br/>**
- **Parameters** 
    - all parameters sent to the requestsectionlane/update endpoint. Except the followin two differences: 
    - it does not accept `is_between` parameter.
    - it accepts an additional parameter, `request_section_lane_pricing_points`, to specify the list of pricing-point id(s) as string of an array of id(s). 

### Find Valid Destination Lane-Group for a Pricing Point
- **Endpoint:** /api/requestsectionlane/pricingpoint/destination/<int:request_section_lane_priring_point_id>/<int:destination_request_section_id>/
 **Method: GET<br/>**


# Notification

### Get Unread Notifications For User
- **Endpoint:** /api/notification/<int:user_id>/
- **Method: GET**

### Batch Update Notifications
- **Endpoint:** /api/notification/batch-update/
- **Method: PATCH**
- **Payload:**
```json
[
    {
    "notification_id": ID,
    "is_read": Boolean,
    "is_inactive_viewable": Boolean,
    "is_active": Boolean
    }, ...
]
```

# Dashboard

### Get Dashboard Header
- **Endpoint:** /api/dashboard/header/
- **Method: GET**

### Get Dashboard
- **Endpoint:** /api/dashboard/
- **Method: GET**

# User Management

### Get Users
- **Endpoint:** /api/user/
- **Method: GET**

### Update User
- **Endpoint:** /api/user/<int:<user_id>/
- **Method**
  - **PATCH:** ***Partial Payload***
  - **PUT:** ***Full Payload***
- **Payload:**
```json
    {
    "is_active": Boolean,
    "is_away": Boolean,
    "has_self_reassign": Boolean,
    "persona": ID,
    "user_manager": ID,
    "service_levels": [
        {
            "service_level_id": ID
        },...
    ]
    }
```
- **NOTE:** If sending data for the ```"service_levels"``` field, send all associated ServiceLevel objects. The endpoint will handle deleting unincluded objects and creating new objects.

# Workflow

### Workflow Manager
- **Endpoint:** /api/workflow/
- **Method: POST**
- **Payload:**
```json
    {
    "request_id": ID (Required),
    "current_request_status_type_id": ID (Optional),
    "next_request_status_type_id": ID (Optional),
    "secondary_pending_drm": Boolean (Optional),
    "secondary_pending_pcr": Boolean (Optional),
    "secondary_pending_pc": Boolean (Optional),
    "secondary_pending_ept": Boolean (Optional),
    }
```
- **Description:** 
  - Field ```"current_request_status_type_id"``` will complete all RequestQueue objects associated with the Request and RequestStatusType, and ```"current_request_status_type_id"``` will create new RequestQueue objects associated with the Request and RequestStatusType. Both fields are optional, however sending neither will result in no action.
  - Optionally sending boolean ```True``` values for any of the fields starting with ```"secondary_"``` will initiate secondary workflow RequestQueue objects. The endpoint will NOT error handle if there is already an open secondary workflow of the given type. **These fields should only be used for the screens where the workflow is initiated.**

  