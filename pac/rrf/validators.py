import json

from pac.helpers.connections import pyodbc_connection
from pac.models import Country, Region, ServicePoint, Province, Terminal, BasingPoint, PostalCode
from pac.rrf import queries
from pac.rrf.models import RequestSectionLanePointType, RequestSectionLanePricingPoint, RequestSection, \
    RequestSectionLane
from pac.rrf.utils import str2bool, to_int


def none_save_join(current_value, new_value):
    current_value = new_value if current_value is None else current_value.join(new_value)
    return current_value


def is_empty(value):
    if value is None or str(value).strip() == "":
        return True
    return False


def check_l001(lane, **kwargs):
    # Column headers or order do not align to P&C Template
    error_message = 'calling check 001'
    # entity.status_message = none_save_join(entity.status_message, error_message)
    pass


# L002: Blank Rows +
def check_l002(lane, **kwargs):
    # Blank Rows
    if is_empty(lane.request_section_id) or is_empty(lane.origin_point_code) or is_empty(
            lane.destination_point_code):
        lane.status_message["L002"] = 'Blank Row Ignored'
        lane.uni_status = 'INVALID'


# L003: Incorrect RequestSectionID +
def check_l003(lane, **kwargs):
    file = kwargs["file"]
    if not is_empty(lane.request_section_id) and file is not None:
        if file.request_section_id != lane.request_section_id:
            lane.status_message["L003"] = 'Incorrect RequestSectionID'
            lane.uni_status = 'INVALID'


# L004 - No validations required as not uploaded into DB - as per stated in FRD
def check_l004(lane, **kwargs):
    # no description for L004 found in FRD
    pass


# L005: Incorrect RequestSectionLaneID
def check_l005(lane, **kwargs):
    if lane.request_section_lane_id and not RequestSectionLane.objects.filter(
            request_section_lane_id=to_int(lane.request_section_lane_id)).exists():
        lane.status_message["L005"] = 'Incorrect RequestSectionLaneID'
        lane.uni_status = 'INVALID'


# L006: Incorrect OriginGroupTypeName -
def check_l006(lane, **kwargs):
    origin_group_type_name = lane.origin_group_type_name

    if RequestSectionLanePointType.objects.filter(
            request_section_lane_point_type_name=origin_group_type_name, is_group_type=True).first() is None:
        lane.status_message["L006"] = 'Incorrect OriginGroupTypeName'
        lane.uni_status = 'INVALID'


# L007: Incorrect OriginGroupCode
def check_l007(lane, **kwargs):
    origin_group_type_name = lane.origin_group_type_name
    origin_group_code = lane.origin_group_code
    is_invalid = False

    if origin_group_type_name == 'Country':
        if Country.objects.filter(country_code=origin_group_code).count() == 0:
            is_invalid = True
    elif origin_group_type_name == 'Region':
        if Region.objects.filter(region_code=origin_group_code).count() == 0:
            is_invalid = True
    elif origin_group_type_name == 'Province':
        if Province.objects.filter(province_code=origin_group_code).count() == 0:
            is_invalid = True

    if is_invalid:
        lane.status_message["L007"] = 'Incorrect OriginGroupCode'
        lane.uni_status = 'INVALID'


# L008: Incorrect OriginPointTypeName
def check_l008(lane, **kwargs):
    location_hierarchy = kwargs["location_hierarchy"]
    origin_point_type_name = lane.origin_point_type_name
    origin_group_type_name = lane.origin_group_type_name
    invalid_flag = False
    if origin_point_type_name and origin_group_type_name:
        origin_point_type_lh = location_hierarchy.get(origin_point_type_name, None)
        origin_group_type_lh = location_hierarchy.get(origin_group_type_name, None)
        if origin_point_type_lh is None or origin_group_type_lh is None:
            invalid_flag = True
        else:
            if RequestSectionLanePointType.objects.filter(
                    request_section_lane_point_type_name=origin_point_type_name,
                    is_point_type=True).first() is None or origin_point_type_lh < origin_group_type_lh:
                invalid_flag = True
    else:
        invalid_flag = True

    if invalid_flag:
        lane.status_message["L008"] = 'Incorrect OriginPointTypeName'
        lane.uni_status = 'INVALID'


