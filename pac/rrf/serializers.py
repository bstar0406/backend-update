import json
from pac.pre_costing.serializers import WeightBreakHeaderSerializer

from rest_framework import serializers
from pac.models import Account
from pac.rrf.models import (Customer, LastAssignedUser, Request,
                            RequestAccessorials, RequestHistory,
                            RequestInformation, RequestLane,
                            RequestLaneHistory, RequestProfile,
                            RequestProfileHistory, RequestSection,
                            RequestSectionHistory, RequestSectionLane,
                            RequestSectionLaneHistory,
                            RequestSectionLaneStaging, RequestStatus,
                            RequestSectionLanePricingPoint
                            )


class StringDictionarySerializerField(serializers.Field):
    def to_representation(self, obj):
        return json.dumps(obj)if obj else None

    def to_internal_value(self, data):
        return json.loads(data) if data else None


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = "__all__"
        read_only_fields = ['customer_id', 'is_active', 'is_inactive_viewable']


class RequestInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestInformation
        fields = "__all__"
        read_only_fields = ['request_information_id',
                            'is_active', 'is_inactive_viewable']


class RequestProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestProfile
        fields = "__all__"
        read_only_fields = ['request_profile_id',
                            'is_active', 'is_inactive_viewable']


class RequestAccessorialsSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestAccessorials
        fields = "__all__"
        read_only_fields = ['request_accessorials_id',
                            'is_active', 'is_inactive_viewable']


class RequestProfileRetrieveSerializer(serializers.ModelSerializer):
    freight_elements = serializers.SerializerMethodField()
    shipments = serializers.SerializerMethodField()
    shipping_controls = serializers.SerializerMethodField()
    competitors = serializers.SerializerMethodField()
    class_controls = serializers.SerializerMethodField()
    class_rating_type = serializers.SerializerMethodField()

    def get_freight_elements(self, obj):
        if not obj.freight_elements:
            return None
        return json.loads(obj.freight_elements)

    def get_shipments(self, obj):
        if not obj.shipments:
            return None
        return json.loads(obj.shipments)

    def get_shipping_controls(self, obj):
        if not obj.shipping_controls:
            return None
        return json.loads(obj.shipping_controls)

    def get_competitors(self, obj):
        if not obj.competitors:
            return None
        return json.loads(obj.competitors)

    def get_class_controls(self, obj):
        if not obj.class_controls:
            return None
        return json.loads(obj.class_controls)

    def get_class_rating_type(self, obj):
        if not obj.is_class_density:
            return "Actual"
        return "Class"

    class Meta:
        model = RequestProfile
        fields = [field.name for field in RequestProfile._meta.get_fields()
                  if field.concrete] + ['class_rating_type']


class RequestProfileHistoryRetrieveSerializer(serializers.ModelSerializer):
    freight_elements = serializers.SerializerMethodField()
    shipments = serializers.SerializerMethodField()
    shipping_controls = serializers.SerializerMethodField()
    competitors = serializers.SerializerMethodField()
    class_controls = serializers.SerializerMethodField()
    class_rating_type = serializers.SerializerMethodField()

    def get_freight_elements(self, obj):
        if not obj.freight_elements:
            return None
        return json.loads(obj.freight_elements)

    def get_shipments(self, obj):
        if not obj.shipments:
            return None
        return json.loads(obj.shipments)

    def get_shipping_controls(self, obj):
        if not obj.shipping_controls:
            return None
        return json.loads(obj.shipping_controls)

    def get_competitors(self, obj):
        if not obj.competitors:
            return None
        return json.loads(obj.competitors)

    def get_class_controls(self, obj):
        if not obj.class_controls:
            return None
        return json.loads(obj.class_controls)

    def get_class_rating_type(self, obj):
        if not obj.is_class_density:
            return "Actual"
        return "Class"

    class Meta:
        model = RequestProfileHistory
        fields = [field.name for field in RequestProfileHistory._meta.get_fields()
                  if field.concrete] + ['class_rating_type']


class RequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = "__all__"
        read_only_fields = ['request_id']


class RequestHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestHistory
        fields = "__all__"
        read_only_fields = ['request_version_id', 'request']


class AccountOwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['account_owner']


class RequestStatusReassignSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestStatus
        fields = ['sales_representative', 'pricing_analyst']


class RequestLaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestLane
        fields = "__all__"
        read_only_fields = ['num_sections', 'num_lanes', 'num_unpublished_lanes',
                            'num_edited_lanes', 'num_duplicate_lanes', 'num_versions',
                            'num_do_not_meet_commitment_lanes']


class RequestLaneRevertSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestLane
        fields = "__all__"
        read_only_fields = ['request_lane_id',
                            'is_active', 'is_inactive_viewable']


class RequestLaneRetrieveSerializer(serializers.ModelSerializer):
    override_class = serializers.SerializerMethodField()

    def get_override_class(self, obj):
        return obj.request_set.first().request_profile.override_class

    class Meta:
        model = RequestLane
        fields = [field.name for field in RequestLane._meta.get_fields(
        ) if field.concrete] + ['override_class']
        read_only_fields = ['num_sections', 'num_lanes', 'num_unpublished_lanes',
                            'num_edited_lanes', 'num_duplicate_lanes', 'num_do_not_meet_commitment_lanes']


class RequestLaneHistoryRetrieveSerializer(serializers.ModelSerializer):
    override_class = serializers.SerializerMethodField()

    def get_override_class(self, obj):
        return obj.requesthistory_set.latest('version_num').request_profile_version.override_class

    class Meta:
        model = RequestLaneHistory
        fields = [field.name for field in RequestLaneHistory._meta.get_fields(
        ) if field.concrete] + ['override_class']


class RequestSectionRetrieveSerializer(serializers.ModelSerializer):
    weight_break = serializers.SerializerMethodField()
    weight_break_header = WeightBreakHeaderSerializer()

    def get_weight_break(self, obj):
        return json.loads(obj.weight_break)

    class Meta:
        model = RequestSection
        fields = "__all__"
        read_only_fields = ['num_lanes', 'num_unpublished_lanes',
                            'num_edited_lanes', 'num_duplicate_lanes', 'num_versions',
                            'num_do_not_meet_commitment_lanes']


class RequestSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestSection
        fields = "__all__"
        read_only_fields = ['num_lanes', 'num_unpublished_lanes',
                            'num_edited_lanes', 'num_duplicate_lanes', 'num_versions',
                            'num_do_not_meet_commitment_lanes']


class RequestSectionHistoryRetrieveSerializer(serializers.ModelSerializer):
    request_section_id = serializers.SerializerMethodField()
    weight_break = serializers.SerializerMethodField()
    sub_service_level = serializers.SerializerMethodField()
    rate_base = serializers.SerializerMethodField()
    override_class = serializers.SerializerMethodField()
    equipment_type = serializers.SerializerMethodField()
    weight_break_header = serializers.SerializerMethodField()

    def get_request_section_id(self, obj):
        return obj.request_section.request_section_id

    def get_weight_break(self, obj):
        return json.loads(obj.weight_break)

    def get_sub_service_level(self, obj):
        return obj.sub_service_level_version.sub_service_level_id

    def get_rate_base(self, obj):
        return obj.rate_base_version.rate_base_id if obj.rate_base_version else None

    def get_override_class(self, obj):
        return obj.override_class_version.freight_class_id if obj.override_class_version else None

    def get_equipment_type(self, obj):
        return obj.equipment_type_version.equipment_type_id if obj.equipment_type_version else None

    def get_weight_break_header(self, obj):
        return obj.weight_break_header_version.weight_break_header_id

    class Meta:
        model = RequestSectionHistory
        fields = [field.name for field in RequestSectionHistory._meta.get_fields() if field.concrete] + \
                 ['sub_service_level', 'rate_base', 'override_class', 'request_section_id',
                  'equipment_type', 'weight_break_header']


