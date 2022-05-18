from pac.helpers.connections import pyodbc_connection


def request_section_lane_insert(request_section_lane, **kwargs):
    rate_table = kwargs['rate_table']

    request_section_id = request_section_lane.request_section_id
    orig_group_type_id = request_section_lane.orig_group_type_id
    orig_group_id = request_section_lane.origin_group_id
    orig_point_type_id = request_section_lane.origin_point_type_id
    orig_point_id = request_section_lane.origin_point_id

    dest_group_type_id = request_section_lane.destination_group_type_id
    dest_group_id = request_section_lane.destination_group_id
    dest_point_type_id = request_section_lane.destination_point_type_id
    dest_point_id = request_section_lane.destination_point_id
    is_between = request_section_lane.is_between
    rates = request_section_lane.weight_break

    cnxn = pyodbc_connection()
    cursor = cnxn.cursor()

    cursor.execute("EXEC [dbo].[RequestSectionLane_Insert] ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?",
                   request_section_id,
                   orig_group_type_id,
                   orig_group_id, orig_point_type_id, orig_point_id, dest_group_type_id, dest_group_id,
                   dest_point_type_id, dest_point_id, is_between, rates, None, None, 0, rate_table)
    raw_data = cursor.fetchone()
    cursor.commit()
    pass


def request_section_lane_pricingpiont_insert(pricing_points_param_array):
    cnxn = pyodbc_connection()
    cursor = cnxn.cursor()

    cursor.execute("EXEC [dbo].[RequestSectionLanePricingPoint_Insert] ?", [pricing_points_param_array])
    cursor.commit()


# convert sting representation of Boolean to native Boolean
def str2bool(value):
    true_set = {'yes', 'true', 't', 'y', '1'}
    false_set = {'no', 'false', 'f', 'n', '0'}

    if isinstance(value, str):
        value = value.lower()
        if value in true_set:
            return True
        if value in false_set:
            return False

    return None


# check if all elements in list are same and matches the given item
def all_elem_same_value(list_of_elem, item):
    return all([elem == item for elem in list_of_elem])


# save int conversion
def to_int(val):
    try:
        return int(val)
    except:
        return None