# L009: Incorrect OriginPointCode
def check_l009(lane, **kwargs):
    origin_point_type_name = lane.origin_point_type_name
    origin_point_code = lane.origin_point_code
    is_invalid = False

    if origin_point_type_name == 'Country':
        if Country.objects.filter(country_code=origin_point_code).count() == 0:
            is_invalid = True
    elif origin_point_type_name == 'Region':
        if Region.objects.filter(region_code=origin_point_code).count() == 0:
            is_invalid = True
    elif origin_point_type_name == 'Province':
        if Province.objects.filter(province_code=origin_point_code).count() == 0:
            is_invalid = True
    elif origin_point_type_name == 'Terminal':
        if Terminal.objects.filter(terminal_code=origin_point_code).count() == 0:
            is_invalid = True
    elif origin_point_type_name == 'Basing Point':
        if BasingPoint.objects.filter(basing_point_name=origin_point_code).count() == 0:
            is_invalid = True
    elif origin_point_type_name == 'Service Point':
        if ServicePoint.objects.filter(service_point_name=origin_point_code).count() == 0:
            is_invalid = True
    elif origin_point_type_name == 'Postal Code':
        if PostalCode.objects.filter(postal_code_name=origin_point_code).count() == 0:
            is_invalid = True

    if is_invalid:
        lane.status_message["L009"] = 'Incorrect OriginPointCode'
        lane.uni_status = 'INVALID'


# L010: Incorrect DestinationGroupTypeName
def check_l010(lane, **kwargs):
    destination_group_type_name = lane.destination_group_type_name

    if RequestSectionLanePointType.objects.filter(
            request_section_lane_point_type_name=destination_group_type_name, is_group_type=True).first() is None:
        lane.status_message["L010"] = 'Incorrect DestinationGroupTypeName'
        lane.uni_status = 'INVALID'


# L011: Incorrect DestinationGroupCode
def check_l011(lane, **kwargs):
    destination_group_type_name = lane.destination_group_type_name
    destination_group_code = lane.destination_group_code
    is_invalid = False

    if destination_group_type_name == 'Country':
        if Country.objects.filter(country_code=destination_group_code).count() == 0:
            is_invalid = True
    elif destination_group_type_name == 'Region':
        if Region.objects.filter(region_code=destination_group_code).count() == 0:
            is_invalid = True
    elif destination_group_type_name == 'Province':
        if Province.objects.filter(province_code=destination_group_code).count() == 0:
            is_invalid = True

    if is_invalid:
        lane.status_message["L011"] = 'Incorrect  DestinationPointTypeName'
        lane.uni_status = 'INVALID'


# L012: Incorrect DestinationPointTypeName
def check_l012(lane, **kwargs):
    invalid_flag = False
    location_hierarchy = kwargs["location_hierarchy"]

    destination_point_type_name = lane.destination_point_type_name
    destination_group_type_name = lane.destination_group_type_name

    if destination_point_type_name and destination_group_type_name:

        destination_point_type_lh = location_hierarchy.get(destination_point_type_name, None)
        destination_group_type_lh = location_hierarchy.get(destination_group_type_name, None)
        if destination_point_type_lh is None or destination_group_type_lh is None:
            invalid_flag = True
        else:
            if RequestSectionLanePointType.objects.filter(
                    request_section_lane_point_type_name=destination_point_type_name,
                    is_point_type=True).first() is None or destination_point_type_lh < destination_group_type_lh:
                invalid_flag = True
    else:
        invalid_flag = True
    if invalid_flag:
        lane.status_message["L012"] = 'Incorrect DestinationPointTypeName'
        lane.uni_status = 'INVALID'