class RequestSectionLaneHistoryRetrieveSerializer(serializers.ModelSerializer):
    request_section_id = serializers.SerializerMethodField()
    origin_province_id = serializers.SerializerMethodField()
    origin_region_id = serializers.SerializerMethodField()
    origin_country_id = serializers.SerializerMethodField()
    origin_terminal_id = serializers.SerializerMethodField()
    origin_zone_id = serializers.SerializerMethodField()
    origin_basing_point_id = serializers.SerializerMethodField()
    origin_service_point_id = serializers.SerializerMethodField()
    origin_postal_code_id = serializers.SerializerMethodField()
    origin_point_type_id = serializers.SerializerMethodField()
    destination_province_id = serializers.SerializerMethodField()
    destination_region_id = serializers.SerializerMethodField()
    destination_country_id = serializers.SerializerMethodField()
    destination_terminal_id = serializers.SerializerMethodField()
    destination_zone_id = serializers.SerializerMethodField()
    destination_basing_point_id = serializers.SerializerMethodField()
    destination_service_point_id = serializers.SerializerMethodField()
    destination_postal_code_id = serializers.SerializerMethodField()
    destination_point_type_id = serializers.SerializerMethodField()
    commitment = serializers.SerializerMethodField()
    request_section_lane_id = serializers.SerializerMethodField()
    customer_rate = serializers.SerializerMethodField()
    customer_discount = serializers.SerializerMethodField()
    dr_rate = serializers.SerializerMethodField()
    partner_rate = serializers.SerializerMethodField()
    partner_discount = serializers.SerializerMethodField()
    profitability = serializers.SerializerMethodField()
    margin = serializers.SerializerMethodField()
    density = serializers.SerializerMethodField()
    pickup_cost = serializers.SerializerMethodField()
    delivery_cost = serializers.SerializerMethodField()
    accessorials_value = serializers.SerializerMethodField()
    accessorials_percentage = serializers.SerializerMethodField()

    def get_commitment(self, obj):
        return json.loads(obj.commitment)

    def get_customer_rate(self, obj):
        return json.loads(obj.customer_rate)

    def get_customer_discount(self, obj):
        return json.loads(obj.customer_discount)

    def get_dr_rate(self, obj):
        return json.loads(obj.dr_rate)

    def get_partner_rate(self, obj):
        return json.loads(obj.partner_rate)

    def get_partner_discount(self, obj):
        return json.loads(obj.partner_discount)

    def get_profitability(self, obj):
        return json.loads(obj.profitability)

    def get_margin(self, obj):
        return json.loads(obj.margin)

    def get_density(self, obj):
        return json.loads(obj.density)

    def get_pickup_cost(self, obj):
        return json.loads(obj.pickup_cost)

    def get_delivery_cost(self, obj):
        return json.loads(obj.delivery_cost)

    def get_accessorials_value(self, obj):
        return json.loads(obj.accessorials_value)

    def get_accessorials_percentage(self, obj):
        return json.loads(obj.accessorials_percentage)

    def get_request_section_id(self, obj):
        return obj.request_section_version.request_section_id

    def get_request_section_lane_id(self, obj):
        return obj.request_section_lane.request_section_lane_id

    def get_origin_province_id(self, obj):
        return obj.origin_province_version.province_id if obj.origin_province_version else None

    def get_origin_region_id(self, obj):
        return obj.origin_region_version.region_id if obj.origin_region_version else None

    def get_origin_country_id(self, obj):
        return obj.origin_country_version.country_id if obj.origin_country_version else None

    def get_origin_terminal_id(self, obj):
        return obj.origin_terminal_version.terminal_id if obj.origin_terminal_version else None

    def get_origin_zone_id(self, obj):
        return obj.origin_zone_version.zone_id if obj.origin_zone_version else None

    def get_origin_basing_point_id(self, obj):
        return obj.origin_basing_point_version.basing_point_id if obj.origin_basing_point_version else None

    def get_origin_service_point_id(self, obj):
        return obj.origin_service_point_version.service_point_id if obj.origin_service_point_version else None

    def get_origin_postal_code_id(self, obj):
        return obj.origin_postal_code_version.postal_code_id if obj.origin_postal_code_version else None

    def get_origin_point_type_id(self, obj):
        return obj.origin_point_type_version.request_section_lane_point_type_id if obj.origin_point_type_version else None

    def get_destination_province_id(self, obj):
        return obj.destination_province_version.province_id if obj.destination_province_version else None

    def get_destination_region_id(self, obj):
        return obj.destination_region_version.region_id if obj.destination_region_version else None

    def get_destination_country_id(self, obj):
        return obj.destination_country_version.country_id if obj.destination_country_version else None

    def get_destination_terminal_id(self, obj):
        return obj.destination_terminal_version.terminal_id if obj.destination_terminal_version else None

    def get_destination_zone_id(self, obj):
        return obj.destination_zone_version.zone_id if obj.destination_zone_version else None

    def get_destination_basing_point_id(self, obj):
        return obj.destination_basing_point_version.basing_point_id if obj.destination_basing_point_version else None

    def get_destination_service_point_id(self, obj):
        return obj.destination_service_point_version.service_point_id if obj.destination_service_point_version else None

    def get_destination_postal_code_id(self, obj):
        return obj.destination_postal_code_version.postal_code_id if obj.destination_postal_code_version else None

    def get_destination_point_type_id(self, obj):
        return obj.destination_point_type_version.request_section_lane_point_type_id if obj.destination_point_type_version else None

    class Meta:
        model = RequestSectionLaneHistory
        fields = [field.name for field in RequestSectionLaneHistory._meta.get_fields() if field.concrete] + \
                 ['request_section_id', 'request_section_lane_id',
                  'origin_province_id', 'origin_region_id', 'origin_country_id', 'origin_terminal_id', 'origin_zone_id',
                  'origin_basing_point_id', 'origin_service_point_id', 'origin_postal_code_id', 'origin_point_type_id',
                  'destination_province_id', 'destination_region_id', 'destination_country_id',
                  'destination_terminal_id', 'destination_zone_id', 'destination_basing_point_id',
                  'destination_service_point_id', 'destination_postal_code_id', 'destination_point_type_id']


class RequestSectionLaneSerializer(serializers.ModelSerializer):
    commitment = serializers.SerializerMethodField()
    customer_rate = serializers.SerializerMethodField()
    customer_discount = serializers.SerializerMethodField()
    dr_rate = serializers.SerializerMethodField()
    partner_rate = serializers.SerializerMethodField()
    partner_discount = serializers.SerializerMethodField()
    profitability = serializers.SerializerMethodField()
    margin = serializers.SerializerMethodField()
    density = serializers.SerializerMethodField()
    pickup_cost = serializers.SerializerMethodField()
    delivery_cost = serializers.SerializerMethodField()
    accessorials_value = serializers.SerializerMethodField()
    accessorials_percentage = serializers.SerializerMethodField()

    cost_override_margin = serializers.SerializerMethodField()
    cost_override_density = serializers.SerializerMethodField()
    cost_override_pickup_cost = serializers.SerializerMethodField()
    cost_override_delivery_cost = serializers.SerializerMethodField()
    cost_override_accessorials_value = serializers.SerializerMethodField()
    cost_override_accessorials_percentage = serializers.SerializerMethodField()

    pricing_rates = serializers.SerializerMethodField()
    workflow_errors = serializers.SerializerMethodField()

    def get_commitment(self, obj):
        return json.loads(obj.commitment)

    def get_customer_rate(self, obj):
        return json.loads(obj.customer_rate)

    def get_customer_discount(self, obj):
        return json.loads(obj.customer_discount)

    def get_dr_rate(self, obj):
        return json.loads(obj.dr_rate)

    def get_partner_rate(self, obj):
        return json.loads(obj.partner_rate)

    def get_partner_discount(self, obj):
        return json.loads(obj.partner_discount)

    def get_profitability(self, obj):
        return json.loads(obj.profitability)

    def get_margin(self, obj):
        return json.loads(obj.margin)

    def get_density(self, obj):
        return json.loads(obj.density)

    def get_pickup_cost(self, obj):
        return json.loads(obj.pickup_cost)

    def get_delivery_cost(self, obj):
        return json.loads(obj.delivery_cost)

    def get_accessorials_value(self, obj):
        return json.loads(obj.accessorials_value)

    def get_accessorials_percentage(self, obj):
        return json.loads(obj.accessorials_percentage)
# TODO find a way how to check object before json.loads

    def get_cost_override_margin(self, obj):
        return json.loads(obj.cost_override_margin) if obj.cost_override_margin else []

    def get_cost_override_density(self, obj):
        return json.loads(obj.cost_override_density) if obj.cost_override_density else []

    def get_cost_override_pickup_cost(self, obj):
        return json.loads(obj.cost_override_pickup_cost) if obj.cost_override_pickup_cost else []

    def get_cost_override_delivery_cost(self, obj):
        return json.loads(obj.cost_override_delivery_cost) if obj.cost_override_delivery_cost else []

    def get_cost_override_accessorials_value(self, obj):
        return json.loads(obj.cost_override_accessorials_value) if obj.cost_override_accessorials_value else []

    def get_cost_override_accessorials_percentage(self, obj):
        return json.loads(
            obj.cost_override_accessorials_percentage) if obj.cost_override_accessorials_percentage else []

    def get_pricing_rates(self, obj):
        return json.loads(obj.pricing_rates) if obj.pricing_rates else None

    def get_workflow_errors(self, obj):
        return json.loads(obj.workflow_errors) if obj.workflow_errors else None

    class Meta:
        model = RequestSectionLane
        exclude = ['basing_point_hash_code', 'lane_hash_code']