# L013: Incorrect DestinationPointCode
def check_l013(lane, **kwargs):
    destination_point_type_name = lane.destination_point_type_name
    destination_point_code = lane.destination_point_code
    is_invalid = False

    if destination_point_type_name == 'Country':
        if Country.objects.filter(country_code=destination_point_code).count() == 0:
            is_invalid = True
    elif destination_point_type_name == 'Region':
        if Region.objects.filter(region_code=destination_point_code).count() == 0:
            is_invalid = True
    elif destination_point_type_name == 'Province':
        if Province.objects.filter(province_code=destination_point_code).count() == 0:
            is_invalid = True
    elif destination_point_type_name == 'Terminal':
        if Terminal.objects.filter(terminal_code=destination_point_code).count() == 0:
            is_invalid = True
    elif destination_point_type_name == 'Basing Point':
        if BasingPoint.objects.filter(basing_point_name=destination_point_code).count() == 0:
            is_invalid = True
    elif destination_point_type_name == 'Service Point':
        if ServicePoint.objects.filter(service_point_name=destination_point_code).count() == 0:
            is_invalid = True
    elif destination_point_type_name == 'Postal Code':
        if PostalCode.objects.filter(postal_code_name=destination_point_code).count() == 0:
            is_invalid = True

    if is_invalid:
        lane.status_message["L013"] = 'Incorrect DestinationPointCode'
        lane.uni_status = 'INVALID'


# L014 Incorrect IsBetween
def check_l014(lane, **kwargs):
    is_between = lane.is_between

    if str2bool(is_between) is None:
        lane.status_message["L014"] = 'Incorrect IsBetween'
        lane.uni_status = 'INVALID'


# L015: Incorrect Rates
def check_l015(lane, **kwargs):
    weight_breaks_rates = json.loads(lane.weight_break)

    for weight_breaks_rate in weight_breaks_rates.values():
        try:
            float(weight_breaks_rate)
        except ValueError:
            lane.status_message["L015"] = 'Incorrect Rates'
            lane.uni_status = 'INVALID'
    # if not isinstance(weight_breaks_rate, numbers.Number):


# L016: No validations required as not uploaded into DB
def check_l016(lane, **kwargs):
    pass


# L017: Duplicate Lanes
def check_l017(lane, **kwargs):
    # Applies only to VALID lanes
    request_section_id = lane.request_section_id
    existing_request_section_lanes = kwargs['existing_request_section_lanes']
    lanes = kwargs['lanes']
    if lane.uni_status == 'VALID' and lane.request_section_lane_id is None:

        file = kwargs["file"]
        duplicated_lanes = file.duplicate_lane_count

        try:
            lane_exist_in_db = any(
                (x['origin_code'].upper() == lane.origin_point_code.upper() and x[
                    'destination_code'].upper() == lane.destination_point_code.upper())
                for x in
                existing_request_section_lanes)

            lane_exist_in_template = list(filter(lambda x:
                                                 (x.origin_point_code.upper() == lane.origin_point_code.upper() and
                                                  x.destination_point_code.upper() == lane.destination_point_code.upper()),
                                                 lanes))

            if lane_exist_in_db or (len(lane_exist_in_template) > 1):
                lane.status_message["L017"] = 'Duplicate Lane'
                duplicated_lanes += 1
            file.duplicate_lane_count = duplicated_lanes

        except Exception as e:
            print(e)


# L018: Directional Lane in Template
def check_l018(lane, **kwargs):
    try:
        existing_request_section_lanes = kwargs['existing_request_section_lanes']
        file = kwargs["file"]
        directional_lane_count = file.directional_lane_count

        is_between_lanes = list(filter(lambda x: (x['is_between']), existing_request_section_lanes))

        # Applies only to VALID lanes when in DB we already have ate least one lane with in_between = True
        if lane.uni_status == 'VALID' and len(is_between_lanes) > 0:
            for is_between_lane in is_between_lanes:
                origin_point_code = lane.origin_point_code
                destination_point_code = lane.destination_point_code
                if is_between_lane['origin_code'].upper() == destination_point_code.upper() \
                        and is_between_lane['destination_code'].upper() == origin_point_code.upper():
                    directional_lane_count += 1
                    lane.status_message["L018"] = 'Between Lane in RRF already'
            file.directional_lane_count = directional_lane_count
    except Exception as e:
        print(e)


# L019: Between Lane in Template
def check_l019(lane, **kwargs):
    file = kwargs["file"]
    existing_request_section_lanes = kwargs['existing_request_section_lanes']

    between_lane_count = file.between_lane_count

    # Applies only to VALID lanes
    if lane.uni_status == 'VALID':
        is_between = str2bool(lane.is_between)

        # This condition only applies when RequestSectionLaneID is also invalid or missing
        if is_between and lane.request_section_lane_id is None:
            origin_point_code = lane.origin_point_code
            destination_point_code = lane.destination_point_code

            request_section_lanes = list(filter(
                lambda x: (x['origin_code'].upper() == destination_point_code.upper() and x[
                    'destination_code'].upper() == origin_point_code.upper()),
                existing_request_section_lanes))

            if len(request_section_lanes) > 0:
                lane.status_message["L019"] = 'Directional Lane in RRF'
                between_lane_count += 1
        file.between_lane_count = between_lane_count