class RequestSectionLaneStagingSerializer(serializers.ModelSerializer):
    commitment = serializers.SerializerMethodField()
    customer_rate = serializers.SerializerMethodField()
    customer_discount = serializers.SerializerMethodField()
    dr_rate = serializers.SerializerMethodField()
    partner_rate = serializers.SerializerMethodField()
    partner_discount = serializers.SerializerMethodField()
    profitability = serializers.SerializerMethodField()
    margin = serializers.SerializerMethodField()
    density = serializers.SerializerMethodField()
    pickup_cost = serializers.SerializerMethodField()
    delivery_cost = serializers.SerializerMethodField()
    accessorials_value = serializers.SerializerMethodField()
    accessorials_percentage = serializers.SerializerMethodField()
    new_commitment = serializers.SerializerMethodField()
    new_customer_rate = serializers.SerializerMethodField()
    new_customer_discount = serializers.SerializerMethodField()
    new_dr_rate = serializers.SerializerMethodField()
    new_partner_rate = serializers.SerializerMethodField()
    new_partner_discount = serializers.SerializerMethodField()
    new_profitability = serializers.SerializerMethodField()
    new_margin = serializers.SerializerMethodField()
    new_density = serializers.SerializerMethodField()
    new_pickup_cost = serializers.SerializerMethodField()
    new_delivery_cost = serializers.SerializerMethodField()
    new_accessorials_value = serializers.SerializerMethodField()
    new_accessorials_percentage = serializers.SerializerMethodField()

    def get_commitment(self, obj):
        return json.loads(obj.commitment)

    def get_customer_rate(self, obj):
        return json.loads(obj.customer_rate)

    def get_customer_discount(self, obj):
        return json.loads(obj.customer_discount)

    def get_dr_rate(self, obj):
        return json.loads(obj.dr_rate)

    def get_partner_rate(self, obj):
        return json.loads(obj.partner_rate)

    def get_partner_discount(self, obj):
        return json.loads(obj.partner_discount)

    def get_profitability(self, obj):
        return json.loads(obj.profitability)

    def get_margin(self, obj):
        return json.loads(obj.margin)

    def get_density(self, obj):
        return json.loads(obj.density)

    def get_pickup_cost(self, obj):
        return json.loads(obj.pickup_cost)

    def get_delivery_cost(self, obj):
        return json.loads(obj.delivery_cost)

    def get_accessorials_value(self, obj):
        return json.loads(obj.accessorials_value)

    def get_accessorials_percentage(self, obj):
        return json.loads(obj.accessorials_percentage)

    def get_new_commitment(self, obj):
        return json.loads(obj.new_commitment)

    def get_new_customer_rate(self, obj):
        return json.loads(obj.new_customer_rate)

    def get_new_customer_discount(self, obj):
        return json.loads(obj.new_customer_discount)

    def get_new_dr_rate(self, obj):
        return json.loads(obj.new_dr_rate)

    def get_new_partner_rate(self, obj):
        return json.loads(obj.new_partner_rate)

    def get_new_partner_discount(self, obj):
        return json.loads(obj.new_partner_discount)

    def get_new_profitability(self, obj):
        return json.loads(obj.new_profitability)

    def get_new_margin(self, obj):
        return json.loads(obj.new_margin)

    def get_new_density(self, obj):
        return json.loads(obj.new_density)

    def get_new_pickup_cost(self, obj):
        return json.loads(obj.new_pickup_cost)

    def get_new_delivery_cost(self, obj):
        return json.loads(obj.new_delivery_cost)

    def get_new_accessorials_value(self, obj):
        return json.loads(obj.new_accessorials_value)

    def get_new_accessorials_percentage(self, obj):
        return json.loads(obj.new_accessorials_percentage)

    class Meta:
        model = RequestSectionLaneStaging
        exclude = ['basing_point_hash_code',
                   'lane_hash_code', 'context_created_on']


class RequestSectionLanePricingPointSerializer(serializers.ModelSerializer):
    request_section_lane_pricing_point_id = serializers.IntegerField(allow_null=True)
    cost = StringDictionarySerializerField(allow_null=True)
    dr_rate = StringDictionarySerializerField(allow_null=True)
    fak_rate = StringDictionarySerializerField(allow_null=True)
    profitability = StringDictionarySerializerField(allow_null=True)
    splits_all = StringDictionarySerializerField(allow_null=True)
    margin = StringDictionarySerializerField(allow_null=True)
    density = StringDictionarySerializerField(allow_null=True)
    pickup_cost = StringDictionarySerializerField(allow_null=True)
    delivery_cost = StringDictionarySerializerField(allow_null=True)
    accessorials_value = StringDictionarySerializerField(allow_null=True)
    accessorials_percentage = StringDictionarySerializerField(allow_null=True)

    workflow_errors = StringDictionarySerializerField(allow_null=True)
    pricing_rates = StringDictionarySerializerField(allow_null=True)

    class Meta:
        model = RequestSectionLanePricingPoint
        exclude = ['pricing_point_hash_code', 'request_section_lane',
                   'origin_postal_code', 'destination_postal_code', 'pricing_point_number']


class LastAssignedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = LastAssignedUser
        fields = "__all__"


class RequestStatusCurrentEditorUpdateSerializer(serializers.Serializer):
    action = serializers.CharField()
    current_editor = serializers.IntegerField()