# L020: Restricted Lanes
def check_l020(lane, **kwargs) -> object:
    # N/A keep placeholder for until rules can be established
    pass


# PP001: Column headers or order do not align to P&C Template
def check_pp001(pricing_point, **kwargs):
    # skipping as we validating headers in different part of code
    pass


# PP002: Blank Rows
def check_pp002(pricing_point, **kwargs):
    # Blank Rows
    if is_empty(pricing_point.request_section_id) or is_empty(pricing_point.request_section_lane_id) or is_empty(
            pricing_point.origin_postal_code_name) or is_empty(pricing_point.destination_postal_code_name):
        pricing_point.status_message["PP002"] = 'Blank Row Ignored'
        pricing_point.uni_status = 'INVALID'


# PP003: Incorrect RequestSectionID
def check_pp003(pricing_point, **kwargs):
    file = kwargs["file"]
    if not is_empty(pricing_point.request_section_id) and file is not None:
        if file.request_section_id != pricing_point.request_section_id:
            pricing_point.status_message["PP003"] = 'Incorrect RequestSectionID'
            pricing_point.uni_status = 'INVALID'


# PP004:
def check_pp004(pricing_point, **kwargs):
    # No validations required as not uploaded into DB
    # Skipping as per RRF
    pass


# PP005: Incorrect RequestSectionLaneID
def check_pp005(pricing_point, **kwargs):
    lane = kwargs['lane']
    file = kwargs["file"]
    error_flag = False

    if not error_flag:
        if lane:
            if not is_empty(lane.request_section_id) and file is not None:
                if to_int(file.request_section_id) != lane.request_section_id:
                    error_flag = True
        else:
            error_flag = True

    if error_flag:
        pricing_point.status_message["PP005"] = 'Incorrect RequestSectionLaneID'
        pricing_point.uni_status = 'INVALID'


# PP006: Incorrect OriginPointCode
def check_pp006(pricing_point, **kwargs):
    if pricing_point.uni_status == 'VALID':
        lane = kwargs['lane']
        if pricing_point.origin_point_code != lane.origin_code:
            pricing_point.status_message["PP006"] = 'Incorrect OriginPointCode'
            pricing_point.uni_status = 'INVALID'


# PP007: Incorrect DestinationPointCode
def check_pp007(pricing_point, **kwargs):
    if pricing_point.uni_status == 'VALID':
        lane = kwargs['lane']
        if pricing_point.destination_point_code != lane.destination_code:
            pricing_point.status_message["PP007"] = 'Incorrect DestinationPointCode'
            pricing_point.uni_status = 'INVALID'


# PP008: Incorrect RequestSectionPricingPointID
def check_pp008(pricing_point, **kwargs):
    request_section_lane_pricing_point = RequestSectionLanePricingPoint.objects.filter(
        request_section_lane_pricing_point_id=to_int(pricing_point.request_section_lane_pricing_point_id)).exists()
    if pricing_point.request_section_lane_pricing_point_id and not request_section_lane_pricing_point:
        pricing_point.status_message["PP008"] = 'Incorrect RequestSectionPricingPointID'
        pricing_point.uni_status = 'INVALID'


# PP009: Incorrect OriginPostCodeID
def check_pp009(pricing_point, **kwargs):
    error_flag = False

    if is_check_passed(pricing_point, ["PP008"]):
        request_section_lane_pricing_point = RequestSectionLanePricingPoint.objects.filter(
            request_section_lane_pricing_point_id=pricing_point.request_section_lane_pricing_point_id).first()

        if request_section_lane_pricing_point:
            if to_int(pricing_point.origin_post_code_id) != request_section_lane_pricing_point.origin_postal_code_id:
                error_flag = True

    if error_flag:
        pricing_point.status_message["PP009"] = 'Incorrect OriginPostCodeID'
        pricing_point.uni_status = 'INVALID'


# PP010: Incorrect OriginPostalCodeName
def check_pp010(pricing_point, **kwargs):
    error_flag = False

    if is_check_passed(pricing_point, ["PP008"]):
        request_section_lane_pricing_point = RequestSectionLanePricingPoint.objects.filter(
            request_section_lane_pricing_point_id=pricing_point.request_section_lane_pricing_point_id).first()
        if request_section_lane_pricing_point:
            if pricing_point.origin_postal_code_name != request_section_lane_pricing_point.origin_postal_code_name:
                error_flag = True

    if error_flag:
        pricing_point.status_message["PP010"] = 'Incorrect OriginPostalCodeName'
        pricing_point.uni_status = 'INVALID'


# PP011: Incorrect DestinationPostCodeID

def check_pp011(pricing_point, **kwargs):
    error_flag = False

    if is_check_passed(pricing_point, ["PP008"]):
        request_section_lane_pricing_point = RequestSectionLanePricingPoint.objects.filter(
            request_section_lane_pricing_point_id=pricing_point.request_section_lane_pricing_point_id).first()
        if request_section_lane_pricing_point:
            if to_int(
                    pricing_point.destination_post_code_id) != request_section_lane_pricing_point.destination_postal_code_id:
                error_flag = True

    if error_flag:
        pricing_point.status_message["PP011"] = 'Incorrect DestinationPostCodeID'
        pricing_point.uni_status = 'INVALID'


# PP012: Incorrect DestinationPostalCodeName
def check_pp012(pricing_point, **kwargs):
    if is_check_passed(pricing_point, ["PP008"]):
        if pricing_point.destination_postal_code_name and not PostalCode.objects.filter(
                postal_code_name=pricing_point.destination_postal_code_name):
            pricing_point.status_message["PP012"] = 'Incorrect DestinationPostalCodeName'
            pricing_point.uni_status = 'INVALID'


# PP013: Incorrect Rates
def check_pp013(pricing_point, **kwargs):
    weight_breaks_rates = json.loads(pricing_point.weight_break)

    for weight_breaks_rate in weight_breaks_rates.values():
        try:
            float(weight_breaks_rate)
        except ValueError:
            pricing_point.status_message["L013"] = 'Incorrect Rates'
            pricing_point.uni_status = 'INVALID'


# PP014:
def check_pp014(pricing_point, **kwargs):
    print('pp014')
    # No validations required as not uploaded into DB
    pass


# PP0015: Duplicate Pricing point
def check_pp015(pricing_point, **kwargs):
    # Applies only to VALID lanes
    try:
        if pricing_point.uni_status == 'VALID' and pricing_point.request_section_lane_pricing_point_id is None:
            lane = kwargs['lane']
            file = kwargs["file"]

            existing_request_section_lane_pricing_points = list(
                RequestSectionLanePricingPoint.objects.values('origin_postal_code_name',
                                                              'destination_postal_code_name').filter(
                    request_section_lane=lane))

            duplicated_lanes = file.duplicate_lane_count

            pricing_point_exist = any(
                (x['origin_postal_code_name'] == pricing_point.origin_postal_code_name and x[
                    'destination_postal_code_name'] == pricing_point.destination_postal_code_name)
                for x in
                existing_request_section_lane_pricing_points)

            if pricing_point_exist:
                pricing_point.status_message["L015"] = 'Duplicate Lanes'
                duplicated_lanes += 1
            # file.duplicate_lane_count = duplicated_lanes

    except Exception as e:
        print(e)


# PP016:
def check_pp016(pricing_point, **kwargs):
    print('pp016')
    # N/A keep placeholder for until rules can be established
    pass


def init_lane_validators():
    validators_lane = [check_l001,
                       check_l002,
                       check_l003,
                       check_l005,
                       check_l006,
                       check_l007,
                       check_l008,
                       check_l009,
                       check_l010,
                       check_l011,
                       check_l012,
                       check_l013,
                       check_l014,
                       check_l015,
                       check_l016,
                       check_l017,
                       check_l018,
                       check_l019,
                       check_l020
                       ]
    # validators_lane = [
    #     check_l019
    # ]
    return validators_lane


def init_pricing_point_validators():
    return [check_pp001,
            check_pp002,
            check_pp003,
            check_pp004,
            check_pp005,
            check_pp006,
            check_pp007,
            check_pp008,
            check_pp009,
            check_pp010,
            check_pp011,
            check_pp012,
            check_pp013,
            check_pp015
            ]


def do_validate_header(header, **kwargs):
    try:
        request_section_id = kwargs['request_section_id']
        error_flag = False
        header.uni_status = 'VALID'
        exclusion_fields = ['id', 'WeightBreak', 'StatusMessage', 'UniStatus', 'UniType', 'CreatedOn', 'UpdatedOn',
                            'CreatedBy', 'File', 'InitialRecOrder']
        clazz = header.__class__
        header_weight_breaks = json.loads(header.weight_break)
        header.status_message = {}
        request_section = RequestSection.objects.filter(request_section_id=request_section_id).first()

        if request_section:
            weight_breaks = []
            request_section_weight_break = request_section.weight_break
            for weight_break in json.loads(request_section_weight_break):
                val = weight_break.split(':')
                weight_breaks.append(tuple(val))
            for idx, header_weight_break in enumerate(header_weight_breaks.keys()):
                if not header_weight_break == weight_breaks[idx][0] and str2bool(weight_breaks[idx][2]):
                    error_flag = True

        clazz_fields = clazz._meta.fields
        for field in clazz_fields:
            db_field = field.get_attname_column()
            field_value = getattr(header, db_field[0], None)

            db_field_name = db_field[1]
            if field_value is not None and db_field_name not in exclusion_fields:
                if db_field_name.upper() != field_value.upper():
                    error_flag = True
                    # TODO to move all literals to dedicated class, file, place...
    except Exception as e:
        error_flag = True

    if error_flag:
        header.status_message["L001"] = 'Column names or order do not align with P&C Template'
        header.uni_status = 'INVALID'


def resolve_lane_ids(entity):
    cnxn = pyodbc_connection()
    cursor = cnxn.cursor()
    entity_uuid = entity.id.hex
    query = queries.RESOLVE_NAME_TO_ID.format(entity_uuid)

    cursor.execute(query)
    ids = cursor.fetchone()
    if ids is None:
        return ids
    entity.request_section_id = ids[0]
    entity.orig_group_type_id = ids[1]
    entity.origin_group_id = ids[2]
    entity.origin_point_type_id = ids[3]

    entity.origin_point_id = ids[4]

    entity.destination_group_type_id = ids[5]
    entity.destination_group_id = ids[6]
    entity.destination_point_type_id = ids[7]
    entity.destination_point_id = ids[8]
    entity.is_between = ids[9]


def resolve_pricing_point_ids(entity):
    cnxn = pyodbc_connection()
    cursor = cnxn.cursor()
    entity_uuid = entity.id.hex
    query = queries.RESOLVE_PP_NAME_TO_ID.format(entity_uuid)

    cursor.execute(query)
    ids = cursor.fetchone()
    if ids is not None:
        entity.origin_postal_code_id = ids[2]
        entity.destination_postal_code_id = ids[3]
    else:
        entity.status_message["S000"] = 'ID resolution error'
        entity.uni_status = 'INVALID'


def do_validate_lanes(file, header, lane, location_hierarchy, **kwargs):
    try:
        existing_request_section_lanes = kwargs['existing_request_section_lanes']
        lanes = kwargs['lanes']
        lane.status_message = {}
        lane.uni_status = 'VALID'
        for validator in init_lane_validators():
            validator(lane, file=file, header=header, location_hierarchy=location_hierarchy,
                      existing_request_section_lanes=existing_request_section_lanes, lanes=lanes)
    except Exception:
        lane.uni_status = 'INVALID'
        lane.status_message = {"L999": "General validation exception"}
    return lane.uni_status


def do_validate_pricing_point(file, header, pricing_point, **kwargs):
    try:
        lane = kwargs['lane']

        pricing_point.status_message = {}
        pricing_point.uni_status = 'VALID'
        for validator in init_pricing_point_validators():
            validator(pricing_point, file=file, header=header, lane=lane)
        return pricing_point.uni_status
    except Exception as e:
        pricing_point.uni_status = 'INVALID'
        pricing_point.status_message = {"PP999": "General validation exception"}
    return pricing_point.uni_status


def is_check_passed(pricing_point, validator_code_list):
    return not any(code in pricing_point.status_message for code in validator_code_list)
