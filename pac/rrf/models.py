import uuid

from django.db import models
from django.db.models import Q
from django.dispatch import receiver
from django.utils import timezone

from core.models import User, UserHistory
from pac.helpers.base import CommentUpdateDelete, Delete
from pac.models import (Account, AccountHistory, BasingPoint,
                        BasingPointHistory, City, CityHistory, Country,
                        CountryHistory, Notification, NotificationHistory,
                        PostalCode, PostalCodeHistory, Province,
                        ProvinceHistory, Region, RegionHistory, ServiceLevel,
                        ServiceLevelHistory, ServiceOffering,
                        ServiceOfferingHistory, ServicePoint,
                        ServicePointHistory, SubServiceLevel,
                        SubServiceLevelHistory, Terminal, TerminalHistory,
                        Unit, WeightBreakHeader, WeightBreakHeaderHistory)


class AccountTree(Delete):
    account_tree_id = models.BigAutoField(
        primary_key=True, null=False, db_column="AccountTreeID")
    account = models.OneToOneField(
        Account, on_delete=models.CASCADE, db_column="AccountID", related_name="+")
    parent_account = models.ForeignKey(
        Account, on_delete=models.CASCADE, null=True, db_column="ParentAccountID", related_name="+")

    def __str__(self):
        return str(self.account_tree_id)

    class Meta:
        db_table = 'AccountTree'


class AccountTreeHistory(CommentUpdateDelete):
    account_tree_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="AccountTreeVersionID")
    account_tree = models.ForeignKey(
        AccountTree, on_delete=models.CASCADE, db_column="AccountTreeID")
    account_version = models.ForeignKey(
        AccountHistory, on_delete=models.CASCADE, db_column="AccountVersionID", related_name="+")
    parent_account_version = models.ForeignKey(
        AccountHistory, on_delete=models.CASCADE, null=True, db_column="ParentAccountVersionID", related_name="+")

    def __str__(self):
        return str(self.account_tree_version_id)

    class Meta:
        index_together = (('account_tree', 'version_num'))
        db_table = 'AccountTree_History'


class Currency(Delete):
    currency_id = models.BigAutoField(
        primary_key=True, null=False, db_column="CurrencyID")
    currency_name = models.CharField(
        max_length=50, unique=True, null=False, blank=False, db_column="CurrencyName")
    currency_code = models.CharField(
        max_length=3, unique=True, null=False, blank=False, db_column="CurrencyCode")

    def __str__(self):
        return str(self.currency_id)

    class Meta:
        db_table = 'Currency'


class CurrencyHistory(CommentUpdateDelete):
    currency_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="CurrencyVersionID")
    currency = models.ForeignKey(
        Currency, on_delete=models.CASCADE, db_column="CurrencyID")
    currency_name = models.CharField(
        max_length=50, null=False, blank=False, db_column="CurrencyName")
    currency_code = models.CharField(
        max_length=3, null=False, blank=False, db_column="CurrencyCode")

    def __str__(self):
        return str(self.currency_version_id)

    class Meta:
        index_together = (('currency', 'version_num'))
        db_table = 'Currency_History'


class Customer(Delete):
    customer_id = models.BigAutoField(
        primary_key=True, null=False, db_column="CustomerID")
    account = models.ForeignKey(
        Account, on_delete=models.CASCADE, null=True, db_column="AccountID")
    service_level = models.ForeignKey(
        ServiceLevel, on_delete=models.CASCADE, db_column="ServiceLevelID")
    city = models.ForeignKey(
        City, on_delete=models.CASCADE, null=True, db_column="CityID")
    customer_name = models.CharField(
        max_length=100, unique=False, null=True, blank=False, db_column="CustomerName")
    customer_alias = models.CharField(
        max_length=100, unique=False, null=True, blank=False, db_column="CustomerAlias")
    customer_address_line_1 = models.CharField(
        max_length=100, unique=False, null=True, blank=False, db_column="CustomerAddressLine1")
    customer_address_line_2 = models.CharField(
        max_length=100, unique=False, null=True, blank=False, db_column="CustomerAddressLine2")
    postal_code = models.CharField(
        max_length=10, unique=False, null=True, blank=False, db_column="PostalCode")
    contact_name = models.CharField(
        max_length=100, unique=False, null=True, blank=False, db_column="ContactName")
    contact_title = models.CharField(
        max_length=100, unique=False, null=True, blank=False, db_column="ContactTitle")
    phone = models.CharField(
        max_length=100, unique=False, null=True, blank=False, db_column="Phone")
    email = models.CharField(
        max_length=100, unique=False, null=True, blank=False, db_column="Email")
    website = models.CharField(
        max_length=100, unique=False, null=True, blank=False, db_column="Website")
    is_valid_data = models.BooleanField(
        null=False, default=False, db_column="IsValidData")

    def __str__(self):
        return str(self.customer_id)

    class Meta:
        db_table = 'Customer'


class CustomerHistory(CommentUpdateDelete):
    customer_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="CustomerVersionID")
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, db_column="CustomerID")
    account_version = models.ForeignKey(
        AccountHistory, on_delete=models.CASCADE, null=True, db_column="AccountVersionID")
    service_level_version = models.ForeignKey(
        ServiceLevelHistory, on_delete=models.CASCADE, db_column="ServiceLevelVersionID")
    city_version = models.ForeignKey(
        CityHistory, on_delete=models.CASCADE, null=True, db_column="CityVersionID")
    customer_name = models.CharField(
        max_length=100, null=True, blank=False, db_column="CustomerName")
    customer_alias = models.CharField(
        max_length=100, null=True, blank=False, db_column="CustomerAlias")
    customer_address_line_1 = models.CharField(
        max_length=100, null=True, blank=False, db_column="CustomerAddressLine1")
    customer_address_line_2 = models.CharField(
        max_length=100, null=True, blank=False, db_column="CustomerAddressLine2")
    postal_code = models.CharField(
        max_length=10, null=True, blank=False, db_column="PostalCode")
    contact_name = models.CharField(
        max_length=100, null=True, blank=False, db_column="ContactName")
    contact_title = models.CharField(
        max_length=100, null=True, blank=False, db_column="ContactTitle")
    phone = models.CharField(
        max_length=100, null=True, blank=False, db_column="Phone")
    email = models.CharField(
        max_length=100, null=True, blank=False, db_column="Email")
    website = models.CharField(
        max_length=100, null=True, blank=False, db_column="Website")
    is_valid_data = models.BooleanField(
        null=False, default=False, db_column="IsValidData")

    def __str__(self):
        return str(self.customer_version_id)

    class Meta:
        index_together = (('customer', 'version_num'))
        db_table = 'Customer_History'


class Language(Delete):
    language_id = models.BigAutoField(
        primary_key=True, null=False, db_column="LanguageID")
    language_name = models.CharField(
        max_length=50, unique=True, null=False, blank=False, db_column="LanguageName")
    language_code = models.CharField(
        max_length=2, unique=True, null=False, blank=False, db_column="LanguageCode")

    def __str__(self):
        return str(self.language_id)

    class Meta:
        db_table = 'Language'


class LanguageHistory(CommentUpdateDelete):
    language_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="LanguageVersionID")
    language = models.ForeignKey(
        Language, on_delete=models.CASCADE, db_column="LanguageID")
    language_name = models.CharField(
        max_length=50, null=False, blank=False, db_column="LanguageName")
    language_code = models.CharField(
        max_length=2, null=False, blank=False, db_column="LanguageCode")

    def __str__(self):
        return str(self.language_version_id)

    class Meta:
        index_together = (('language', 'version_num'))
        db_table = 'Language_History'


class RequestStatusType(Delete):
    request_status_type_id = models.BigAutoField(
        primary_key=True, null=False, db_column="RequestStatusTypeID")
    request_status_type_name = models.CharField(
        max_length=50, unique=True, null=False, blank=False, db_column="RequestStatusTypeName")
    next_request_status_type = models.TextField(
        default="[]", null=False, blank=False, db_column="NextRequestStatusType")
    assigned_persona = models.CharField(
        max_length=50, null=False, blank=False, db_column="AssignedPersona")
    editor = models.CharField(
        max_length=50, null=False, blank=False, db_column="Editor")
    queue_personas = models.TextField(
        default="[]", null=False, blank=False, db_column="QueuePersonas")
    is_secondary = models.BooleanField(
        default=False, null=False, blank=False, db_column="IsSecondary")
    is_final = models.BooleanField(
        default=False, null=False, blank=False, db_column="IsFinal")

    def __str__(self):
        return str(self.request_status_type_id)

    class Meta:
        db_table = 'RequestStatusType'


class RequestStatusTypeHistory(CommentUpdateDelete):
    request_status_type_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="RequestStatusTypeVersionID")
    request_status_type = models.ForeignKey(
        RequestStatusType, on_delete=models.CASCADE, db_column="RequestStatusTypeID")
    request_status_type_name = models.CharField(
        max_length=50, null=False, blank=False, db_column="RequestStatusTypeName")
    next_request_status_type = models.TextField(
        default="[]", null=False, blank=False, db_column="NextRequestStatusType")
    assigned_persona = models.CharField(
        max_length=50, null=False, blank=False, db_column="AssignedPersona")
    editor = models.CharField(
        max_length=50, null=False, blank=False, db_column="Editor")
    queue_personas = models.TextField(
        default="[]", null=False, blank=False, db_column="QueuePersonas")
    is_secondary = models.BooleanField(
        default=False, null=False, blank=False, db_column="IsSecondary")
    is_final = models.BooleanField(
        default=False, null=False, blank=False, db_column="IsFinal")

    def __str__(self):
        return str(self.request_status_type_version_id)

    class Meta:
        index_together = (('request_status_type', 'version_num'))
        db_table = 'RequestStatusType_History'


class FreightClass(Delete):
    freight_class_id = models.BigAutoField(
        primary_key=True, null=False, db_column="FreightClassID")
    freight_class_name = models.CharField(
        max_length=50, unique=True, null=False, blank=False, db_column="FreightClassName")

    def __str__(self):
        return str(self.freight_class_id)

    class Meta:
        db_table = 'FreightClass'


class FreightClassHistory(CommentUpdateDelete):
    freight_class_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="FreightClassVersionID")
    freight_class = models.ForeignKey(
        FreightClass, on_delete=models.CASCADE, db_column="FreightClassID")
    freight_class_name = models.CharField(
        max_length=50, null=False, blank=False, db_column="FreightClassName")

    def __str__(self):
        return str(self.freight_class_version_id)

    class Meta:
        index_together = (('freight_class', 'version_num'))
        db_table = 'FreightClass_History'


class RateBase(Delete):
    rate_base_id = models.BigAutoField(
        primary_key=True, null=False, db_column="RateBaseID")
    rate_base_name = models.CharField(
        max_length=50, null=False, blank=False, db_column="RateBaseName")
    product_number = models.CharField(
        max_length=50, null=True, blank=False, db_column="ProductNumber")
    description = models.TextField(
        max_length=50, null=True, blank=False, db_column="Description")
    release = models.CharField(
        max_length=50, null=True, blank=False, db_column="Release")
    effective_date = models.DateField(
        max_length=50, null=True, blank=False, db_column="EffectiveDate")

    def __str__(self):
        return str(self.rate_base_id)

    class Meta:
        db_table = 'RateBase'


class RateBaseHistory(CommentUpdateDelete):
    rate_base_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="RateBaseVersionID")
    rate_base = models.ForeignKey(
        RateBase, on_delete=models.CASCADE, db_column="RateBaseID")
    rate_base_name = models.CharField(
        max_length=50, null=False, blank=False, db_column="RateBaseName")
    product_number = models.CharField(
        max_length=50, null=True, blank=False, db_column="ProductNumber")
    description = models.TextField(
        max_length=50, null=True, blank=False, db_column="Description")
    release = models.CharField(
        max_length=50, null=True, blank=False, db_column="Release")
    effective_date = models.DateField(
        max_length=50, null=True, blank=False, db_column="EffectiveDate")

    def __str__(self):
        return str(self.rate_base_version_id)

    class Meta:
        index_together = (('rate_base', 'version_num'))
        db_table = 'RateBase_History'


class EquipmentType(Delete):
    equipment_type_id = models.BigAutoField(
        primary_key=True, null=False, db_column="EquipmentTypeID")
    equipment_type_name = models.CharField(
        max_length=50, null=False, blank=False, db_column="EquipmentTypeName")
    equipment_type_code = models.CharField(
        max_length=2, null=False, blank=False, db_column="EquipmentTypeCode")

    def __str__(self):
        return str(self.equipment_type_id)

    class Meta:
        db_table = 'EquipmentType'


class EquipmentTypeHistory(CommentUpdateDelete):
    equipment_type_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="EquipmentTypeVersionID")
    equipment_type = models.ForeignKey(
        EquipmentType, on_delete=models.CASCADE, db_column="EquipmentTypeID")
    equipment_type_name = models.CharField(
        max_length=50, null=False, blank=False, db_column="EquipmentTypeName")
    equipment_type_code = models.CharField(
        max_length=2, null=False, blank=False, db_column="EquipmentTypeCode")

    def __str__(self):
        return str(self.equipment_type_version_id)

    class Meta:
        index_together = (('equipment_type', 'version_num'))
        db_table = 'EquipmentType_History'


class Zone(Delete):
    zone_id = models.BigAutoField(
        primary_key=True, null=False, db_column="ZoneID")
    zone_name = models.CharField(
        max_length=50, null=False, blank=False, db_column="ZoneName")
    zone_code = models.CharField(
        max_length=10, unique=True, null=True, blank=False, default="Test", db_column="ZoneCode")
    description = models.TextField(
        max_length=50, null=True, blank=False, db_column="Description")

    def __str__(self):
        return str(self.zone_id)

    class Meta:
        db_table = 'Zone'


class ZoneHistory(CommentUpdateDelete):
    zone_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="ZoneVersionID")
    zone = models.ForeignKey(
        Zone, on_delete=models.CASCADE, null=False, db_column="ZoneID")
    zone_name = models.CharField(
        max_length=50, null=False, blank=False, db_column="ZoneName")
    zone_code = models.CharField(
        max_length=10, unique=True, null=True, blank=False, default="Test", db_column="ZoneCode")
    description = models.TextField(
        max_length=50, null=True, blank=False, db_column="Description")

    def __str__(self):
        return str(self.zone_version_id)

    class Meta:
        index_together = (('zone', 'version_num'))
        db_table = 'Zone_History'


class RequestType(Delete):
    request_type_id = models.BigAutoField(
        primary_key=True, null=False, db_column="RequestTypeID")
    request_type_name = models.CharField(
        max_length=50, unique=True, null=False, blank=False, db_column="RequestTypeName")
    apply_to_customer_under_review = models.BooleanField(
        null=False, default=True, db_column="ApplyToCustomerUnderReview")
    apply_to_revision = models.BooleanField(
        null=False, default=True, db_column="ApplyToRevision")
    allow_sales_commitment = models.BooleanField(
        null=False, default=True, db_column="AllowSalesCommitment")

    def __str__(self):
        return str(self.request_type_id)

    class Meta:
        db_table = 'RequestType'


class RequestTypeHistory(CommentUpdateDelete):
    request_type_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="RequestTypeVersionID")
    request_type = models.ForeignKey(
        RequestType, on_delete=models.CASCADE, db_column="RequestTypeID")
    request_type_name = models.CharField(
        max_length=50, null=False, blank=False, db_column="RequestTypeName")
    apply_to_customer_under_review = models.BooleanField(
        null=False, default=True, db_column="ApplyToCustomerUnderReview")
    apply_to_revision = models.BooleanField(
        null=False, default=True, db_column="ApplyToRevision")
    allow_sales_commitment = models.BooleanField(
        null=False, default=True, db_column="AllowSalesCommitment")

    def __str__(self):
        return str(self.request_type_version_id)

    class Meta:
        index_together = (('request_type', 'version_num'))
        db_table = 'RequestType_History'


class RequestAccessorials(Delete):
    request_accessorials_id = models.BigAutoField(
        primary_key=True, null=False, db_column="RequestAccessorialsID")
    request_number = models.CharField(
        max_length=32, unique=True, null=False, blank=False, db_column="RequestNumber")
    is_valid_data = models.BooleanField(
        null=False, default=False, db_column="IsValidData")

    def __str__(self):
        return str(self.request_accessorials_id)

    class Meta:
        db_table = 'RequestAccessorials'


class RequestAccessorialsHistory(CommentUpdateDelete):
    request_accessorials_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="RequestAccessorialsVersionID")
    request_accessorials = models.ForeignKey(
        RequestAccessorials, on_delete=models.CASCADE, db_column="RequestAccessorialsID")
    request_number = models.CharField(
        max_length=32, null=False, blank=False, db_column="RequestNumber")
    is_valid_data = models.BooleanField(
        null=False, default=False, db_column="IsValidData")

    def __str__(self):
        return str(self.request_accessorials_version_id)

    class Meta:
        index_together = (('request_accessorials', 'version_num'))
        db_table = 'RequestAccessorials_History'


class RequestInformation(Delete):
    request_information_id = models.BigAutoField(
        primary_key=True, null=False, db_column="RequestInformationID")
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, db_column="CustomerID")
    request_type = models.ForeignKey(
        RequestType, on_delete=models.CASCADE, null=True, db_column="RequestTypeID")
    language = models.ForeignKey(
        Language, on_delete=models.CASCADE, null=True, db_column="LanguageID")
    currency = models.ForeignKey(
        Currency, on_delete=models.CASCADE, null=True, db_column="CurrencyID")
    request_number = models.CharField(
        max_length=32, unique=True, null=False, blank=False, db_column="RequestNumber")
    is_valid_data = models.BooleanField(
        null=False, default=False, db_column="IsValidData")
    is_new_business = models.BooleanField(
        null=True, default=True, db_column="IsNewBusiness")
    is_paying_by_credit_card = models.BooleanField(
        null=True, default=True, db_column="IsPayingByCreditCard")
    is_extended_payment = models.BooleanField(
        null=True, default=True, db_column="IsExtendedPayment")
    extended_payment_terms_margin = models.FloatField(
        null=True, default=True, db_column="ExtendedPaymentTermsMargin")

    extended_payment_days = models.IntegerField(
        null=True, blank=False, db_column="ExtendedPaymentDays")
    priority = models.IntegerField(
        null=True, blank=False, db_column="Priority")
    effective_date = models.DateField(null=True, blank=False, db_column="EffectiveDate")
    expiry_date = models.DateField(null=True, blank=False, db_column="ExpiryDate")

    def __str__(self):
        return str(self.request_information_id)

    class Meta:
        db_table = 'RequestInformation'


class RequestInformationHistory(CommentUpdateDelete):
    request_information_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="RequestInformationVersionID")
    request_information = models.ForeignKey(
        RequestInformation, on_delete=models.CASCADE, db_column="RequestInformationID")
    customer_version = models.ForeignKey(
        CustomerHistory, on_delete=models.CASCADE, db_column="CustomerVersionID")
    request_type_version = models.ForeignKey(
        RequestTypeHistory, on_delete=models.CASCADE, null=True, db_column="RequestTypeVersionID")
    language_version = models.ForeignKey(
        LanguageHistory, on_delete=models.CASCADE, null=True, db_column="LanguageVersionID")
    currency_version = models.ForeignKey(
        CurrencyHistory, on_delete=models.CASCADE, null=True, db_column="CurrencyVersionID")
    request_number = models.CharField(
        max_length=32, null=False, blank=False, db_column="RequestNumber")
    is_valid_data = models.BooleanField(
        null=False, default=False, db_column="IsValidData")
    is_new_business = models.BooleanField(
        null=True, default=True, db_column="IsNewBusiness")
    is_paying_by_credit_card = models.BooleanField(
        null=True, default=True, db_column="IsPayingByCreditCard")
    is_extended_payment = models.BooleanField(
        null=True, default=True, db_column="IsExtendedPayment")
    extended_payment_terms_margin = models.FloatField(
        null=True, default=True, db_column="ExtendedPaymentTermsMargin")

    extended_payment_days = models.IntegerField(
        null=True, blank=False, db_column="ExtendedPaymentDays")
    priority = models.IntegerField(
        null=True, blank=False, db_column="Priority")
    effective_date = models.DateField(null=True, blank=False, db_column="EffectiveDate")
    expiry_date = models.DateField(null=True, blank=False, db_column="ExpiryDate")

    def __str__(self):
        return str(self.request_information_version_id)

    class Meta:
        index_together = (('request_information', 'version_num'))
        db_table = 'RequestInformation_History'


class RequestLane(Delete):
    request_lane_id = models.BigAutoField(
        primary_key=True, null=False, db_column="RequestLaneID")
    request_number = models.CharField(
        max_length=32, unique=True, null=False, blank=False, db_column="RequestNumber")
    is_valid_data = models.BooleanField(
        null=False, default=False, db_column="IsValidData")
    num_sections = models.IntegerField(
        null=False, blank=False, default=0, db_column="NumSections")
    num_lanes = models.IntegerField(
        null=False, blank=False, default=0, db_column="NumLanes")
    num_unpublished_lanes = models.IntegerField(
        null=False, blank=False, default=0, db_column="NumUnpublishedLanes")
    num_edited_lanes = models.IntegerField(
        null=False, blank=False, default=0, db_column="NumEditedLanes")
    num_duplicate_lanes = models.IntegerField(
        null=False, blank=False, default=0, db_column="NumDuplicateLanes")
    num_do_not_meet_commitment_lanes = models.IntegerField(
        null=False, blank=False, default=0, db_column="NumDoNotMeetCommitmentLanes")

    def __str__(self):
        return str(self.request_lane_id)

    class Meta:
        db_table = 'RequestLane'


class RequestLaneHistory(CommentUpdateDelete):
    request_lane_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="RequestLaneVersionID")
    request_lane = models.ForeignKey(
        RequestLane, on_delete=models.CASCADE, db_column="RequestLaneID")
    request_number = models.CharField(
        max_length=32, null=False, blank=False, db_column="RequestNumber")
    is_valid_data = models.BooleanField(
        null=False, default=False, db_column="IsValidData")
    num_sections = models.IntegerField(
        null=False, blank=False, db_column="NumSections")
    num_lanes = models.IntegerField(
        null=False, blank=False, db_column="NumLanes")
    num_unpublished_lanes = models.IntegerField(
        null=False, blank=False, db_column="NumUnpublishedLanes")
    num_edited_lanes = models.IntegerField(
        null=False, blank=False, db_column="NumEditedLanes")
    num_duplicate_lanes = models.IntegerField(
        null=False, blank=False, db_column="NumDuplicateLanes")
    num_do_not_meet_commitment_lanes = models.IntegerField(
        null=False, blank=False, default=0, db_column="NumDoNotMeetCommitmentLanes")

    def __str__(self):
        return str(self.request_lane_version_id)

    class Meta:
        index_together = (('request_lane', 'version_num'))
        db_table = 'RequestLane_History'

class Commodity(Delete):
    commodity_id = models.BigAutoField(
        primary_key=True, null=False, db_column="CommodityID")
    freight_class = models.ForeignKey(
        FreightClass, on_delete=models.CASCADE, db_column="FreightClassID")
    is_active = models.BooleanField(
        default=False, null=False, db_column="IsActive")
    is_inactive_viewable = models.BooleanField(
        default=False, null=False, db_column="IsInactiveViewable")
    commodity_name = models.TextField(
        max_length=100, null=True, blank=False, db_column="CommodityName")
    commodity_code = models.TextField(
        max_length=100, null=True, blank=False, db_column="CommodityCode")

    def __str__(self):
        return str(self.commodity_id)

    class Meta:
        #index_together = (("commodity_id"))
        db_table = 'Commodity'

class CommodityHistory(CommentUpdateDelete):
        commodity_version_id = models.BigAutoField(
            primary_key=True, null=False, db_column="CommodityVersionID")
        commodity_id = models.ForeignKey(
            Commodity, on_delete=models.CASCADE, db_column="CommodityID")
        freight_class_version_id = models.ForeignKey(
            FreightClassHistory, on_delete=models.CASCADE, db_column="FreightClassVersionID")
        is_active = models.BooleanField(
            default=False, null=False, db_column="IsActive")
        is_inactive_viewable = models.BooleanField(
            default=False, null=False, db_column="IsInactiveViewable")
        commodity_name = models.TextField(
            max_length=100, null=True, blank=False, db_column="CommodityName")
        commodity_code_history = models.TextField(
            max_length=100, null=True, blank=False, db_column="CommodityCode")

        def __str__(self):
            return str(self.commodity_id)

        class Meta:
            index_together = (("commodity_id", "version_num"))
            db_table = 'Commodity_History'

class AccChargeBehavior(Delete):
        acc_charge_behaviour_id = models.BigAutoField(
            primary_key=True, null=False, db_column="AccChargeBehaviorID")
        tm_charge_behavior_code = models.TextField(
            max_length=40, null=True, blank=False, db_column="TMChargeBehaviorCode")
        is_active = models.BooleanField(
            default=False, null=False, db_column="IsActive")
        is_inactive_viewable = models.BooleanField(
            default=False, null=False, db_column="IsInactiveViewable")
        acc_charge_behavior = models.TextField(
            max_length=10, null=True, blank=False, db_column="AccChargeBehavior")

        def __str__(self):
            return str(self.acc_charge_behaviour_id)
        class Meta:
            db_table = 'AccChargeBehavior'

class AccChargeBehaviorHistory(Delete):
        version_num = models.IntegerField(
            default=False, null=False, db_column="VersionNum")
        is_latest_version = models.BooleanField(
            default=False, null=False, db_column="IsLatestVersion")
        updated_on = models.DateTimeField(
            default=False, null=False, db_column="UpdatedOn")
        updated_by = models.TextField(
            default=False, null=False, db_column="UpdatedBy")
        base_version = models.IntegerField(
            default=False, null=False, db_column="BaseVersion")
        comments = models.TextField(
            default=False, null=False, db_column="Comments")
        acc_charge_behaviour_version_id = models.BigAutoField(
            primary_key=True, null=False, db_column="AccChargeBehaviorID")
        tm_charge_behavior_code = models.ForeignKey(
            AccChargeBehavior, on_delete=models.CASCADE,  db_column="TMChargeBehaviorCode")
        is_active = models.BooleanField(
            default=False, null=False, db_column="IsActive")
        is_inactive_viewable = models.BooleanField(
            default=False, null=False, db_column="IsInactiveViewable")
        acc_charge_behavior = models.TextField(
            max_length=10, null=True, blank=False, db_column="AccChargeBehavior")

        def __str__(self):
            return str(self.acc_charge_behaviour_version_id)

        class Meta:
            index_together = (("acc_charge_behaviour_version_id", "version_num"))
            db_table = 'AccChargeBehaviorHistory'

class AccRangeType(Delete):
        acc_range_type_id = models.BigAutoField(
            primary_key=True, null=False, db_column="AccRangeTypeID")
        tm_range_type_code = models.TextField(
            max_length=10, null=True, blank=False, db_column="TMRangeTypeCode")
        is_active = models.BooleanField(
            default=False, null=False, db_column="IsActive")
        is_inactive_viewable = models.BooleanField(
            default=False, null=False, db_column="IsInactiveViewable")
        tm_range_type = models.TextField(
            max_length=40, null=True, blank=False, db_column="TMRangeType")

        def __str__(self):
            return str(self.acc_range_type_id)
        class Meta:
            db_table = 'AccRangeType'

class AccRangeTypeHistory(Delete):
        version_num = models.IntegerField(
            default=False, null=False, db_column="VersionNum")
        is_latest_version = models.BooleanField(
            default=False, null=False, db_column="IsLatestVersion")
        updated_on = models.DateTimeField(
            default=False, null=False, db_column="UpdatedOn")
        updated_by = models.TextField(
            default=False, null=False, db_column="UpdatedBy")
        base_version = models.IntegerField(
            default=False, null=False, db_column="BaseVersion")
        comments = models.TextField(
            default=False, null=False, db_column="Comments")
        acc_range_type_version_id = models.BigAutoField(
            primary_key=True, null=False, db_column="AccRangeTypeVersionID")
        tm_range_type_code = models.ForeignKey(
            AccRangeType, on_delete=models.CASCADE, db_column="TMRangeTypeCode")
        is_active = models.BooleanField(
            default=False, null=False, db_column="IsActive")
        is_inactive_viewable = models.BooleanField(
            default=False, null=False, db_column="IsInactiveViewable")
        tm_range_type =  models.TextField(
            max_length=40, null=True, blank=False, db_column="TMRangeType")

        def __str__(self):
            return str(self.acc_range_type_version_id)

        class Meta:
            index_together = (("acc_range_type_version_id", "version_num"))
            db_table = 'AccRangeTypeHistory'


class AccFactor(Delete):
        acc_factor_id = models.BigAutoField(
            primary_key=True, null=False, db_column="AccFactorID")
        tm_acc_factor_code = models.TextField(
            max_length=10, null=True, blank=False, db_column="TMAccFactorCode")
        is_active = models.BooleanField(
            default=False, null=False, db_column="IsActive")
        is_inactive_viewable = models.BooleanField(
            default=False, null=False, db_column="IsInactiveViewable")
        acc_factor = models.TextField(
            max_length=40, null=True, blank=False, db_column="AccFactor")

        def __str__(self):
            return str(self.acc_factor_id)
        class Meta:
            db_table = 'AccFactor'

class AccFactorHistory(Delete):
        version_num = models.IntegerField(
            default=False, null=False, db_column="VersionNum")
        is_latest_version = models.BooleanField(
            default=False, null=False, db_column="IsLatestVersion")
        updated_on = models.DateTimeField(
            default=False, null=False, db_column="UpdatedOn")
        updated_by = models.TextField(
            default=False, null=False, db_column="UpdatedBy")
        base_version = models.IntegerField(
            default=False, null=False, db_column="BaseVersion")
        comments = models.TextField(
            default=False, null=False, db_column="Comments")
        acc_factor_version_id = models.BigAutoField(
            primary_key=True, null=False, db_column="AccFactorVersionID")
        tm_acc_factor_code = models.ForeignKey(
            AccFactor, on_delete=models.CASCADE, db_column="TMAccFactorCode")
        is_active = models.BooleanField(
            default=False, null=False, db_column="IsActive")
        is_inactive_viewable = models.BooleanField(
            default=False, null=False, db_column="IsInactiveViewable")
        acc_factor = models.TextField(
            max_length=40, null=True, blank=False, db_column="AccFactor")

        def __str__(self):
            return str(self.acc_factor_version_id)

        class Meta:
            index_together = (("acc_factor_version_id", "version_num"))
            db_table = 'AccFactorHistory'

class AccessorialHeader(Delete):
    acc_header_id = models.BigAutoField(
            primary_key=True, null=False, db_column="AccHeaderID")
    is_active = models.BooleanField(
            default=False, null=False, db_column="IsActive")
    is_inactive_viewable = models.BooleanField(
            default=False, null=False, db_column="IsInactiveViewable")
    tmacc_charge_code = models.TextField(
            max_length=10, null=True, blank=False, db_column="TMAccChargeCode")
    acc_charge_behaviour_id = models.ForeignKey(
            AccChargeBehavior, on_delete=models.CASCADE, db_column="AccChargeBehaviourID")
    currency_id_accessorial_header= models.ForeignKey(
            Currency, on_delete=models.CASCADE, db_column="CurrencyID", related_name="+")
    dangerous_goods = models.BooleanField(
            default=False, null=False, db_column="DangerousGoods")
    acc_range_field_id = models.ForeignKey(
            AccRangeType, on_delete=models.CASCADE, db_column="AccRangeTypeID")
    description = models.TextField(
            max_length=40, null=True, blank=False, db_column="Description")
    temperature_controlled = models.BooleanField(
            default=False, null=False, db_column="TemperatureControlled")
    business_grouping = models.BigIntegerField(
            default=False, null=False, db_column="BusinessGrouping")

    def __str__(self):
        return str(self.acc_header_id)

    class Meta:
        db_table = 'AccessorialHeader'


class AccessorialHeaderHistory(CommentUpdateDelete):
    version_num = models.IntegerField(
            default=False, null=False, db_column="VersionNum")
    is_latest_version = models.BooleanField(
            default=False, null=False, db_column="IsLatestVersion")
    updated_on = models.DateTimeField(
            default=False, null=False, db_column="UpdatedOn")
    updated_by = models.TextField(
            default=False, null=False, db_column="UpdatedBy")
    base_version = models.IntegerField(
            default=False, null=False, db_column="BaseVersion")
    comments = models.TextField(
            default=False, null=False, db_column="Comments")
    acc_header_version_id = models.BigAutoField(
            primary_key=True, null=False, db_column="AccHeaderVersionID")
    is_active = models.BooleanField(
            default=False, null=False, db_column="IsActive")
    is_inactive_viewable = models.BooleanField(
            default=False, null=False, db_column="IsInactiveViewable")
    tmacc_charge_code = models.TextField(
            max_length=10, null=True, blank=False, db_column="TMAccChargeCode")
    acc_charge_behaviour_version_id = models.ForeignKey(
            AccChargeBehavior, on_delete=models.CASCADE, db_column="AccChargeBehaviourVersionID", related_name="+")
    currency_id= models.ForeignKey(
            Currency, on_delete=models.CASCADE, db_column="CurrencyID", related_name="+")
    dangerous_goods = models.BooleanField(
            default=False, null=False, db_column="DangerousGoods")
    acc_range_field_version_id = models.ForeignKey(
            AccRangeTypeHistory, on_delete=models.CASCADE, db_column="AccRangeTypeVersionID", related_name="+")
    description = models.TextField(
            max_length=40, null=True, blank=False, db_column="Description")
    temperature_controlled = models.BooleanField(
            default=False, null=False, db_column="TemperatureControlled")
    business_grouping = models.BigIntegerField(
            default=False, null=False, db_column="BusinessGrouping")

    def __str__(self):
            return str(self.acc_header_version_id)

    class Meta:
            index_together = (("acc_header_version_id", "version_num"))
            db_table = 'AccessorialHeader_History'

class AccessorialDetail(Delete):
    acc_detail_id = models.BigAutoField(
            primary_key=True, null=False, db_column="AccDetailID")
    is_active = models.BooleanField(
            default=False, null=False, db_column="IsActive")
    is_inactive_viewable = models.BooleanField(
            default=False, null=False, db_column="IsInactiveViewable")
    tmacc_detail_id = models.BigIntegerField(
            default=False, null=False, db_column="TMAccDetailID")
    acc_header_id = models.ForeignKey(
            AccessorialHeader, on_delete=models.CASCADE, db_column="AccHeaderID")
    allow_between = models.BooleanField(
            default=False, null=False, db_column="AllowBetween")
    carrier_movement_type = models.TextField(
            max_length=1, null=True, blank=False, db_column="CarrierMovementType")
    commodity_id = models.ForeignKey(
            Commodity, on_delete=models.CASCADE, db_column="CommodityID")
    acc_rate_custom_maximum = models.DecimalField(
            max_digits=19, decimal_places=6, null=True, db_column="AccRateCustomMaximum")
    acc_rate_custom_minimum = models.DecimalField(
            max_digits=19, decimal_places=6, null=True, db_column="AccRateCustomMinimum")
    description = models.TextField(
            max_length=40, null=True, blank=False, db_column="Description")
    effective_from = models.DateTimeField(
            auto_now_add=False, null=True, db_column="EffectiveFrom")
    effective_to = models.DateTimeField(
            auto_now_add=False, null=True, db_column="EffectiveTo")
    origin_zone_type = models.TextField(
            max_length=10, null=True, blank=False, db_column="OriginZoneType")
    origin_zone_id = models.BigIntegerField(
            default=False, null=False, blank=False, db_column="OriginZoneID")
    destination_zone_type = models.TextField(
            max_length=10, null=True, blank=False, db_column="DestinationZoneType")
    destination_zone_id = models.BigIntegerField(
            default=False, null=False, blank=False, db_column="DestinationZoneID")
    sub_service_level_id = models.ForeignKey(
            SubServiceLevel, on_delete=models.CASCADE, db_column="SubServiceLevelID")
    acc_rate_dock = models.BooleanField(
            default=False, null=False, db_column="AccRateDock")
    acc_rate_DOE_factorA = models.DecimalField(
            max_digits=19, decimal_places=6, null=True, db_column="AccRateDOEFactorA")
    acc_rate_DOE_factorB = models.DecimalField(
            max_digits=19, decimal_places=6, null=True, db_column="AccRateDOEFactorB")
    acc_rate_elevator = models.BooleanField(
            default=False, null=False, db_column="AccRateElevator")
    acc_rate_exclude_legs = models.BooleanField(
            default=False, null=False, db_column="AccRateExcludeLegs")
    acc_rate_extra_stop_rates = models.TextField(
            max_length=4000, null=True, blank=False, db_column="AccRateExtraStopRates")
    acc_rate_factorID = models.ForeignKey(
            AccFactor, on_delete=models.CASCADE, db_column="AccRateFactorID", related_name="+")
    acc_rate_increment = models.DecimalField(
            max_digits=19, decimal_places=6, null=True, db_column="AccRateIncrement")
    acc_rate_fuel_price_average = models.TextField(
            max_length=10, null=True, blank=False, db_column="AccRateFuelPriceAverage")
    acc_rate_max_charge = models.DecimalField(
            max_digits=19, decimal_places=6, null=True, db_column="AccRateMaxCharge")
    acc_rate_min_charge = models.DecimalField(
            max_digits=19, decimal_places=6, null=True, db_column="AccRateMinCharge")
    acc_rate_percent = models.DecimalField(
            max_digits=19, decimal_places=6, null=True, db_column="AccRatePercent")
    acc_rate_range_field1ID = models.ForeignKey(
            AccRangeType, on_delete=models.CASCADE, db_column="AccRangeTypeID", related_name="+")
    acc_rate_range_field2ID = models.BigIntegerField(
            default=False, null=True, db_column="AccRateRangeField2ID")
    acc_rate_range_from1 = models.DecimalField(
            max_digits=19, decimal_places=6, null=True, db_column="AccRateRangeFrom1")
    acc_rate_range_to1 = models.DecimalField(
            max_digits=19, decimal_places=6, null=True, db_column="AccRateRangeTo1")
    acc_rate_range_from2 = models.DecimalField(
            max_digits=19, decimal_places=6, null=True, db_column="AccRateRangeFrom2")
    acc_rate_range_to2 = models.DecimalField(
            max_digits=19, decimal_places=6, null=True, db_column="AccRateRangeTo2")
    acc_rate_shipping_instructionID = models.BigIntegerField(
            default=False, null=True, db_column="AccRateShippingInstructionID")
    acc_rate_survey = models.BooleanField(
            default=False, null=False, db_column="AccRateSurvey")
    acc_rate_stairs = models.BooleanField(
            default=False, null=False, db_column="AccRateStairs")
    acc_rate_status_code = models.TextField(
            max_length=10, null=True, blank=False, db_column="AccRateStatusCode")
    acc_rate_threshold_amount = models.DecimalField(
            max_digits=19, decimal_places=6, null=True, db_column="AccRateThresholdAmount")
    acc_rate_vehicle_restricted = models.BooleanField(
            default=False, null=False, db_column="AccRateVehicleRestricted")

    def __str__(self):
        return str(self.acc_detail_id)

    class Meta:
        db_table = 'AccessorialDetail'


class AccessorialDetailHistory(CommentUpdateDelete):
    version_num = models.IntegerField(
            default=False, null=False, db_column="VersionNum")
    is_latest_version = models.BooleanField(
            default=False, null=False, db_column="IsLatestVersion")
    updated_on = models.DateTimeField(
            default=False, null=False, db_column="UpdatedOn")
    updated_by = models.TextField(
            default=False, null=False, db_column="UpdatedBy")
    base_version = models.IntegerField(
            default=False, null=False, db_column="BaseVersion")
    comments = models.TextField(
            default=False, null=False, db_column="Comments")
    acc_detail_version_id = models.BigAutoField(
            primary_key=True, null=False, db_column="AccDetailVersionID")
    is_active = models.BooleanField(
            default=False, null=False, db_column="IsActive")
    is_inactive_viewable = models.BooleanField(
            default=False, null=False, db_column="IsInactiveViewable")
    tmacc_detail_id = models.BigIntegerField(
            default=False, null=False, db_column="TMAccDetailID")
    acc_header_version_id = models.BigIntegerField(
            default=False, null=False, db_column="AccountHeader")
    allow_between = models.BooleanField(
            default=False, null=False, db_column="AllowBetween")
    carrier_movement_type = models.TextField(
            max_length=1, null=True, blank=False, db_column="CarrierMovementType")
    commodity_id = models.ForeignKey(
            Commodity, on_delete=models.CASCADE, db_column="CommodityID")
    acc_rate_custom_maximum = models.DecimalField(
            max_digits=19, decimal_places=6, null=True, db_column="AccRateCustomMaximum")
    acc_rate_custom_minimum = models.DecimalField(
            max_digits=19, decimal_places=6, null=True, db_column="AccRateCustomMinimum")
    description = models.TextField(
            max_length=40, null=True, blank=False, db_column="Description")
    effective_from = models.DateTimeField(
            auto_now_add=False, null=True, db_column="EffectiveFrom")
    effective_to = models.DateTimeField(
            auto_now_add=False, null=True, db_column="EffectiveTo")
    origin_zone_type = models.TextField(
            max_length=10, null=True, blank=False, db_column="OriginZoneType")
    origin_zone_id = models.ForeignKey(
        Zone, on_delete=models.CASCADE, null=True, db_column="OriginZoneID", related_name="+")
    destination_zone_type = models.TextField(
            max_length=10, null=True, blank=False, db_column="DestinationZoneType")
    destination_zone_id = models.ForeignKey(
            Zone, on_delete=models.CASCADE, null=True, db_column="DestinationZoneID", related_name="+")
    sub_service_level_id = models.ForeignKey(
            SubServiceLevel, on_delete=models.CASCADE, db_column="SubServiceLevelID")
    acc_rate_dock = models.BooleanField(
            default=False, null=False, db_column="AccRateDock")
    acc_rate_DOE_factorA = models.DecimalField(
            max_digits=19, decimal_places=6, null=True, db_column="AccRateDOEFactorA")
    acc_rate_DOE_factorB = models.DecimalField(
            max_digits=19, decimal_places=6, null=True, db_column="AccRateDOEFactorB")
    acc_rate_elevator = models.BooleanField(
            default=False, null=False, db_column="AccRateElevator")
    acc_rate_exclude_legs = models.BooleanField(
            default=False, null=False, db_column="AccRateExcludeLegs")
    acc_rate_extra_stop_rates = models.TextField(
            max_length=4000, null=True, blank=False, db_column="AccRateExtraStopRates")
    acc_rate_factorID = models.ForeignKey(
            AccFactor, on_delete=models.CASCADE, db_column="AccRateFactorID")
    acc_rate_increment = models.DecimalField(
            max_digits=19, decimal_places=6, null=True, db_column="AccRateIncrement")
    acc_rate_fuel_price_average = models.TextField(
            max_length=10, null=True, blank=False, db_column="AccRateFuelPriceAverage")
    acc_rate_max_charge = models.DecimalField(
            max_digits=19, decimal_places=6, null=True, db_column="AccRateMaxCharge")
    acc_rate_min_charge = models.DecimalField(
            max_digits=19, decimal_places=6, null=True, db_column="AccRateMinCharge")
    acc_rate_percent = models.DecimalField(
            max_digits=19, decimal_places=6, null=True, db_column="AccRatePercent")
    acc_rate_range_field_version1_id = models.ForeignKey(
            AccRangeTypeHistory, on_delete=models.CASCADE, db_column="AccRangeTypeVersionID", related_name="+")
    acc_rate_range_field_version2_id = models.BigIntegerField(
            default=False, null=True, db_column="AccRateRangeFieldVersion2ID")
    acc_rate_range_from1 = models.DecimalField(
            max_digits=19, decimal_places=6, null=True, db_column="AccRateRangeFrom1")
    acc_rate_range_to1 = models.DecimalField(
            max_digits=19, decimal_places=6, null=True, db_column="AccRateRangeTo1")
    acc_rate_range_from2 = models.DecimalField(
            max_digits=19, decimal_places=6, null=True, db_column="AccRateRangeFrom2")
    acc_rate_range_to2 = models.DecimalField(
            max_digits=19, decimal_places=6, null=True, db_column="AccRateRangeTo2")
    acc_rate_shipping_instructionID = models.BigIntegerField(
            default=False, null=True, db_column="AccRateShippingInstructionID")
    acc_rate_survey = models.BooleanField(
            default=False, null=False, db_column="AccRateSurvey")
    acc_rate_stairs = models.BooleanField(
            default=False, null=False, db_column="AccRateStairs")
    acc_rate_status_code = models.TextField(
            max_length=10, null=True, blank=False, db_column="AccRateStatusCode")
    acc_rate_threshold_amount = models.DecimalField(
            max_digits=19, decimal_places=6, null=True, db_column="AccRateThresholdAmount")
    acc_rate_vehicle_restricted = models.BooleanField(
            default=False, null=False, db_column="AccRateVehicleRestricted")

    def __str__(self):
            return str(self.acc_detail_version_id)

    class Meta:
            index_together = (("acc_detail_version_id", "version_num"))
            db_table = 'AccessorialDetail_History'


class AccessorialDetention(Delete):
        acc_detention_id = models.BigAutoField(
            primary_key=True, null=False, db_column="AccDetentionID")
        tm_detention_id = models.BigIntegerField(
            default=False, null=False, db_column="TMDetentionID")
        is_active = models.BooleanField(
            default=False, null=False, db_column="IsActive")
        is_inactive_viewable = models.BooleanField(
            default=False, null=False, db_column="IsInactiveViewable")
        acc_header_id = models.ForeignKey(
            AccessorialHeader, on_delete=models.CASCADE, db_column="AccHeaderID")
        base_rate = models.BooleanField(
            default=False, null=False, db_column="BaseRate")
        currency_id_accessorial_detention= models.ForeignKey(
            Currency, on_delete=models.CASCADE, db_column="CurrencyID", related_name="+")
        description = models.TextField(
            max_length=40, null=True, blank=False, db_column="Description")
        detention_type = models.TextField(
            max_length=10, null=True, blank=False, db_column="DetentionType")
        effective_from = models.DateTimeField(
            default=False, null=False, db_column="EffectiveFrom")
        effective_to = models.DateTimeField(
            default=False, null=False, db_column="EffectiveTo")
        equipment_id = models.ForeignKey(
            EquipmentType, on_delete=models.CASCADE, null=True, db_column="EquipmentTypeID", related_name="+")
        exclude_closed_days_detention = models.TextField(
            max_length=20, null=True, blank=False, db_column="ExcludeClosedDaysDetention")
        exclude_closed_days_freetime = models.TextField(
            max_length=20, null=True, blank=False, db_column="ExcludeClosedDaysFreeTime")
        fb_based_date_field = models.TextField(
            max_length=10, null=True, blank=False, db_column="FBBasedDateField")
        free_time = models.DecimalField(
            max_digits=19, decimal_places=6, null=True, db_column="FreeTime")
        free_time_unit = models.TextField(
            max_length=3, null=True, blank=False, db_column="FreeTimeUnit")
        freetime_unit_to_measure = models.TextField(
            max_length=10, null=True, blank=False, db_column="FreeTimeUnitofMeasure")
        inter_company= models.TextField(
            max_length=5, null=True, blank=False, db_column="InterCompany")
        late_no_bill = models.TextField(
            max_length=5, null=True, blank=False, db_column="LateNoBill")
        late_window = models.DecimalField(
            max_digits=19, decimal_places=6, null=True, db_column="LateWindow")
        ltl_proration_method = models.TextField(
            max_length=10, null=True, blank=False, db_column="LtlProrationMethod")
        max_bill_time = models.DecimalField(
            max_digits=19, decimal_places=6, null=True, db_column="MaxBillTime")
        min_bill_time = models.DecimalField(
            max_digits=19, decimal_places=6, null=True, db_column="MinBillTime")
        free_times= models.TextField(
            max_length=4000, null=True, blank=False, db_column="FreeTimes")
        sub_service_level_id = models.ForeignKey(
            SubServiceLevel, on_delete=models.CASCADE, db_column="SubServiceLevelID")
        operations_code = models.TextField(
            max_length=10, null=True, blank=False, db_column="OperationsCode")
        payment_option = models.TextField(
            max_length=10, null=True, blank=False, db_column="PaymentOption")
        second_bill_rate = models.DecimalField(
            max_digits=19, decimal_places=6, null=True, db_column="SecondBillRate")
        shipper = models.TextField(
            max_length=10, null=True, blank=False, db_column="Shipper")
        shipper_group = models.TextField(
            max_length=10, null=True, blank=False, db_column="ShipperGroup")
        origin_zone_type = models.TextField(
            max_length=10, null=True, blank=False, db_column="OriginZoneType")
        origin_zone_id = models.ForeignKey(
            Zone, on_delete=models.CASCADE, null=True, db_column="OriginZoneID", related_name="+")
        destination_zone_type = models.TextField(
            max_length=40, null=True, blank=False, db_column="DestinationZoneType")
        destination_zone_id = models.ForeignKey(
                Zone, on_delete=models.CASCADE, null=True, db_column="DestinationZoneID", related_name="+")
        destination_zone_id = models.BigIntegerField(
            default=False, null=False, db_column="DestinationZoneID")
        start_bill_rate = models.DecimalField(
            max_digits=19, decimal_places=6, null=True, db_column="StartBillRate")
        start_option = models.TextField(
            max_length=40, null=True, blank=False, db_column="StartOption")
        stop_option = models.TextField(
            max_length=40, null=True, blank=False, db_column="StopOption")
        use_actual_time = models.BooleanField(
            default=False, null=False, db_column="UseActualTime")
        warning_send = models.TextField(
            max_length=5, null=True, blank=False, db_column="WarningSend")
        warning_time = models.DecimalField(
            max_digits=19, decimal_places=6, null=True, db_column="WarningTime")

        def __str__(self):
            return str(self.acc_detention_id)
        class Meta:
            db_table = 'AccessorialDetention'

class AccessorialDetentionHistory(Delete):
        version_num = models.IntegerField(
            default=False, null=False, db_column="VersionNum")
        is_latest_version = models.BooleanField(
            default=False, null=False, db_column="IsLatestVersion")
        updated_on = models.DateTimeField(
            default=False, null=False, db_column="UpdatedOn")
        updated_by = models.TextField(
            default=False, null=False, db_column="UpdatedBy")
        base_version = models.IntegerField(
            default=False, null=False, db_column="BaseVersion")
        comments = models.TextField(
            default=False, null=False, db_column="Comments")
        acc_detention_version_id = models.BigAutoField(
            primary_key=True, null=False, db_column="AccDetentionVersionID")
        tm_detention_id = models.BigIntegerField(
            default=False, null=False, db_column="TMDetentionID")
        is_active = models.BooleanField(
            default=False, null=False, db_column="IsActive")
        is_inactive_viewable = models.BooleanField(
            default=False, null=False, db_column="IsInactiveViewable")
        acc_header_version_id = models.ForeignKey(
            AccessorialHeaderHistory, on_delete=models.CASCADE, db_column="AccHeaderVersionID")
        base_rate = models.BooleanField(
            default=False, null=False, db_column="BaseRate")
        currency_id_accessorial_detention_history = models.ForeignKey(
            Currency, on_delete=models.CASCADE, db_column="CurrencyID", related_name="+")
        description = models.TextField(
            max_length=40, null=True, blank=False, db_column="Description")
        detention_type = models.TextField(
            max_length=10, null=True, blank=False, db_column="DetentionType")
        effective_from = models.DateTimeField(
            default=False, null=False, db_column="EffectiveFrom")
        effective_to = models.DateTimeField(
            default=False, null=False, db_column="EffectiveTo")
        equipment_id = models.ForeignKey(
            EquipmentType, on_delete=models.CASCADE, null=True, db_column="EquipmentTypeID", related_name="+")
        exclude_closed_days_detention = models.TextField(
            max_length=20, null=True, blank=False, db_column="ExcludeClosedDaysDetention")
        exclude_closed_days_freetime = models.TextField(
            max_length=20, null=True, blank=False, db_column="ExcludeClosedDaysFreeTime")
        fb_based_date_field = models.TextField(
            max_length=10, null=True, blank=False, db_column="FBBasedDateField")
        free_time = models.DecimalField(
            max_digits=19, decimal_places=6, null=True, db_column="FreeTime")
        free_time_unit = models.TextField(
             max_length=3, null=True, blank=False, db_column="FreeTimeUnit")
        freetime_unit_to_measure = models.TextField(
             max_length=10, null=True, blank=False, db_column="FreeTimeUnitofMeasure")
        inter_company= models.TextField(
             max_length=5, null=True, blank=False, db_column="InterCompany")
        late_no_bill = models.TextField(
             max_length=5, null=True, blank=False, db_column="LateNoBill")
        late_window = models.DecimalField(
            max_digits=19, decimal_places=6, null=True, db_column="LateWindow")
        ltl_proration_method = models.TextField(
             max_length=10, null=True, blank=False, db_column="LtlProrationMethod")
        max_bill_time = models.DecimalField(
            max_digits=19, decimal_places=6, null=True, db_column="MaxBillTime")
        min_bill_time = models.DecimalField(
            max_digits=19, decimal_places=6, null=True, db_column="MinBillTime")
        free_times= models.TextField(
            max_length=4000, null=True, blank=False, db_column="FreeTimes")
        sub_service_level_id = models.ForeignKey(
            SubServiceLevel, on_delete=models.CASCADE, db_column="SubServiceLevelID")
        operations_code = models.TextField(
            max_length=10, null=True, blank=False, db_column="OperationsCode")
        payment_option = models.TextField(
            max_length=10, null=True, blank=False, db_column="PaymentOption")
        second_bill_rate = models.DecimalField(
            max_digits=19, decimal_places=6, null=True, db_column="SecondBillRate")
        shipper = models.TextField(
            max_length=10, null=True, blank=False, db_column="Shipper")
        shipper_group = models.TextField(
            max_length=10, null=True, blank=False, db_column="ShipperGroup")
        origin_zone_type = models.TextField(
            max_length=10, null=True, blank=False, db_column="OriginZoneType")
        origin_zone_id = models.BigIntegerField(
            default=False, null=False, db_column="OriginZoneID")
        destination_zone_type = models.TextField(
            max_length=40, null=True, blank=False, db_column="DestinationZoneType")
        destination_zone_id = models.BigIntegerField(
            default=False, null=False, db_column="DestinationZoneID")
        start_bill_rate = models.DecimalField(
            max_digits=19, decimal_places=6, null=True, db_column="StartBillRate")
        start_option = models.TextField(
            max_length=40, null=True, blank=False, db_column="StartOption")
        stop_option = models.TextField(
            max_length=40, null=True, blank=False, db_column="StopOption")
        use_actual_time = models.BooleanField(
            default=False, null=False, db_column="UseActualTime")
        warning_send = models.TextField(
             max_length=5, null=True, blank=False, db_column="WarningSend")
        warning_time = models.DecimalField(
            max_digits=19, decimal_places=6, null=True, db_column="WarningTime")

        def __str__(self):
            return str(self.acc_detention_version_id)

        class Meta:
            index_together = (("acc_detention_version_id", "version_num"))
            db_table = 'AccessorialDetentionHistory'

class AccessorialStorage(Delete):
    acc_storage_id = models.BigAutoField(
            primary_key=True, null=False, db_column="AccStorageID")
    is_active = models.BooleanField(
            default=False, null=False, db_column="IsActive")
    is_inactive_viewable = models.BooleanField(
            default=False, null=False, db_column="IsInactiveViewable")
    tm_storage_id = models.BigIntegerField(
            default=False, null=False, blank=False, db_column="TMStorageID")
    acc_header_id = models.ForeignKey(
                AccessorialHeader, on_delete=models.CASCADE, db_column="AccHeaderID")
    base_rate = models.BooleanField(
            default=False, null=False, db_column="BaseRate")
    bill_option = models.TextField(
            max_length=1, null=True, blank=False, db_column="BillOption")
    currency_id_accessorial_storage= models.ForeignKey(
            Currency, on_delete=models.CASCADE, db_column="CurrencyID", related_name="+")
    dangerous_goods = models.BooleanField(
            default=False, null=False, db_column="DangerousGoods")
    description = models.TextField(
            max_length=40, null=True, blank=False, db_column="Description")
    effective_from = models.DateTimeField(
            default=False, null=False, db_column="EffectiveFrom")
    effective_to = models.DateTimeField(
            default=False, null=False, db_column="EffectiveTo")
    free_days = models.BigIntegerField(
            default=False, null=False, db_column="FreeDays")
    high_value = models.BooleanField(
            default=False, null=False, db_column="HighValue")
    include_delivery_day = models.BooleanField(
            default=False, null=False, db_column="IncludeDeliveryDay")
    include_terminal_service_calendar = models.BooleanField(
            default=False, null=False, db_column="IncludeTerminalServiceCalendar")
    sub_service_level_id = models.ForeignKey(
            SubServiceLevel, on_delete=models.CASCADE, db_column="SubServiceLevelID")
    operations_code = models.TextField(
            max_length=10, null=True, blank=False, db_column="OperationsCode")
    rate_amount = models.DecimalField(
            max_digits=19, decimal_places=6, null=True, db_column="RateAmount")
    rate_max = models.DecimalField(
            max_digits=19, decimal_places=6, null=True, db_column="RateMax")
    rate_min = models.DecimalField(
            max_digits=19, decimal_places=6, null=True, db_column="RateMin")
    rate_per = models.DecimalField(
            max_digits=19, decimal_places=6, null=True, db_column="RatePer")
    unit_id = models.ForeignKey(
            Unit, on_delete=models.CASCADE, db_column="UnitID", related_name="+")
    temp_controlled = models.BooleanField(
                default=False, null=False, db_column="TempControlled")

    def __str__(self):
        return str(self.acc_storage_id)

    class Meta:
        db_table = 'AccessorialStorage'


class AccessorialStorageHistory(CommentUpdateDelete):
    version_num = models.IntegerField(
            default=False, null=False, db_column="VersionNum")
    is_latest_version = models.BooleanField(
            default=False, null=False, db_column="IsLatestVersion")
    updated_on = models.DateTimeField(
            default=False, null=False, db_column="UpdatedOn")
    updated_by = models.TextField(
            default=False, null=False, db_column="UpdatedBy")
    base_version = models.IntegerField(
            default=False, null=False, db_column="BaseVersion")
    comments = models.TextField(
            default=False, null=False, db_column="Comments")
    acc_storage_version_id = models.BigAutoField(
            primary_key=True, null=False, db_column="AccStorageVersionID")
    is_active = models.BooleanField(
            default=False, null=False, db_column="IsActive")
    is_inactive_viewable = models.BooleanField(
            default=False, null=False, db_column="IsInactiveViewable")
    tm_storage_id = models.BigIntegerField(
            default=False, null=False, blank=False, db_column="TMStorageID")
    acc_header_version_id = models.ForeignKey(
                AccessorialHeaderHistory, on_delete=models.CASCADE, db_column="AccHeaderVersionID")
    base_rate = models.BooleanField(
            default=False, null=False, db_column="BaseRate")
    bill_option = models.TextField(
            max_length=1, null=True, blank=False, db_column="BillOption")
    currency_id_accessorial_storage= models.ForeignKey(
            Currency, on_delete=models.CASCADE, db_column="CurrencyID", related_name="+")
    dangerous_goods = models.BooleanField(
            default=False, null=False, db_column="DangerousGoods")
    description = models.TextField(
            max_length=40, null=True, blank=False, db_column="Description")
    effective_from = models.DateTimeField(
            default=False, null=False, db_column="EffectiveFrom")
    effective_to = models.DateTimeField(
            default=False, null=False, db_column="EffectiveTo")
    free_days = models.BigIntegerField(
            default=False, null=False, db_column="FreeDays")
    high_value = models.BooleanField(
            default=False, null=False, db_column="HighValue")
    include_delivery_day = models.BooleanField(
            default=False, null=False, db_column="IncludeDeliveryDay")
    include_terminal_service_calendar = models.BooleanField(
            default=False, null=False, db_column="IncludeTerminalServiceCalendar")
    sub_service_level_id = models.ForeignKey(
            SubServiceLevel, on_delete=models.CASCADE, db_column="SubServiceLevelID")
    operations_code = models.TextField(
            max_length=10, null=True, blank=False, db_column="OperationsCode")
    rate_amount = models.DecimalField(
            max_digits=19, decimal_places=6, null=True, db_column="RateAmount")
    rate_max = models.DecimalField(
            max_digits=19, decimal_places=6, null=True, db_column="RateMax")
    rate_min = models.DecimalField(
            max_digits=19, decimal_places=6, null=True, db_column="RateMin")
    rate_per = models.DecimalField(
            max_digits=19, decimal_places=6, null=True, db_column="RatePer")
    unit_id = models.ForeignKey(
            Unit, on_delete=models.CASCADE, db_column="UnitID", related_name="+")
    temp_controlled = models.BooleanField(
                default=False, null=False, db_column="TempControlled")

    def __str__(self):
            return str(self.acc_storage_version_id)

    class Meta:
            index_together = (("acc_storage_version_id", "version_num"))
            db_table = 'AccessorialStorage_History'

class CustomerZones(Delete):
        customer_zone_id = models.BigAutoField(
            max_length=8, primary_key=True, null=False, db_column="CustomerZoneID")
        customer_zone_name = models.TextField(
            max_length=40, null=True, blank=False, db_column="CustomerZoneName")
        is_active = models.BooleanField(
            default=False, null=False, db_column="IsActive")
        is_inactive_viewable = models.BooleanField(
            default=False, null=False, db_column="IsInactiveViewable")
        service_point_id = models.ForeignKey(
            ServicePoint, on_delete=models.CASCADE, db_column="ServicePointID", related_name="+")

        def __str__(self):
            return str(self.customer_zone_id)
        class Meta:
            db_table = 'CustomerZones'

class CustomerZonesHistory(Delete):
        version_num = models.IntegerField(
            default=False, null=False, db_column="VersionNum")
        is_latest_version = models.BooleanField(
            default=False, null=False, db_column="IsLatestVersion")
        updated_on = models.DateTimeField(
            default=False, null=False, db_column="UpdatedOn")
        updated_by = models.TextField(
            default=False, null=False, db_column="UpdatedBy")
        base_version = models.IntegerField(
            default=False, null=False, db_column="BaseVersion")
        comments = models.TextField(
            default=False, null=False, db_column="Comments")
        customer_zone_version_id = models.BigAutoField(
            primary_key=True, null=False, db_column="CustomerZoneVersionID")
        customer_zone_id = models.ForeignKey(
            CustomerZones, on_delete=models.CASCADE, db_column="CustomerZoneID", related_name="+")
        customer_zone_name = models.TextField(
            max_length=40, null=True, blank=False, db_column="CustomerZoneName")
        is_active = models.BooleanField(
            default=False, null=False, db_column="IsActive")
        is_inactive_viewable = models.BooleanField(
            default=False, null=False, db_column="IsInactiveViewable")
        service_point_version_id = models.ForeignKey(
            ServicePointHistory, on_delete=models.CASCADE, db_column="ServicePointVersionID", related_name="+")

        def __str__(self):
            return str(self.customer_zone_version_id)

        class Meta:
            index_together = (("customer_zone_version_id", "version_num"))
            db_table = 'CustomerZonesHistory'

class SubPostalCode(Delete):
        sub_postal_code_id = models.BigAutoField(
            max_length=8, primary_key=True, null=False, db_column="SubPostalCodeID")
        sub_postal_code_name = models.TextField(
            max_length=40, null=True, blank=False, db_column="SubPostalCodeName")
        is_active = models.BooleanField(
            default=False, null=False, db_column="IsActive")
        is_inactive_viewable = models.BooleanField(
            default=False, null=False, db_column="IsInactiveViewable")
        postal_code_id = models.ForeignKey(
            PostalCode, on_delete=models.CASCADE, db_column="PostalCodeID", related_name="+")

        def __str__(self):
            return str(self.sub_postal_code_id)
        class Meta:
            db_table = 'SubPostalCode'

class SubPostalCodeHistory(Delete):
        version_num = models.IntegerField(
            default=False, null=False, db_column="VersionNum")
        is_latest_version = models.BooleanField(
            default=False, null=False, db_column="IsLatestVersion")
        updated_on = models.DateTimeField(
            default=False, null=False, db_column="UpdatedOn")
        updated_by = models.TextField(
            default=False, null=False, db_column="UpdatedBy")
        base_version = models.IntegerField(
            default=False, null=False, db_column="BaseVersion")
        comments = models.TextField(
            default=False, null=False, db_column="Comments")
        sub_postal_code_version_id = models.BigAutoField(
            max_length=8, primary_key=True, null=False, db_column="SubPostalCodeVersionID")
        sub_postal_code_id = models.ForeignKey(
            SubPostalCode, on_delete=models.CASCADE, db_column="SubPostalCodeID")
        sub_postal_code_name = models.TextField(
            max_length=40, null=True, blank=False, db_column="SubPostalCodeName")
        is_active = models.BooleanField(
            default=False, null=False, db_column="IsActive")
        is_inactive_viewable = models.BooleanField(
            default=False, null=False, db_column="IsInactiveViewable")
        postal_code_version_id = models.ForeignKey(
            PostalCodeHistory, on_delete=models.CASCADE, db_column="PostalCodeVersionID", related_name="+")

        def __str__(self):
            return str(self.sub_postal_code_version_id)

        class Meta:
            index_together = (("sub_postal_code_version_id", "version_num"))
            db_table = 'SubPostalCodeHistory'

class RequestSection(Delete):
    request_section_id = models.BigAutoField(
        primary_key=True, null=False, db_column="RequestSectionID")
    request_lane = models.ForeignKey(
        RequestLane, on_delete=models.CASCADE, db_column="RequestLaneID")
    rate_base = models.ForeignKey(
        RateBase, null=True, on_delete=models.CASCADE, db_column="RateBaseID")
    override_class = models.ForeignKey(
        FreightClass, null=True, on_delete=models.CASCADE, db_column="OverrideClassID")
    equipment_type = models.ForeignKey(
        EquipmentType, on_delete=models.CASCADE, null=True, db_column="EquipmentTypeID", related_name="+")
    sub_service_level = models.ForeignKey(
        SubServiceLevel, on_delete=models.CASCADE, db_column="SubServiceLevelID")
    weight_break_header = models.ForeignKey(
        WeightBreakHeader, on_delete=models.CASCADE, db_column="WeightBreakHeaderID")
    section_number = models.UUIDField(
        max_length=32, null=False, blank=False, default=uuid.uuid4, db_column="SectionNumber")
    section_name = models.CharField(
        max_length=50, null=False, blank=False, db_column="SectionName")
    weight_break = models.TextField(
        blank=False, default="[]", db_column="WeightBreak")
    is_density_pricing = models.BooleanField(
        null=False, default=False, db_column="IsDensityPricing")
    override_density = models.DecimalField(
        max_digits=19, decimal_places=6, null=True, db_column="OverrideDensity")
    commodity_id = models.ForeignKey(
        Commodity, on_delete=models.CASCADE, null=True, db_column="CommodityID")
    num_lanes = models.IntegerField(
        null=False, blank=False, default=0, db_column="NumLanes")
    num_unpublished_lanes = models.IntegerField(
        null=False, blank=False, default=0, db_column="NumUnpublishedLanes")
    num_edited_lanes = models.IntegerField(
        null=False, blank=False, default=0, db_column="NumEditedLanes")
    num_duplicate_lanes = models.IntegerField(
        null=False, blank=False, default=0, db_column="NumDuplicateLanes")
    num_do_not_meet_commitment_lanes = models.IntegerField(
        null=False, blank=False, default=0, db_column="NumDoNotMeetCommitmentLanes")
    # PAC-1835
    unit_factor = models.DecimalField(
        max_digits=19, decimal_places=6, null=False, default=100, db_column="UnitFactor")
    as_rating = models.BooleanField(
        null=False, default=True, db_column="AsRating")
    has_min = models.BooleanField(
        null=False, default=True, db_column="HasMin")
    has_max = models.BooleanField(
        null=False, default=True, db_column="HasMax")
    base_rate = models.BooleanField(
        null=False, default=True, db_column="BaseRate")

    def __str__(self):
        return str(self.request_section_id)

    class Meta:
        db_table = 'RequestSection'


class RequestSectionHistory(CommentUpdateDelete):
    request_section_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="RequestSectionVersionID")
    request_section = models.ForeignKey(
        RequestSection, on_delete=models.CASCADE, db_column="RequestSectionID")
    request_lane_version = models.ForeignKey(
        RequestLaneHistory, on_delete=models.CASCADE, db_column="RequestLaneVersionID")
    sub_service_level_version = models.ForeignKey(
        SubServiceLevelHistory, on_delete=models.CASCADE, db_column="SubServiceLevelVersionID")
    rate_base_version = models.ForeignKey(
        RateBaseHistory, null=True, on_delete=models.CASCADE, db_column="RateBaseVersionID")
    override_class_version = models.ForeignKey(
        FreightClassHistory, null=True, on_delete=models.CASCADE, db_column="OverrideClassVersionID")
    equipment_type_version = models.ForeignKey(
        EquipmentTypeHistory, null=True, on_delete=models.CASCADE, db_column="EquipmentTypeVersionID")
    weight_break_header_version = models.ForeignKey(
        WeightBreakHeaderHistory, on_delete=models.CASCADE, db_column="WeightBreakHeaderVersionID")
    section_number = models.CharField(
        max_length=32, null=False, blank=False, db_column="SectionNumber")
    section_name = models.CharField(
        max_length=50, null=False, blank=False, db_column="SectionName")
    commodity_id = models.ForeignKey(
        Commodity, on_delete=models.CASCADE, null=True, db_column="CommodityID")
    weight_break = models.TextField(
        blank=False, default="[]", db_column="WeightBreak")
    is_density_pricing = models.BooleanField(
        null=False, default=False, db_column="IsDensityPricing")
    override_density = models.DecimalField(
        max_digits=19, decimal_places=6, null=True, db_column="OverrideDensity")
    num_lanes = models.IntegerField(
        null=False, blank=False, db_column="NumLanes")
    num_unpublished_lanes = models.IntegerField(
        null=False, blank=False, db_column="NumUnpublishedLanes")
    num_edited_lanes = models.IntegerField(
        null=False, blank=False, db_column="NumEditedLanes")
    num_duplicate_lanes = models.IntegerField(
        null=False, blank=False, db_column="NumDuplicateLanes")
    num_do_not_meet_commitment_lanes = models.IntegerField(
        null=False, blank=False, default=0, db_column="NumDoNotMeetCommitmentLanes")

    def __str__(self):
        return str(self.request_section_version_id)

    class Meta:
        # TODO enable indices back when we're fix issues with Django <-> SQL indices

        indexes = [
            models.Index(fields=['request_lane_version'], name='IX1'),
            models.Index(fields=['request_lane_version', 'section_number'], name='IX2'),
            models.Index(fields=['request_section'], name='IX3'),
        ]
        index_together = (('request_section', 'version_num'))
        db_table = 'RequestSection_History'


class RequestSectionLanePointType(Delete):
    request_section_lane_point_type_id = models.BigAutoField(
        primary_key=True, null=False, db_column="RequestSectionLanePointTypeID")
    request_section_lane_point_type_name = models.CharField(
        max_length=50, null=False, blank=False, db_column="RequestSectionLanePointTypeName")
    service_offering = models.ForeignKey(
        ServiceOffering, null=False, on_delete=models.CASCADE, db_column="ServiceOfferingID")
    is_density_pricing = models.BooleanField(
        null=False, default=False, db_column="IsDensityPricing")
    location_hierarchy = models.IntegerField(
        null=False, blank=False, db_column="LocationHierarchy")
    is_group_type = models.BooleanField(
        null=False, default=False, db_column="IsGroupType")
    is_point_type = models.BooleanField(
        null=False, default=False, db_column="IsPointType")

    def __str__(self):
        return str(self.request_section_lane_point_type_id)

    class Meta:
        db_table = 'RequestSectionLanePointType'


class RequestSectionLanePointTypeHistory(CommentUpdateDelete):
    request_section_lane_point_type_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="RequestSectionLanePointTypeVersionID")
    request_section_lane_point_type = models.ForeignKey(
        RequestSectionLanePointType, null=False, on_delete=models.CASCADE, db_column="RequestSectionLanePointTypeID")
    request_section_lane_point_type_name = models.CharField(
        max_length=50, null=False, blank=False, db_column="RequestSectionLanePointTypeName")
    service_offering_version = models.ForeignKey(
        ServiceOfferingHistory, null=False, on_delete=models.CASCADE, db_column="ServiceOfferingVersionID")
    is_density_pricing = models.BooleanField(
        null=False, default=False, db_column="IsDensityPricing")
    location_hierarchy = models.IntegerField(
        null=False, blank=False, db_column="LocationHierarchy")
    is_group_type = models.BooleanField(
        null=False, default=False, db_column="IsGroupType")
    is_point_type = models.BooleanField(
        null=False, default=False, db_column="IsPointType")

    def __str__(self):
        return str(self.request_section_lane_point_type_version_id)

    class Meta:
        index_together = (('request_section_lane_point_type', 'version_num'))
        db_table = 'RequestSectionLanePointType_History'


class RequestSectionLane(Delete):
    request_section_lane_id = models.BigAutoField(
        primary_key=True, null=False, db_column="RequestSectionLaneID")
    request_section = models.ForeignKey(
        RequestSection, on_delete=models.CASCADE, db_column="RequestSectionID")
    origin_province = models.ForeignKey(
        Province, on_delete=models.CASCADE, null=True, db_column="OriginProvinceID", related_name="+")
    origin_region = models.ForeignKey(
        Region, on_delete=models.CASCADE, null=True, db_column="OriginRegionID", related_name="+")
    origin_country = models.ForeignKey(
        Country, on_delete=models.CASCADE, null=True, db_column="OriginCountryID", related_name="+")
    origin_terminal = models.ForeignKey(
        Terminal, on_delete=models.CASCADE, null=True, db_column="OriginTerminalID", related_name="+")
    origin_zone = models.ForeignKey(
        Zone, on_delete=models.CASCADE, null=True, db_column="OriginZoneID", related_name="+")
    origin_basing_point = models.ForeignKey(
        BasingPoint, on_delete=models.CASCADE, null=True, db_column="OriginBasingPointID", related_name="+")
    origin_service_point = models.ForeignKey(
        ServicePoint, on_delete=models.CASCADE, null=True, db_column="OriginServicePointID", related_name="+")
    origin_postal_code = models.ForeignKey(
        PostalCode, on_delete=models.CASCADE, null=True, db_column="OriginPostalCodeID", related_name="+")
    origin_point_type = models.ForeignKey(
        RequestSectionLanePointType, on_delete=models.CASCADE, db_column="OriginPointTypeID", related_name="+")
    destination_province = models.ForeignKey(
        Province, on_delete=models.CASCADE, null=True, db_column="DestinationProvinceID", related_name="+")
    destination_region = models.ForeignKey(
        Region, on_delete=models.CASCADE, null=True, db_column="DestinationRegionID", related_name="+")
    destination_country = models.ForeignKey(
        Country, on_delete=models.CASCADE, null=True, db_column="DestinationCountryID", related_name="+")
    destination_terminal = models.ForeignKey(
        Terminal, on_delete=models.CASCADE, null=True, db_column="DestinationTerminalID", related_name="+")
    destination_zone = models.ForeignKey(
        Zone, on_delete=models.CASCADE, null=True, db_column="DestinationZoneID", related_name="+")
    destination_basing_point = models.ForeignKey(
        BasingPoint, on_delete=models.CASCADE, null=True, db_column="DestinationBasingPointID", related_name="+")
    destination_service_point = models.ForeignKey(
        ServicePoint, on_delete=models.CASCADE, null=True, db_column="DestinationServicePointID", related_name="+")
    destination_postal_code = models.ForeignKey(
        PostalCode, on_delete=models.CASCADE, null=True, db_column="DestinationPostalCodeID", related_name="+")
    destination_point_type = models.ForeignKey(
        RequestSectionLanePointType, on_delete=models.CASCADE, db_column="DestinationPointTypeID", related_name="+")
    origin_province_code = models.CharField(
        max_length=2, null=True, blank=False, db_column="OriginProvinceCode")
    origin_region_code = models.CharField(
        max_length=4, null=True, blank=False, db_column="OriginRegionCode")
    origin_country_code = models.CharField(
        max_length=2, null=True, blank=False, db_column="OriginCountryCode")
    origin_terminal_code = models.CharField(
        max_length=3, null=True, blank=False, db_column="OriginTerminalCode")
    origin_zone_name = models.CharField(
        max_length=50, null=True, blank=False, db_column="OriginZoneName")
    origin_basing_point_name = models.CharField(
        max_length=50, null=True, blank=False, db_column="OriginBasingPointName")
    origin_service_point_name = models.CharField(
        max_length=50, null=True, blank=False, db_column="OriginServicePointName")
    origin_postal_code_name = models.CharField(
        max_length=10, null=True, blank=False, db_column="OriginPostalCodeName")
    origin_point_type_name = models.CharField(
        max_length=50, blank=False, db_column="OriginPointTypeName")
    origin_code = models.CharField(
        max_length=50, blank=False, db_column="OriginCode")
    destination_province_code = models.CharField(
        max_length=2, null=True, blank=False, db_column="DestinationProvinceCode")
    destination_region_code = models.CharField(
        max_length=4, null=True, blank=False, db_column="DestinationRegionCode")
    destination_country_code = models.CharField(
        max_length=2, null=True, blank=False, db_column="DestinationCountryCode")
    destination_terminal_code = models.CharField(
        max_length=3, null=True, blank=False, db_column="DestinationTerminalCode")
    destination_zone_name = models.CharField(
        max_length=50, null=True, blank=False, db_column="DestinationZoneName")
    destination_basing_point_name = models.CharField(
        max_length=50, null=True, blank=False, db_column="DestinationBasingPointName")
    destination_service_point_name = models.CharField(
        max_length=50, null=True, blank=False, db_column="DestinationServicePointName")
    destination_postal_code_name = models.CharField(
        max_length=10, null=True, blank=False, db_column="DestinationPostalCodeName")
    destination_point_type_name = models.CharField(
        max_length=50, blank=False, db_column="DestinationPointTypeName")
    destination_code = models.CharField(
        max_length=50, blank=False, db_column="DestinationCode")
    lane_number = models.CharField(
        max_length=32, null=False, blank=False, db_column="LaneNumber")
    is_published = models.BooleanField(
        null=False, default=False, db_column="IsPublished")
    is_edited = models.BooleanField(
        null=False, default=False, db_column="IsEdited")
    is_duplicate = models.BooleanField(
        null=False, default=False, db_column="IsDuplicate")
    is_between = models.BooleanField(
        null=False, default=False, db_column="IsBetween")
    is_lane_group = models.BooleanField(
        null=False, default=False, db_column="IsLaneGroup")
    basing_point_hash_code = models.BinaryField(null=True, db_column="BasingPointHashCode")
    lane_hash_code = models.BinaryField(null=False, db_column="LaneHashCode")
    commitment = models.TextField(
        blank=False, default="[]", db_column="Commitment")
    customer_rate = models.TextField(
        blank=False, default="[]", db_column="CustomerRate")
    customer_discount = models.TextField(
        blank=False, default="[]", db_column="CustomerDiscount")
    dr_rate = models.TextField(blank=False, default="[]", db_column="DrRate")
    partner_rate = models.TextField(
        blank=False, default="[]", db_column="PartnerRate")
    partner_discount = models.TextField(
        blank=False, default="[]", db_column="PartnerDiscount")
    profitability = models.TextField(
        blank=False, default="[]", db_column="Profitability")
    pickup_count = models.IntegerField(
        null=True, blank=False, default=0, db_column="PickupCount")
    delivery_count = models.IntegerField(
        null=True, blank=False, default=0, db_column="DeliveryCount")
    dock_adjustment = models.DecimalField(
        max_digits=19, decimal_places=6, null=True, db_column="DockAdjustment")
    margin = models.TextField(blank=False, default="[]", db_column="Margin")
    density = models.TextField(blank=False, default="[]", db_column="Density")
    pickup_cost = models.TextField(
        blank=False, default="[]", db_column="PickupCost")
    delivery_cost = models.TextField(
        blank=False, default="[]", db_column="DeliveryCost")
    accessorials_value = models.TextField(
        blank=False, default="[]", db_column="AccessorialsValue")
    accessorials_percentage = models.TextField(
        blank=False, default="[]", db_column="AccessorialsPercentage")
    # PAC-1729
    cost_override_pickup_count = models.IntegerField(
        null=True, blank=False, default=0, db_column="CostOverridePickupCount")
    cost_override_delivery_count = models.IntegerField(
        null=True, blank=False, default=0, db_column="CostOverrideDeliveryCount")
    cost_override_dock_adjustment = models.DecimalField(
        max_digits=19, decimal_places=6, null=True, db_column="CostOverrideDockAdjustment")
    cost_override_margin = models.TextField(null=True, blank=False, default="[]", db_column="CostOverrideMargin")
    cost_override_density = models.TextField(null=True, blank=False, default="[]", db_column="CostOverrideDensity")
    cost_override_pickup_cost = models.TextField(
        null=True, blank=True, default="[]", db_column="CostOverridePickupCost")
    cost_override_delivery_cost = models.TextField(
        null=True, blank=True, default="[]", db_column="CostOverrideDeliveryCost")
    cost_override_accessorials_value = models.TextField(
        null=True, blank=True, default="[]", db_column="CostOverrideAccessorialsValue")
    cost_override_accessorials_percentage = models.TextField(
        null=True, blank=True, default="[]", db_column="CostOverrideAccessorialsPercentage")

    do_not_meet_commitment = models.BooleanField(
        null=False, default=False, db_column="DoNotMeetCommitment")

    pricing_rates = models.TextField(null=True, default="[]", db_column="PricingRates")
    workflow_errors = models.TextField(null=True, default=None, db_column="WorkflowErrors")
    is_excluded = models.BooleanField(
        null=True, default=False, db_column="IsExcluded")
    is_flagged = models.BooleanField(
        null=True, default=False, db_column="IsFlagged")

    def __str__(self):
        return str(self.request_section_lane_id)

    class Meta:
        db_table = 'RequestSectionLane'


class RequestSectionLaneHistory(CommentUpdateDelete):
    request_section_lane_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="RequestSectionLaneVersionID")
    request_section_lane = models.ForeignKey(
        RequestSectionLane, on_delete=models.CASCADE, db_column="RequestSectionLaneID")
    request_section_version = models.ForeignKey(
        RequestSectionHistory, on_delete=models.CASCADE, db_column="RequestSectionVersionID")
    origin_province_version = models.ForeignKey(
        ProvinceHistory, on_delete=models.CASCADE, null=True, db_column="OriginProvinceVersionID", related_name="+")
    origin_region_version = models.ForeignKey(
        RegionHistory, on_delete=models.CASCADE, null=True, db_column="OriginRegionVersionID", related_name="+")
    origin_country_version = models.ForeignKey(
        CountryHistory, on_delete=models.CASCADE, null=True, db_column="OriginCountryVersionID", related_name="+")
    origin_terminal_version = models.ForeignKey(
        TerminalHistory, on_delete=models.CASCADE, null=True, db_column="OriginTerminalVersionID", related_name="+")
    origin_zone_version = models.ForeignKey(
        ZoneHistory, on_delete=models.CASCADE, null=True, db_column="OriginZoneVersionID", related_name="+")
    origin_basing_point_version = models.ForeignKey(
        BasingPointHistory, on_delete=models.CASCADE, null=True, db_column="OriginBasingPointVersionID",
        related_name="+")
    origin_service_point_version = models.ForeignKey(
        ServicePointHistory, on_delete=models.CASCADE, null=True, db_column="OriginServicePointVersionID",
        related_name="+")
    origin_postal_code_version = models.ForeignKey(
        PostalCodeHistory, on_delete=models.CASCADE, null=True, db_column="OriginPostalCodeVersionID", related_name="+")
    origin_point_type_version = models.ForeignKey(
        RequestSectionLanePointTypeHistory, on_delete=models.CASCADE, db_column="OriginPointTypeVersionID",
        related_name="+")
    destination_province_version = models.ForeignKey(
        ProvinceHistory, on_delete=models.CASCADE, null=True, db_column="DestinationProvinceVersionID",
        related_name="+")
    destination_region_version = models.ForeignKey(
        RegionHistory, on_delete=models.CASCADE, null=True, db_column="DestinationRegionVersionID", related_name="+")
    destination_country_version = models.ForeignKey(
        CountryHistory, on_delete=models.CASCADE, null=True, db_column="DestinationCountryVersionID", related_name="+")
    destination_terminal_version = models.ForeignKey(
        TerminalHistory, on_delete=models.CASCADE, null=True, db_column="DestinationTerminalVersionID",
        related_name="+")
    destination_zone_version = models.ForeignKey(
        ZoneHistory, on_delete=models.CASCADE, null=True, db_column="DestinationZoneVersionID", related_name="+")
    destination_basing_point_version = models.ForeignKey(
        BasingPointHistory, on_delete=models.CASCADE, null=True, db_column="DestinationBasingPointVersionID",
        related_name="+")
    destination_service_point_version = models.ForeignKey(
        ServicePointHistory, on_delete=models.CASCADE, null=True, db_column="DestinationServicePointVersionID",
        related_name="+")
    destination_postal_code_version = models.ForeignKey(
        PostalCodeHistory, on_delete=models.CASCADE, null=True, db_column="DestinationPostalCodeVersionID",
        related_name="+")
    destination_point_type_version = models.ForeignKey(
        RequestSectionLanePointTypeHistory, on_delete=models.CASCADE, db_column="DestinationPointTypeVersionID",
        related_name="+")
    origin_province_code = models.CharField(
        max_length=2, null=True, blank=False, db_column="OriginProvinceCode")
    origin_region_code = models.CharField(
        max_length=4, null=True, blank=False, db_column="OriginRegionCode")
    origin_country_code = models.CharField(
        max_length=2, null=True, blank=False, db_column="OriginCountryCode")
    origin_terminal_code = models.CharField(
        max_length=3, null=True, blank=False, db_column="OriginTerminalCode")
    origin_zone_name = models.CharField(
        max_length=50, null=True, blank=False, db_column="OriginZoneName")
    origin_basing_point_name = models.CharField(
        max_length=50, null=True, blank=False, db_column="OriginBasingPointName")
    origin_service_point_name = models.CharField(
        max_length=50, null=True, blank=False, db_column="OriginServicePointName")
    origin_postal_code_name = models.CharField(
        max_length=10, null=True, blank=False, db_column="OriginPostalCodeName")
    origin_point_type_name = models.CharField(
        max_length=50, blank=False, db_column="OriginPointTypeName")
    origin_code = models.CharField(
        max_length=50, blank=False, db_column="OriginCode")
    destination_province_code = models.CharField(
        max_length=2, null=True, blank=False, db_column="DestinationProvinceCode")
    destination_region_code = models.CharField(
        max_length=4, null=True, blank=False, db_column="DestinationRegionCode")
    destination_country_code = models.CharField(
        max_length=2, null=True, blank=False, db_column="DestinationCountryCode")
    destination_terminal_code = models.CharField(
        max_length=3, null=True, blank=False, db_column="DestinationTerminalCode")
    destination_zone_name = models.CharField(
        max_length=50, null=True, blank=False, db_column="DestinationZoneName")
    destination_basing_point_name = models.CharField(
        max_length=50, null=True, blank=False, db_column="DestinationBasingPointName")
    destination_service_point_name = models.CharField(
        max_length=50, null=True, blank=False, db_column="DestinationServicePointName")
    destination_postal_code_name = models.CharField(
        max_length=10, null=True, blank=False, db_column="DestinationPostalCodeName")
    destination_point_type_name = models.CharField(
        max_length=50, blank=False, db_column="DestinationPointTypeName")
    destination_code = models.CharField(
        max_length=50, blank=False, db_column="DestinationCode")
    lane_number = models.CharField(
        max_length=32, null=False, blank=False, db_column="LaneNumber")
    is_published = models.BooleanField(
        null=False, default=False, db_column="IsPublished")
    is_edited = models.BooleanField(
        null=False, default=False, db_column="IsEdited")
    is_duplicate = models.BooleanField(
        null=False, default=False, db_column="IsDuplicate")
    is_between = models.BooleanField(
        null=False, default=False, db_column="IsBetween")
    is_lane_group = models.BooleanField(
        null=False, default=False, db_column="IsLaneGroup")
    basing_point_hash_code = models.BinaryField(null=True, db_column="BasingPointHashCode")
    lane_hash_code = models.BinaryField(null=False, db_column="LaneHashCode")
    commitment = models.TextField(
        blank=False, default="[]", db_column="Commitment")
    customer_rate = models.TextField(
        blank=False, default="[]", db_column="CustomerRate")
    customer_discount = models.TextField(
        blank=False, default="[]", db_column="CustomerDiscount")
    dr_rate = models.TextField(blank=False, default="[]", db_column="DrRate")
    partner_rate = models.TextField(
        blank=False, default="[]", db_column="PartnerRate")
    partner_discount = models.TextField(
        blank=False, default="[]", db_column="PartnerDiscount")
    profitability = models.TextField(
        blank=False, default="[]", db_column="Profitability")
    pickup_count = models.IntegerField(
        null=True, blank=False, default=0, db_column="PickupCount")
    delivery_count = models.IntegerField(
        null=True, blank=False, default=0, db_column="DeliveryCount")
    dock_adjustment = models.DecimalField(
        max_digits=19, decimal_places=6, null=True, db_column="DockAdjustment")
    margin = models.TextField(blank=False, default="[]", db_column="Margin")
    density = models.TextField(blank=False, default="[]", db_column="Density")
    pickup_cost = models.TextField(
        blank=False, default="[]", db_column="PickupCost")
    delivery_cost = models.TextField(
        blank=False, default="[]", db_column="DeliveryCost")
    accessorials_value = models.TextField(
        blank=False, default="[]", db_column="AccessorialsValue")
    accessorials_percentage = models.TextField(
        blank=False, default="[]", db_column="AccessorialsPercentage")
    # PAC-1729
    cost_override_pickup_count = models.IntegerField(
        null=True, blank=False, default=0, db_column="CostOverridePickupCount")
    cost_override_delivery_count = models.IntegerField(
        null=True, blank=False, default=0, db_column="CostOverrideDeliveryCount")
    cost_override_dock_adjustment = models.DecimalField(
        max_digits=19, decimal_places=6, null=True, db_column="CostOverrideDockAdjustment")
    cost_override_margin = models.TextField(null=True, blank=False, default="[]", db_column="CostOverrideMargin")
    cost_override_density = models.TextField(null=True, blank=False, default="[]", db_column="CostOverrideDensity")
    cost_override_pickup_cost = models.TextField(
        null=True, blank=True, default="[]", db_column="CostOverridePickupCost")
    cost_override_delivery_cost = models.TextField(
        null=True, blank=True, default="[]", db_column="CostOverrideDeliveryCost")
    cost_override_accessorials_value = models.TextField(
        null=True, blank=True, default="[]", db_column="CostOverrideAccessorialsValue")
    cost_override_accessorials_percentage = models.TextField(
        null=True, blank=True, default="[]", db_column="CostOverrideAccessorialsPercentage")

    do_not_meet_commitment = models.BooleanField(
        null=False, default=False, db_column="DoNotMeetCommitment")

    pricing_rates = models.TextField(null=True, default="[]", db_column="PricingRates")
    workflow_errors = models.TextField(null=True, default=None, db_column="WorkflowErrors")
    is_excluded = models.BooleanField(
        null=True, default=False, db_column="IsExcluded")
    is_flagged = models.BooleanField(
        null=True, default=False, db_column="IsFlagged")

    def __str__(self):
        return str(self.request_section_lane_version_id)

    class Meta:
        index_together = (('request_section_lane', 'version_num'))
        db_table = 'RequestSectionLane_History'


class RequestSectionLaneStaging(Delete):
    request_section_lane_staging_id = models.BigAutoField(
        primary_key=True, null=False, db_column="RequestSectionLaneStagingID")
    request_section_lane_id = models.IntegerField(
        null=False, db_column="RequestSectionLaneID")
    request_section_id = models.IntegerField(
        null=False, db_column="RequestSectionID")
    request_lane_id = models.IntegerField(
        null=False, db_column="RequestLaneID")
    origin_province_id = models.IntegerField(
        null=True, db_column="OriginProvinceID")
    origin_region_id = models.IntegerField(
        null=True, db_column="OriginRegionID")
    origin_country_id = models.IntegerField(
        null=True, db_column="OriginCountryID")
    origin_terminal_id = models.IntegerField(
        null=True, db_column="OriginTerminalID")
    origin_zone_id = models.IntegerField(
        null=True, db_column="OriginZoneID")
    origin_basing_point_id = models.IntegerField(
        null=True, db_column="OriginBasingPointID")
    origin_service_point_id = models.IntegerField(
        null=True, db_column="OriginServicePointID")
    origin_postal_code_id = models.IntegerField(
        null=True, db_column="OriginPostalCodeID")
    origin_point_type_id = models.IntegerField(
        db_column="OriginPointTypeID")
    destination_province_id = models.IntegerField(
        null=True, db_column="DestinationProvinceID")
    destination_region_id = models.IntegerField(
        null=True, db_column="DestinationRegionID")
    destination_country_id = models.IntegerField(
        null=True, db_column="DestinationCountryID")
    destination_terminal_id = models.IntegerField(
        null=True, db_column="DestinationTerminalID")
    destination_zone_id = models.IntegerField(
        null=True, db_column="DestinationZoneID")
    destination_basing_point_id = models.IntegerField(
        null=True, db_column="DestinationBasingPointID")
    destination_service_point_id = models.IntegerField(
        null=True, db_column="DestinationServicePointID")
    destination_postal_code_id = models.IntegerField(
        null=True, db_column="DestinationPostalCodeID")
    destination_point_type_id = models.IntegerField(
        null=True, db_column="DestinationPointTypeID")
    origin_province_code = models.CharField(
        max_length=2, null=True, blank=False, db_column="OriginProvinceCode")
    origin_region_code = models.CharField(
        max_length=4, null=True, blank=False, db_column="OriginRegionCode")
    origin_country_code = models.CharField(
        max_length=2, null=True, blank=False, db_column="OriginCountryCode")
    origin_terminal_code = models.CharField(
        max_length=3, null=True, blank=False, db_column="OriginTerminalCode")
    origin_zone_name = models.CharField(
        max_length=50, null=True, blank=False, db_column="OriginZoneName")
    origin_basing_point_name = models.CharField(
        max_length=50, null=True, blank=False, db_column="OriginBasingPointName")
    origin_service_point_name = models.CharField(
        max_length=50, null=True, blank=False, db_column="OriginServicePointName")
    origin_postal_code_name = models.CharField(
        max_length=10, null=True, blank=False, db_column="OriginPostalCodeName")
    origin_point_type_name = models.CharField(
        max_length=50, blank=False, db_column="OriginPointTypeName")
    origin_code = models.CharField(
        max_length=50, blank=False, db_column="OriginCode")
    destination_province_code = models.CharField(
        max_length=2, null=True, blank=False, db_column="DestinationProvinceCode")
    destination_region_code = models.CharField(
        max_length=4, null=True, blank=False, db_column="DestinationRegionCode")
    destination_country_code = models.CharField(
        max_length=2, null=True, blank=False, db_column="DestinationCountryCode")
    destination_terminal_code = models.CharField(
        max_length=3, null=True, blank=False, db_column="DestinationTerminalCode")
    destination_zone_name = models.CharField(
        max_length=50, null=True, blank=False, db_column="DestinationZoneName")
    destination_basing_point_name = models.CharField(
        max_length=50, null=True, blank=False, db_column="DestinationBasingPointName")
    destination_service_point_name = models.CharField(
        max_length=50, null=True, blank=False, db_column="DestinationServicePointName")
    destination_postal_code_name = models.CharField(
        max_length=10, null=True, blank=False, db_column="DestinationPostalCodeName")
    destination_point_type_name = models.CharField(
        max_length=50, blank=False, db_column="DestinationPointTypeName")
    destination_code = models.CharField(
        max_length=50, blank=False, db_column="DestinationCode")
    lane_number = models.CharField(
        max_length=32, null=False, blank=False, db_column="LaneNumber")
    is_published = models.BooleanField(
        null=False, default=False, db_column="IsPublished")
    is_edited = models.BooleanField(
        null=False, default=False, db_column="IsEdited")
    is_duplicate = models.BooleanField(
        null=False, default=False, db_column="IsDuplicate")
    is_between = models.BooleanField(
        null=False, default=False, db_column="IsBetween")
    is_lane_group = models.BooleanField(
        null=False, default=False, db_column="IsLaneGroup")
    basing_point_hash_code = models.BinaryField(null=True, db_column="BasingPointHashCode")
    lane_hash_code = models.BinaryField(null=False, db_column="LaneHashCode")
    new_is_between = models.BooleanField(
        null=False, default=False, db_column="NewIsBetween")
    new_is_active = models.BooleanField(
        null=False, default=False, db_column="NewIsActive")
    new_is_inactive_viewable = models.BooleanField(
        null=False, default=False, db_column="NewIsInactiveViewable")
    is_updated = models.BooleanField(
        null=False, default=False, db_column="IsUpdated")
    context_id = models.CharField(
        max_length=32, null=False, blank=False, db_column="ContextID")
    context_created_on = models.CharField(
        max_length=20, null=False, db_column="ContextCreatedOn")
    commitment = models.TextField(
        blank=False, default="[]", db_column="Commitment")
    new_commitment = models.TextField(
        blank=False, default="[]", db_column="NewCommitment")
    customer_rate = models.TextField(
        blank=False, default="[]", db_column="CustomerRate")
    new_customer_rate = models.TextField(
        blank=False, default="[]", db_column="NewCustomerRate")
    customer_discount = models.TextField(
        blank=False, default="[]", db_column="CustomerDiscount")
    new_customer_discount = models.TextField(
        blank=False, default="[]", db_column="NewCustomerDiscount")
    dr_rate = models.TextField(blank=False, default="[]", db_column="DrRate")
    new_dr_rate = models.TextField(
        blank=False, default="[]", db_column="NewDrRate")
    partner_rate = models.TextField(
        blank=False, default="[]", db_column="PartnerRate")
    new_partner_rate = models.TextField(
        blank=False, default="[]", db_column="NewPartnerRate")
    partner_discount = models.TextField(
        blank=False, default="[]", db_column="PartnerDiscount")
    new_partner_discount = models.TextField(
        blank=False, default="[]", db_column="NewPartnerDiscount")
    profitability = models.TextField(
        blank=False, default="[]", db_column="Profitability")
    new_profitability = models.TextField(
        blank=False, default="[]", db_column="NewProfitability")
    pickup_count = models.IntegerField(
        null=True, blank=False, default=0, db_column="PickupCount")
    new_pickup_count = models.IntegerField(
        null=True, blank=False, default=0, db_column="NewPickupCount")
    delivery_count = models.IntegerField(
        null=True, blank=False, default=0, db_column="DeliveryCount")
    new_delivery_count = models.IntegerField(
        null=True, blank=False, default=0, db_column="NewDeliveryCount")
    dock_adjustment = models.DecimalField(
        max_digits=19, decimal_places=6, null=True, db_column="DockAdjustment")
    new_dock_adjustment = models.DecimalField(
        max_digits=19, decimal_places=6, null=True, db_column="NewDockAdjustment")
    margin = models.TextField(blank=False, default="[]", db_column="Margin")
    new_margin = models.TextField(
        blank=False, default="[]", db_column="NewMargin")
    density = models.TextField(blank=False, default="[]", db_column="Density")
    new_density = models.TextField(
        blank=False, default="[]", db_column="NewDensity")
    pickup_cost = models.TextField(
        blank=False, default="[]", db_column="PickupCost")
    new_pickup_cost = models.TextField(
        blank=False, default="[]", db_column="NewPickupCost")
    delivery_cost = models.TextField(
        blank=False, default="[]", db_column="DeliveryCost")
    new_delivery_cost = models.TextField(
        blank=False, default="[]", db_column="NewDeliveryCost")
    accessorials_value = models.TextField(
        blank=False, default="[]", db_column="AccessorialsValue")
    new_accessorials_value = models.TextField(
        blank=False, default="[]", db_column="NewAccessorialsValue")
    accessorials_percentage = models.TextField(
        blank=False, default="[]", db_column="AccessorialsPercentage")
    new_accessorials_percentage = models.TextField(
        blank=False, default="[]", db_column="NewAccessorialsPercentage")
    do_not_meet_commitment = models.BooleanField(
        null=False, default=False, db_column="DoNotMeetCommitment")
    new_do_not_meet_commitment = models.BooleanField(
        null=False, default=False, db_column="NewDoNotMeetCommitment")
    pricing_rates = models.TextField(null=True, default="[]", db_column="PricingRates")
    workflow_errors = models.TextField(null=True, default=None, db_column="WorkflowErrors")

    def __str__(self):
        return str(self.request_section_lane_staging_id)

    class Meta:
        db_table = 'RequestSectionLane_Staging'


class RequestSectionLanePricingPoint(Delete):
    request_section_lane_pricing_point_id = models.BigAutoField(
        primary_key=True, null=False, db_column="RequestSectionLanePricingPointID")
    request_section_lane = models.ForeignKey(
        RequestSectionLane, on_delete=models.CASCADE, db_column="RequestSectionLaneID")
    origin_postal_code = models.ForeignKey(
        PostalCode, on_delete=models.CASCADE, null=False, db_column="OriginPostalCodeID", related_name="+")
    destination_postal_code = models.ForeignKey(
        PostalCode, on_delete=models.CASCADE, null=False, db_column="DestinationPostalCodeID", related_name="+")
    origin_postal_code_name = models.CharField(
        max_length=10, null=False, blank=False, db_column="OriginPostalCodeName")
    destination_postal_code_name = models.CharField(
        max_length=10, null=False, blank=False, db_column="DestinationPostalCodeName")
    pricing_point_number = models.CharField(
        max_length=32, null=False, blank=False, db_column="PricingPointNumber")
    pricing_point_hash_code = models.BinaryField(null=False, db_column="PricingPointHashCode")
    cost = models.TextField(null=False, db_column="Cost")
    dr_rate = models.TextField(blank=False, default="[]", db_column="DrRate")
    fak_rate = models.TextField(blank=False, default="[]", db_column="FakRate")
    profitability = models.TextField(
        blank=False, default="[]", db_column="Profitability")
    splits_all = models.TextField(
        blank=False, default="[]", db_column="SplitsAll")
    splits_all_usage_percentage = models.DecimalField(
        max_digits=19, decimal_places=6, null=True, db_column="SplitsAllUsagePercentage")
    pickup_count = models.IntegerField(
        null=True, blank=False, default=0, db_column="PickupCount")
    delivery_count = models.IntegerField(
        null=True, blank=False, default=0, db_column="DeliveryCount")
    dock_adjustment = models.DecimalField(
        max_digits=19, decimal_places=6, null=True, db_column="DockAdjustment")
    margin = models.TextField(blank=False, default="[]", db_column="Margin")
    density = models.TextField(blank=False, default="[]", db_column="Density")
    pickup_cost = models.TextField(
        blank=False, default="[]", db_column="PickupCost")
    delivery_cost = models.TextField(
        blank=False, default="[]", db_column="DeliveryCost")
    accessorials_value = models.TextField(
        blank=False, default="[]", db_column="AccessorialsValue")
    accessorials_percentage = models.TextField(
        blank=False, default="[]", db_column="AccessorialsPercentage")

    # 1837
    cost_override_pickup_count = models.IntegerField(
        null=True, blank=False, default=0, db_column="CostOverridePickupCount")
    cost_override_delivery_count = models.IntegerField(
        null=True, blank=False, default=0, db_column="CostOverrideDeliveryCount")
    cost_override_dock_adjustment = models.DecimalField(
        max_digits=19, decimal_places=6, null=True, db_column="CostOverrideDockAdjustment")
    cost_override_margin = models.TextField(blank=False, null=True, default="[]", db_column="CostOverrideMargin")
    cost_override_density = models.TextField(blank=False, null=True, default="[]", db_column="CostOverrideDensity")
    cost_override_pickup_cost = models.TextField(blank=True, null=True, default="[]",
                                                 db_column="CostOverridePickupCost")
    cost_override_delivery_cost = models.TextField(blank=True, null=True, default="[]",
                                                   db_column="CostOverrideDeliveryCost")
    cost_override_accessorials_value = models.TextField(
        blank=True, null=True, default="[]", db_column="CostOverrideAccessorialsValue")
    cost_override_accessorials_percentage = models.TextField(
        blank=True, null=True, default="[]", db_column="CostOverrideAccessorialsPercentage")

    pricing_rates = models.TextField(null=True, default="[]", db_column="PricingRates")
    workflow_errors = models.TextField(null=True, default=None, db_column="WorkflowErrors")

    def __str__(self):
        return str(self.request_section_lane_pricing_point_id)

    class Meta:
        db_table = 'RequestSectionLanePricingPoint'


class RequestSectionLanePricingPointHistory(CommentUpdateDelete):
    request_section_lane_pricing_point_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="RequestSectionLanePricingPointVersionID")
    request_section_lane_pricing_point = models.ForeignKey(
        RequestSectionLanePricingPoint, on_delete=models.CASCADE, db_column="RequestSectionLanePricingPointID")
    request_section_lane_version = models.ForeignKey(
        RequestSectionLaneHistory, on_delete=models.CASCADE, db_column="RequestSectionLaneVersionID")
    origin_postal_code_version = models.ForeignKey(
        PostalCodeHistory, on_delete=models.CASCADE, null=False, db_column="OriginPostalCodeVersionID",
        related_name="+")
    destination_postal_code_version = models.ForeignKey(
        PostalCodeHistory, on_delete=models.CASCADE, null=False, db_column="DestinationPostalCodeVersionID",
        related_name="+")
    origin_postal_code_name = models.CharField(
        max_length=10, null=False, blank=False, db_column="OriginPostalCodeName")
    destination_postal_code_name = models.CharField(
        max_length=10, null=False, blank=False, db_column="DestinationPostalCodeName")
    pricing_point_number = models.CharField(
        max_length=32, null=False, blank=False, db_column="PricingPointNumber")
    pricing_point_hash_code = models.BinaryField(null=False, db_column="PricingPointHashCode")
    cost = models.TextField(null=False, db_column="Cost")
    dr_rate = models.TextField(blank=False, default="[]", db_column="DrRate")
    fak_rate = models.TextField(blank=False, default="[]", db_column="FakRate")
    profitability = models.TextField(
        blank=False, default="[]", db_column="Profitability")
    splits_all = models.TextField(
        blank=False, default="[]", db_column="SplitsAll")
    splits_all_usage_percentage = models.DecimalField(
        max_digits=19, decimal_places=6, null=True, db_column="SplitsAllUsagePercentage")
    pickup_count = models.IntegerField(
        null=True, blank=False, default=0, db_column="PickupCount")
    delivery_count = models.IntegerField(
        null=True, blank=False, default=0, db_column="DeliveryCount")
    dock_adjustment = models.DecimalField(
        max_digits=19, decimal_places=6, null=True, db_column="DockAdjustment")
    margin = models.TextField(blank=False, default="[]", db_column="Margin")
    density = models.TextField(blank=False, default="[]", db_column="Density")
    pickup_cost = models.TextField(
        blank=False, default="[]", db_column="PickupCost")
    delivery_cost = models.TextField(
        blank=False, default="[]", db_column="DeliveryCost")
    accessorials_value = models.TextField(
        blank=False, default="[]", db_column="AccessorialsValue")
    accessorials_percentage = models.TextField(
        blank=False, default="[]", db_column="AccessorialsPercentage")

    # 1837
    cost_override_pickup_count = models.IntegerField(
        null=True, blank=False, default=0, db_column="CostOverridePickupCount")
    cost_override_delivery_count = models.IntegerField(
        null=True, blank=False, default=0, db_column="CostOverrideDeliveryCount")
    cost_override_dock_adjustment = models.DecimalField(
        max_digits=19, decimal_places=6, null=True, db_column="CostOverrideDockAdjustment")
    cost_override_margin = models.TextField(blank=False, null=True, default="[]", db_column="CostOverrideMargin")
    cost_override_density = models.TextField(blank=False, null=True, default="[]", db_column="CostOverrideDensity")
    cost_override_pickup_cost = models.TextField(blank=True, null=True, default="[]",
                                                 db_column="CostOverridePickupCost")
    cost_override_delivery_cost = models.TextField(blank=True, null=True, default="[]",
                                                   db_column="CostOverrideDeliveryCost")
    cost_override_accessorials_value = models.TextField(
        blank=True, null=True, default="[]", db_column="CostOverrideAccessorialsValue")
    cost_override_accessorials_percentage = models.TextField(
        blank=True, null=True, default="[]", db_column="CostOverrideAccessorialsPercentage")

    pricing_rates = models.TextField(null=True, default="[]", db_column="PricingRates")
    workflow_errors = models.TextField(null=True, default=None, db_column="WorkflowErrors")

    def __str__(self):
        return str(self.request_section_lane_pricing_point_version_id)

    class Meta:
        index_together = (
            ('request_section_lane_pricing_point', 'version_num'))
        db_table = 'RequestSectionLanePricingPoint_History'


class RequestProfile(Delete):
    request_profile_id = models.BigAutoField(
        primary_key=True, null=False, db_column="RequestProfileID")
    request_number = models.CharField(
        max_length=32, unique=True, null=False, blank=False, db_column="RequestNumber")
    is_valid_data = models.BooleanField(
        null=False, default=False, db_column="IsValidData")
    using_standard_tarrif = models.BooleanField(
        null=True, default=False, db_column="UsingStandardTariff")
    exclude_from_fak_rating = models.BooleanField(
        null=True, default=False, db_column="ExcludeFromFAKRating")
    use_actual_weight = models.BooleanField(
        null=True, default=False, db_column="UseActualWeight")
    is_class_density = models.BooleanField(
        null=True, default=False, db_column="IsClassDensity")
    avg_weight_density = models.DecimalField(
        max_digits=19, decimal_places=6, null=True, db_column="AvgWeightedDensity")
    override_density = models.DecimalField(
        max_digits=19, decimal_places=6, null=True, db_column="OverrideDensity")
    subject_to_cube = models.DecimalField(
        max_digits=19, decimal_places=6, null=True, db_column="SubjectToCube")
    linear_length_rule = models.DecimalField(
        max_digits=19, decimal_places=6, null=True, db_column="LinearLengthRule")
    weight_per_linear_length_rule = models.DecimalField(
        max_digits=19, decimal_places=6, null=True, db_column="WeightPerLinearLengthRule")
    avg_weighted_class = models.DecimalField(
        max_digits=19, decimal_places=6, null=True, db_column="AvgWeightedClass")
    override_class = models.DecimalField(
        max_digits=19, decimal_places=6, null=True, db_column="OverrideClass")
    freight_elements = models.TextField(
        null=True, blank=False, default="[]", db_column="FreightElements")
    shipments = models.TextField(
        null=True, blank=False, default="[]", db_column="Shipments")
    shipping_controls = models.TextField(
        null=True, blank=False, default="[]", db_column="ShippingControls")
    competitors = models.TextField(
        null=True, blank=False, default="[]", db_column="Competitors")
    class_controls = models.TextField(
        null=True, blank=False, default="[]", db_column="ClassControls")

    def __str__(self):
        return str(self.request_profile_id)

    class Meta:
        db_table = 'RequestProfile'


class RequestProfileHistory(CommentUpdateDelete):
    request_profile_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="RequestProfileVersionID")
    request_profile = models.ForeignKey(
        RequestProfile, on_delete=models.CASCADE, db_column="RequestProfileID")
    request_number = models.CharField(
        max_length=32, null=False, blank=False, db_column="RequestNumber")
    is_valid_data = models.BooleanField(
        null=False, default=False, db_column="IsValidData")
    using_standard_tarrif = models.BooleanField(
        null=True, default=False, db_column="UsingStandardTariff")
    exclude_from_fak_rating = models.BooleanField(
        null=True, default=False, db_column="ExcludeFromFAKRating")
    use_actual_weight = models.BooleanField(
        null=True, default=False, db_column="UseActualWeight")
    is_class_density = models.BooleanField(
        null=True, default=False, db_column="IsClassDensity")
    avg_weight_density = models.DecimalField(
        max_digits=19, decimal_places=6, null=True, db_column="AvgWeightedDensity")
    override_density = models.DecimalField(
        max_digits=19, decimal_places=6, null=True, db_column="OverrideDensity")
    subject_to_cube = models.DecimalField(
        max_digits=19, decimal_places=6, null=True, db_column="SubjectToCube")
    linear_length_rule = models.DecimalField(
        max_digits=19, decimal_places=6, null=True, db_column="LinearLengthRule")
    weight_per_linear_length_rule = models.DecimalField(
        max_digits=19, decimal_places=6, null=True, db_column="WeightPerLinearLengthRule")
    avg_weighted_class = models.DecimalField(
        max_digits=19, decimal_places=6, null=True, db_column="AvgWeightedClass")
    override_class = models.DecimalField(
        max_digits=19, decimal_places=6, null=True, db_column="OverrideClass")
    freight_elements = models.TextField(
        null=True, blank=False, default="[]", db_column="FreightElements")
    shipments = models.TextField(
        null=True, blank=False, default="[]", db_column="Shipments")
    shipping_controls = models.TextField(
        null=True, blank=False, default="[]", db_column="ShippingControls")
    competitors = models.TextField(
        null=True, blank=False, default="[]", db_column="Competitors")
    class_controls = models.TextField(
        null=True, blank=False, default="[]", db_column="ClassControls")

    def __str__(self):
        return str(self.request_profile_version_id)

    class Meta:
        index_together = (('request_profile', 'version_num'))
        db_table = 'RequestProfile_History'


class Request(Delete):
    request_id = models.BigAutoField(
        primary_key=True, null=False, db_column="RequestID")
    request_number = models.CharField(
        max_length=32, unique=True, null=False, blank=False, db_column="RequestNumber")
    request_code = models.CharField(
        max_length=32, unique=True, null=False, blank=False, db_column="RequestCode")
    request_information = models.ForeignKey(
        RequestInformation, on_delete=models.CASCADE, null=True, db_column="RequestInformationID")
    request_profile = models.ForeignKey(
        RequestProfile, on_delete=models.CASCADE, null=True, db_column="RequestProfileID")
    request_lane = models.ForeignKey(
        RequestLane, on_delete=models.CASCADE, null=True, db_column="RequestLaneID")
    request_accessorials = models.ForeignKey(
        RequestAccessorials, on_delete=models.CASCADE, null=True, db_column="RequestAccessorialsID")
    initiated_on = models.DateTimeField(
        auto_now_add=True, null=False, db_column="InitiatedOn")
    initiated_by = models.ForeignKey(
        User, on_delete=models.CASCADE, null=False, db_column="InitiatedBy", related_name="+")
    submitted_on = models.DateTimeField(
        auto_now_add=False, null=True, db_column="SubmittedOn")
    submitted_by = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, db_column="SubmittedBy", related_name="+")
    is_valid_data = models.BooleanField(
        null=False, default=False, db_column="IsValidData")
    is_review = models.BooleanField(
        null=False, default=False, db_column="IsReview")
    request_owner = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, db_column="RequestOwner", related_name="+")
    uni_type = models.TextField(null=True, blank=False, db_column="UniType")
    speedsheet_name = models.TextField(null=True, blank=True, db_column="SpeedsheetName")
    language = models.ForeignKey(
        Language, on_delete=models.CASCADE, null=True, db_column="LanguageID")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        request_status_instance = RequestStatus.objects.filter(
            request=self).first()
        if request_status_instance:
            request_status_instance.save()

        for request_queue_instance in RequestQueue.objects.filter(request=self):
            request_queue_instance.save()

    def __str__(self):
        return str(self.request_id)

    class Meta:
        db_table = 'Request'


class RequestHistory(CommentUpdateDelete):
    request_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="RequestVersionID")
    request = models.ForeignKey(
        Request, on_delete=models.CASCADE, null=False, db_column="RequestID")
    request_number = models.CharField(
        max_length=32, unique=False, null=False, blank=False, db_column="RequestNumber")
    request_code = models.CharField(
        max_length=32, unique=False, null=False, blank=False, db_column="RequestCode")
    request_information_version = models.ForeignKey(
        RequestInformationHistory, on_delete=models.CASCADE, null=True, db_column="RequestInformationVersionID")
    request_profile_version = models.ForeignKey(
        RequestProfileHistory, on_delete=models.CASCADE, null=True, db_column="RequestProfileVersionID")
    request_lane_version = models.ForeignKey(
        RequestLaneHistory, on_delete=models.CASCADE, null=True, db_column="RequestLaneVersionID")
    request_accessorials_version = models.ForeignKey(
        RequestAccessorialsHistory, on_delete=models.CASCADE, null=True, db_column="RequestAccessorialsVersionID")
    initiated_on = models.DateTimeField(
        auto_now_add=False, null=False, db_column="InitiatedOn")
    initiated_by_version = models.ForeignKey(
        UserHistory, on_delete=models.CASCADE, null=False, db_column="InitiatedByVersion", related_name="+")
    submitted_on = models.DateTimeField(
        auto_now_add=False, null=True, db_column="SubmittedOn")
    submitted_by_version = models.ForeignKey(
        UserHistory, on_delete=models.CASCADE, null=True, db_column="SubmittedByVersion", related_name="+")
    is_valid_data = models.BooleanField(
        null=False, default=False, db_column="IsValidData")
    is_review = models.BooleanField(
        null=False, default=False, db_column="IsReview")
    uni_type = models.TextField(null=True, blank=False, db_column="UniType")
    speedsheet_name = models.TextField(null=True, blank=True, db_column="SpeedsheetName")
    language = models.ForeignKey(
        Language, on_delete=models.CASCADE, null=True, db_column="LanguageID")

    def __str__(self):
        return str(self.request_version_id)

    class Meta:
        db_table = 'Request_History'


class ServiceType(Delete):
    service_type_id = models.BigAutoField(
        primary_key=True, null=False, db_column="ServiceTypeID")
    service_class = models.CharField(
        max_length=10, null=False, blank=False, db_column="ServiceClass")
    service_type_name = models.CharField(
        max_length=10, null=False, blank=False, db_column="ServiceTypeName")
    service_type_description = models.TextField(
        max_length=50, null=False, blank=False, db_column="ServiceTypeDescription")

    def __str__(self):
        return str(self.service_type_id)

    class Meta:
        db_table = "ServiceType"


class ServiceTypeHistory(CommentUpdateDelete):
    service_type_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="ServiceTypeVersionID")
    service_type = models.ForeignKey(
        ServiceType, on_delete=models.CASCADE, db_column="ServiceTypeID")
    service_class = models.CharField(
        max_length=10, null=False, blank=False, db_column="ServiceClass")
    service_type_name = models.CharField(
        max_length=10, null=False, blank=False, db_column="ServiceTypeName")
    service_type_description = models.TextField(
        max_length=50, null=False, blank=False, db_column="ServiceTypeDescription")

    def __str__(self):
        return str(self.service_type_version_id)

    class Meta:
        index_together = (('service_type', 'version_num'))
        db_table = "ServiceTypeHistory"

class ServiceMatrix(Delete):
    is_active = models.BooleanField(
        default=1, null=False, db_column="IsActive")
    is_inactive_viewable = models.BooleanField(
        default=1, null=False, db_column="IsInactiveViewable")
    service_matrix_id = models.BigAutoField(
        primary_key=True, null=False, db_column="ServiceMatrixID")
    service_type_id = models.ForeignKey(
        ServiceType, on_delete=models.CASCADE, null=True, db_column="ServiceTypeID")
    sub_service_level_id = models.ForeignKey(
        SubServiceLevel, on_delete=models.CASCADE, null=True, db_column="SubServiceLevelID")
    basing_point_id = models.ForeignKey(
        BasingPoint, on_delete=models.CASCADE, null=True, db_column="BasingPointID")
    zone_id = models.ForeignKey(
        Zone, on_delete=models.CASCADE, null=True, db_column="ZoneID")
    country_id = models.ForeignKey(
        Country, on_delete=models.CASCADE, null=True, db_column="CountryID")
    postal_code_id = models.ForeignKey(
        PostalCode, on_delete=models.CASCADE, null=True, db_column="PostalCodeID")
    province_id = models.ForeignKey(
        Province, on_delete=models.CASCADE, null=True, db_column="ProvinceID")
    region_id = models.ForeignKey(
        Region, on_delete=models.CASCADE, null=True, db_column="RegionID")
    service_point_id = models.ForeignKey(
        ServicePoint, on_delete=models.CASCADE, null=True, db_column="ServicePointID")
    terminal_id = models.ForeignKey(
        Terminal, on_delete=models.CASCADE, null=True, db_column="TerminalID")

    def __str__(self):
        return str(self.service_matrix_id)

    class Meta:
        db_table = "ServiceMatrix"


class ServiceMatrixHistory(CommentUpdateDelete):
    version_num = models.IntegerField(
        default=False, null=False, db_column="VersionNum")
    is_latest_version = models.BooleanField(
        default=False, null=False, db_column="IsLatestVersion")
    updated_on = models.DateTimeField(
        default=False, null=False, db_column="UpdatedOn")
    updated_by = models.TextField(
        default=False, null=False, db_column="UpdatedBy")
    base_version = models.IntegerField(
        default=False, null=False, db_column="BaseVersion")
    comments = models.TextField(
        default=False, null=False, db_column="Comments")
    is_active = models.BooleanField(
        default=1, null=False, db_column="IsActive")
    is_inactive_viewable = models.BooleanField(
        default=1, null=False, db_column="IsInactiveViewable")
    service_matrix_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="ServiceMatrixVersionID")
    service_matrix = models.ForeignKey(
        ServiceMatrix, on_delete=models.CASCADE, null=False, db_column="ServiceMatrixID")
    service_type_version_id = models.ForeignKey(
        ServiceTypeHistory, on_delete=models.CASCADE, null=True, db_column="ServiceTypeVersionID")
    sub_service_level_id = models.ForeignKey(
        SubServiceLevel, on_delete=models.CASCADE, null=True, db_column="SubServiceLevelID")
    basing_point_version_id = models.ForeignKey(
        BasingPointHistory, on_delete=models.CASCADE, null=True, db_column="BasingPointVersionID")
    zone_version_id = models.ForeignKey(
        ZoneHistory, on_delete=models.CASCADE, null=True, db_column="ZoneVersionID")
    country_version_id = models.ForeignKey(
        CountryHistory, on_delete=models.CASCADE, null=True, db_column="CountryVersionID")
    postal_code_version_id = models.ForeignKey(
        PostalCodeHistory, on_delete=models.CASCADE, null=True, db_column="PostalCodeVersionID")
    province_version_id = models.ForeignKey(
        ProvinceHistory, on_delete=models.CASCADE, null=True, db_column="ProvinceVersionID")
    region_version_id = models.ForeignKey(
        RegionHistory, on_delete=models.CASCADE, null=True, db_column="RegionVersionID")
    service_point_version_id = models.ForeignKey(
        ServicePointHistory, on_delete=models.CASCADE, null=True, db_column="ServicePointVersionID")
    terminal_version_id = models.ForeignKey(
        TerminalHistory, on_delete=models.CASCADE, null=True, db_column="TerminalVersionID")

    def __str__(self):
        return str(self.service_matrix_version_id)

    class Meta:
        index_together = (("service_matrix", "version_num"))
        db_table = "ServiceMatrixHistory"

class LastAssignedUser(Delete):
    last_assigned_user_id = models.BigAutoField(
        primary_key=True, null=False, db_column="LastAssignedUserID")
    persona_name = models.CharField(
        max_length=50, null=False, blank=False, db_column="PersonaName")
    service_level = models.ForeignKey(
        ServiceLevel, on_delete=models.CASCADE, null=False, db_column="ServiceLevelID")
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=False, db_column="UserID")

    def __str__(self):
        return str(self.last_assigned_user_id)

    class Meta:
        unique_together = (('persona_name', 'service_level'))
        db_table = 'LastAssignedUser'


class UserServiceLevel(Delete):
    user_service_level_id = models.BigAutoField(
        primary_key=True, null=False, db_column="UserServiceLevelID")
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=False, db_column="UserID")
    service_level = models.ForeignKey(
        ServiceLevel, on_delete=models.CASCADE, null=False, db_column="ServiceLevelID")

    def __str__(self):
        return str(self.user_service_level_id)

    class Meta:
        db_table = 'UserServiceLevel'


class UserServiceLevelHistory(CommentUpdateDelete):
    user_service_level_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="UserServiceLevelVersionID")
    user_service_level = models.ForeignKey(
        UserServiceLevel, on_delete=models.CASCADE, null=False, db_column="UserServiceLevelID")
    user_version = models.ForeignKey(
        UserHistory, on_delete=models.CASCADE, null=False, db_column="UserVersionID")
    service_level_version = models.ForeignKey(
        ServiceLevelHistory, on_delete=models.CASCADE, null=False, db_column="ServiceLevelVersionID")

    def __str__(self):
        return str(self.user_service_level_version_id)

    class Meta:
        index_together = (('user_service_level', 'version_num'))
        db_table = 'UserServiceLevel_History'


class Tariff(Delete):
    tariff_id = models.BigAutoField(
        primary_key=True, null=False, db_column="TariffID")
    request = models.ForeignKey(
        Request, on_delete=models.CASCADE, null=False, db_column="RequestID")
    request_number = models.CharField(
        max_length=32, unique=True, null=False, blank=False, db_column="RequestNumber")
    published_on = models.DateTimeField(
        auto_now_add=True, null=True, db_column="PublishedOn")
    expires_on = models.DateTimeField(
        auto_now_add=True, null=True, db_column="ExpiresOn")
    document_url = models.TextField(
        null=True, blank=False, db_column="DocumentUrl")
    is_valid_data = models.BooleanField(
        null=False, default=False, db_column="IsValidData")

    def __str__(self):
        return str(self.tariff_id)

    class Meta:
        db_table = 'Tariff'


class TariffHistory(CommentUpdateDelete):
    tariff_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="TariffVersionID")
    tariff = models.ForeignKey(
        Tariff, on_delete=models.CASCADE, null=False, db_column="TariffID")
    request_version = models.ForeignKey(
        RequestHistory, on_delete=models.CASCADE, null=False, db_column="RequestVersionID")
    request_number = models.CharField(
        max_length=32, unique=True, null=False, blank=False, db_column="RequestNumber")
    published_on = models.DateTimeField(
        auto_now_add=False, null=True, db_column="PublishedOn")
    expires_on = models.DateTimeField(
        auto_now_add=False, null=True, db_column="ExpiresOn")
    document_url = models.TextField(
        null=True, blank=False, db_column="DocumentUrl")
    is_valid_data = models.BooleanField(
        null=False, default=False, db_column="IsValidData")

    def __str__(self):
        return str(self.tariff_version_id)

    class Meta:
        index_together = (('tariff', 'version_num'))
        db_table = 'Tariff_History'


class RequestStatus(Delete):
    request_status_id = models.BigAutoField(
        primary_key=True, null=False, db_column="RequestStatusID")
    request = models.ForeignKey(
        Request, on_delete=models.CASCADE, null=False, db_column="RequestID")
    request_status_type = models.ForeignKey(
        RequestStatusType, on_delete=models.CASCADE, null=False, db_column="RequestStatusTypeID")
    sales_representative = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, db_column="SalesRepresentativeID", related_name="+")
    pricing_analyst = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, db_column="PricingAnalystID", related_name="+")
    credit_analyst = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, db_column="CreditAnalystID", related_name="+")
    current_editor = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, db_column="CurrentEditorID", related_name="+")

    def __str__(self):
        return str(self.request_status_id)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._old_request_status_type_name = self.request_status_type.request_status_type_name

    def save(self, *args, **kwargs):
        # TODO Bug!!! This method is being invoked when we change fields in Reauest, and suppose to update the status,
        # but it is not updating status.
        super().save(*args, **kwargs)

        request_status_type_triggers = {
            "RRF Submitted": self._rrf_submitted_trigger,
            # "RRF Archived": self._rrf_cancelled_trigger,
            # "RRF Re-activated": self._rrf_reactivated_trigger,
            "RRF Cancelled": self._rrf_cancelled_trigger,
            "Cost+ Declined": self._cost_plus_declined_trigger,
            # "Speedsheet Archived": self._rrf_cancelled_trigger,
            # "Speedsheet Re-activated": self._rrf_cancelled_trigger,
            # "Speedsheet Cancelled": self._rrf_cancelled_trigger,

        }
        request_status_type_name = self.request_status_type.request_status_type_name
        if request_status_type_name in request_status_type_triggers and self._old_request_status_type_name != request_status_type_name:
            request_status_type_triggers[request_status_type_name]()

        if self.request.request_information.is_extended_payment and request_status_type_name not in [
                "RRF Initiated", "RRF Archived", "RRF Cancelled"] and not RequestQueue.objects.filter(
                Q(request_status_type__request_status_type_name="Pending EPT Approval", completed_on__isnull=True) |
                Q(request_status_type__request_status_type_name="EPT Approved", completed_on__isnull=False),
                request=self.request).exists():
            from pac.rrf.workflow import WorkflowManager
            workflow_manager = WorkflowManager(request=self.request,
                                               request_status=RequestStatus.objects.filter(
                                                   request=self.request).first(),
                                               next_request_status_type=RequestStatusType.objects.filter(
                                                   request_status_type_name="Pending EPT Approval").first())
            workflow_manager.generate_request_queue()

    def _rrf_submitted_trigger(self):
        self.request.submitted_on = timezone.now()
        self.request.submitted_by = self.sales_representative
        self.request.save()

    def _rrf_archived_trigger(self):
        self.request.is_active = False
        self.request.save()

    def _rrf_reactivated_trigger(self):
        self.request.is_active = True
        self.request.save()

    def _rrf_cancelled_trigger(self):
        latest_rrf_cancelled_request_queue = RequestQueue.objects.filter(
            request=self.request, request_status_type__request_status_type_name="RRF Cancelled").latest('assigned_on')
        request_queues = RequestQueue.objects.filter(
            request=self.request, is_inactive_viewable=True).exclude(
            request_queue_id=latest_rrf_cancelled_request_queue.pk)
        for request_queue in request_queues:
            request_queue.is_inactive_viewable = False
            request_queue.is_active = False
            request_queue.save()

        self.request.is_inactive_viewable = False
        self.request.is_active = False
        self.request.save()

    def _cost_plus_declined_trigger(self):
        secondary_request_queues = RequestQueue.objects.filter(
            is_secondary=True, request=self.request, is_active=True)
        for secondary_request_queue in secondary_request_queues:
            secondary_request_queue.is_active = False
            secondary_request_queue.is_inactive_viewable = False
            secondary_request_queue.save()

    class Meta:
        db_table = 'RequestStatus'


class RequestStatusHistory(CommentUpdateDelete):
    request_status_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="RequestStatusVersionID")
    request_status = models.ForeignKey(
        RequestStatus, on_delete=models.CASCADE, null=False, db_column="RequestStatusID")
    request_version = models.ForeignKey(
        RequestHistory, on_delete=models.CASCADE, null=False, db_column="RequestVersionID")
    request_status_type_version = models.ForeignKey(
        RequestStatusTypeHistory, on_delete=models.CASCADE, null=False, db_column="RequestStatusTypeVersionID")
    sales_representative_version = models.ForeignKey(
        UserHistory, on_delete=models.CASCADE, null=True, db_column="SalesRepresentativeVersionID", related_name="+")
    pricing_analyst_version = models.ForeignKey(
        UserHistory, on_delete=models.CASCADE, null=True, db_column="PricingAnalystVersionID", related_name="+")
    credit_analyst_version = models.ForeignKey(
        UserHistory, on_delete=models.CASCADE, null=True, db_column="CreditAnalystVersionID", related_name="+")
    current_editor_version = models.ForeignKey(
        UserHistory, on_delete=models.CASCADE, null=True, db_column="CurrentEditorVersionID", related_name="+")

    def __str__(self):
        return str(self.request_status_version_id)

    class Meta:
        index_together = (('request_status', 'version_num'))
        db_table = 'RequestStatus_History'


# Access Control - Request Parties
class RequestQueue(Delete):
    request_queue_id = models.BigAutoField(
        primary_key=True, null=False, db_column="RequestQueueID")
    request = models.ForeignKey(
        Request, on_delete=models.CASCADE, db_column="RequestID")
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, db_column="UserID")
    request_status_type = models.ForeignKey(
        RequestStatusType, on_delete=models.CASCADE, db_column="RequestStatusTypeID")
    user_persona = models.CharField(
        max_length=50, null=False, blank=False, db_column="UserPersona")
    assigned_on = models.DateTimeField(
        auto_now_add=False, null=False, db_column="AssignedOn")
    due_date = models.DateTimeField(
        auto_now_add=False, null=True, db_column="DueDate")
    completed_on = models.DateTimeField(
        auto_now_add=False, null=True, db_column="CompletedOn")
    is_secondary = models.BooleanField(
        default=False, null=False, blank=False, db_column="IsSecondary")
    is_final = models.BooleanField(
        default=False, null=False, blank=False, db_column="IsFinal")
    is_actionable = models.BooleanField(
        default=False, null=False, blank=False, db_column="IsActionable")
    attachment = models.TextField(
        null=True, default=None, db_column="Attachment")

    def save(self, *args, **kwargs):
        if not self.pk:
            self.send_notifications()
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.request_queue_id)

    def _rrf_with_sales_notification(self):
        if self.user_persona == "Sales Representative":
            Notification.objects.create(
                user=self.user,
                message=f"{self.user.user_name} has editor rights for Request No. {self.request.request_code} for {self.request.request_information.customer.account}] - {self.request.request_information.customer.service_level.service_level_name}")

    def _pending_credit_approval_notification(self):
        if self.user_persona == "Credit Analyst":
            Notification.objects.create(
                user=self.user,
                # message=f"Request No. {self.request.request_code} requires approval for New Customer {self.request.request_information.customer.account}]")
                message=f"Request No. {self.request.request_code} requires approval for New Customer ]")

    def _credit_approved_notification(self):
        if self.user_persona == "Sales Representative":
            Notification.objects.create(
                user=self.user,
                message=f"Request No. {self.request.request_code} for New Customer {self.request.request_information.customer.account}] has been approved")

    def _credit_declined_notification(self):
        if self.user_persona == "Sales Representative":
            Notification.objects.create(
                user=self.user,
                message=f"Request No. {self.request.request_code} for New Customer {self.request.request_information.customer.account}] has been declined")

    def _pending_cost_plus_approval_notification(self):
        if self.user_persona == "Sales Manager":
            Notification.objects.create(
                user=self.user,
                message=f"Request No. {self.request.request_code} for {self.request.request_information.customer.account}] - {self.request.request_information.customer.service_level.service_level_name} requires Cost+ approval")

    def _cost_plus_approved_notification(self):
        if self.user_persona == "Sales Representative":
            Notification.objects.create(
                user=self.user,
                message=f"Cost+ for Request No. {self.request.request_code} for {self.request.request_information.customer.account}] - {self.request.request_information.customer.service_level.service_level_name} has been approved")

    def _cost_plus_declined_notification(self):
        if self.user_persona == "Sales Representative":
            Notification.objects.create(
                user=self.user,
                message=f"Cost+ for Request No. {self.request.request_code} for {self.request.request_information.customer.account}] - {self.request.request_information.customer.service_level.service_level_name} has been declined")

    def _rrf_with_pricing_notification(self):
        if self.user_persona == "Pricing Analyst":
            Notification.objects.create(
                user=self.user,
                message=f"Request No. {self.request.request_code} for {self.request.request_information.customer.account}] - {self.request.request_information.customer.service_level.service_level_name} has been assigned to {self.user.user_name}-{self.user.user_name} has editor rights of Request No. {self.request.request_code} for {self.request.request_information.customer.account}] - {self.request.request_information.customer.service_level.service_level_name}")

    def _pending_sales_approval_notification(self):
        if self.user_persona == "Sales Representative":
            Notification.objects.create(
                user=self.user,
                message=f"Request No. {self.request.request_code} for {self.request.request_information.customer.account}] - {self.request.request_information.customer.service_level.service_level_name} requires approval for publishing from {self.user.user_name}")

    def _sales_declined_notification(self):
        if self.user_persona == "Pricing Analyst":
            sales_representative = RequestStatus.objects.filter(
                request=self.request).first().sales_representative
            Notification.objects.create(
                user=self.user,
                message=f"Request No. {self.request.request_code} for {self.request.request_information.customer.account}] - {self.request.request_information.customer.service_level.service_level_name} has been declined for publishing by {sales_representative.user_name}")

    def _pending_partner_approval_notification(self):
        if self.user_persona == "Partner Carrier":
            Notification.objects.create(
                user=self.user,
                message=f"Request No. {self.request.request_code} for {self.request.request_information.customer.account}] - {self.request.request_information.customer.service_level.service_level_name} requires approval for publishing from {self.user.user_name}")

    def _partner_approved_notification(self):
        if self.user_persona == "Pricing Analyst":
            Notification.objects.create(
                user=self.user,
                message=f"Request No. {self.request.request_code} for {self.request.request_information.customer.account}] - {self.request.request_information.customer.service_level.service_level_name} has been approved for publishing by [Insert Partner Carrier]")

    def _partner_declined_notification(self):
        if self.user_persona == "Pricing Analyst":
            Notification.objects.create(
                user=self.user,
                message=f"Request No. {self.request.request_code} for {self.request.request_information.customer.account}] - {self.request.request_information.customer.service_level.service_level_name} has been declined for publishing by [Insert Partner Carrier]")

    def _sales_approved_notification(self):
        if self.user_persona == "Pricing Analyst":
            sales_representative = RequestStatus.objects.filter(
                request=self.request).first().sales_representative
            Notification.objects.create(
                user=self.user,
                message=f"Request No. {self.request.request_code} for {self.request.request_information.customer.account}] - {self.request.request_information.customer.service_level.service_level_name} has been approved for publishing by {sales_representative.user_name}")

    def _submitted_to_publish_notification(self):
        if self.user_persona == "Sales Representative":
            pricing_analyst = RequestStatus.objects.filter(
                request=self.request).first().pricing_analyst
            Notification.objects.create(
                user=self.user,
                message=f"Request No. {self.request.request_code} for {self.request.request_information.customer.account}] - {self.request.request_information.customer.service_level.service_level_name} has been sent for publishing by {pricing_analyst.user_name}")

    def _published_succesfully_notification(self):
        if self.user_persona in ["Pricing Analyst", "Sales Representative"]:
            Notification.objects.create(
                user=self.user,
                message=f"Request No. {self.request.request_code} for {self.request.request_information.customer.account}] - {self.request.request_information.customer.service_level.service_level_name} has been successfully published in TMS")

    def _publishing_failed_notification(self):
        if self.user_persona in ["Pricing Analyst", "Sales Representative"]:
            Notification.objects.create(
                user=self.user,
                message=f"Request No. {self.request.request_code} for {self.request.request_information.customer.account}] - {self.request.request_information.customer.service_level.service_level_name} has failed to publish in TMS")

    def _secondary_pending_drm_approval_notification(self):
        if self.user_persona in ["Sales Manager", "Pricing Analyst"]:
            Notification.objects.create(
                user=self.user,
                message=f"Deal Review Meeting has been requested for Request No. {self.request.request_code} for {self.request.request_information.customer.account}] - {self.request.request_information.customer.service_level.service_level_name}")

    def _secondary_drm_approved_notification(self):
        if self.user_persona in ["Pricing Manager", "Pricing Analyst", "Sales Representative"]:
            Notification.objects.create(
                user=self.user,
                message=f"Deal Review Meeting has been approved for Request No. {self.request.request_code} for {self.request.request_information.customer.account}] - {self.request.request_information.customer.service_level.service_level_name}")

    def _secondary_drm_declined_notification(self):
        if self.user_persona in ["Pricing Analyst", "Sales Representative"]:
            Notification.objects.create(
                user=self.user,
                message=f"Deal Review Meeting has been declined for Request No. {self.request.request_code} for {self.request.request_information.customer.account}] - {self.request.request_information.customer.service_level.service_level_name}")

    def _secondary_pending_pcr_approval_notification(self):
        if self.user_persona in ["Sales Manager", "Pricing Analyst"]:
            Notification.objects.create(
                user=self.user,
                message=f"Pricing Committee has been requested for Request No. {self.request.request_code} for {self.request.request_information.customer.account}] - {self.request.request_information.customer.service_level.service_level_name}")

    def _secondary_pcr_approved_notification(self):
        if self.user_persona in ["Pricing Manager", "Pricing Analyst", "Sales Representative"]:
            Notification.objects.create(
                user=self.user,
                message=f"Pricing Committee has been approved for Request No. {self.request.request_code} for {self.request.request_information.customer.account}] - {self.request.request_information.customer.service_level.service_level_name}")

    def _secondary_pcr_declined_notification(self):
        if self.user_persona in ["Pricing Analyst", "Sales Representative"]:
            Notification.objects.create(
                user=self.user,
                message=f"Pricing Committee has been declined for Request No. {self.request.request_code} for {self.request.request_information.customer.account}] - {self.request.request_information.customer.service_level.service_level_name}")

    def _secondary_pending_pc_approval_notification(self):
        if self.user_persona in ["Sales Manager"]:
            Notification.objects.create(
                user=self.user,
                message=f"Priority Change has been requested for Request No. {self.request.request_code} for {self.request.request_information.customer.account}] - {self.request.request_information.customer.service_level.service_level_name}")

    def _secondary_pc_approved_notification(self):
        if self.user_persona in ["Pricing Analyst", "Sales Representative"]:
            Notification.objects.create(
                user=self.user,
                message=f"Priority Change has been approved for Request No. {self.request.request_code} for {self.request.request_information.customer.account}] - {self.request.request_information.customer.service_level.service_level_name}")

    def _secondary_pc_declined_notification(self):
        if self.user_persona in ["Sales Representative"]:
            Notification.objects.create(
                user=self.user,
                message=f"Priority Change has been declined for Request No. {self.request.request_code} for {self.request.request_information.customer.account}] - {self.request.request_information.customer.service_level.service_level_name}")

    def _secondary_pending_ept_approval_notification(self):
        if self.user_persona in ["Credit Manager"]:
            Notification.objects.create(
                user=self.user,
                message=f"Extended Payment Terms has been requested for Request No. {self.request.request_code} for {self.request.request_information.customer.account}] - {self.request.request_information.customer.service_level.service_level_name}")

    def _secondary_ept_approved_notification(self):
        if self.user_persona in ["Pricing Analyst", "Sales Representative"]:
            Notification.objects.create(
                user=self.user,
                message=f"Extended Payment Terms has been approved for Request No. {self.request.request_code} for {self.request.request_information.customer.account}] - {self.request.request_information.customer.service_level.service_level_name}")

    def _secondary_ept_declined_notification(self):
        if self.user_persona in ["Pricing Analyst", "Sales Representative"]:
            Notification.objects.create(
                user=self.user,
                message=f"Extended Payment Terms has been declined for Request No. {self.request.request_code} for {self.request.request_information.customer.account}] - {self.request.request_information.customer.service_level.service_level_name}")

    def send_notifications(self):
        mapping = {
            "RRF with Sales": self._rrf_with_sales_notification,
            "Pending Credit Approval": self._pending_credit_approval_notification,
            "Credit Approved": self._credit_approved_notification,
            "Credit Declined": self._credit_declined_notification,
            "Pending Cost+ Approval": self._pending_cost_plus_approval_notification,
            "Cost+ Approved": self._cost_plus_approved_notification,
            "Cost+ Declined": self._cost_plus_declined_notification,
            "RRF with Pricing": self._rrf_with_pricing_notification,
            "Pending Sales Approval": self._pending_sales_approval_notification,
            "Sales Declined": self._sales_declined_notification,
            "Pending Partner Approval": self._pending_partner_approval_notification,
            "Partner Approved": self._partner_approved_notification,
            "Partner Declined": self._partner_declined_notification,
            "Sales Approved": self._sales_approved_notification,
            "Submitted to Publish": self._submitted_to_publish_notification,
            "Published Successfully": self._published_succesfully_notification,
            "Publishing Failed": self._publishing_failed_notification,
            "Pending DRM Approval": self._secondary_pending_drm_approval_notification,
            "DRM Approved": self._secondary_drm_approved_notification,
            "DRM Declined": self._secondary_drm_declined_notification,
            "Pending PCR Approval": self._secondary_pending_pcr_approval_notification,
            "PCR Approved": self._secondary_pcr_approved_notification,
            "PCR Declined": self._secondary_pcr_declined_notification,
            "Pending PC Approval": self._secondary_pending_pc_approval_notification,
            "PC Approved": self._secondary_pc_approved_notification,
            "PC Declined": self._secondary_pc_declined_notification,
            "Pending EPT Approval": self._secondary_pending_ept_approval_notification,
            "EPT Approved": self._secondary_ept_approved_notification,
            "EPT Declined": self._secondary_ept_declined_notification
        }

        if self.request_status_type.request_status_type_name in mapping:
            mapping[self.request_status_type.request_status_type_name]()

    class Meta:
        db_table = 'RequestQueue'


class RequestQueueHistory(CommentUpdateDelete):
    request_queue_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="RequestQueueVersionID")
    request_queue = models.ForeignKey(
        RequestQueue, on_delete=models.CASCADE, db_column="RequestQueueID")
    request_version = models.ForeignKey(
        RequestHistory, on_delete=models.CASCADE, db_column="RequestVersionID")
    user_version = models.ForeignKey(
        UserHistory, on_delete=models.CASCADE, db_column="UserVersionID")
    request_status_type_version = models.ForeignKey(
        RequestStatusTypeHistory, on_delete=models.CASCADE, db_column="RequestStatusTypeVersionID")
    user_persona = models.CharField(
        max_length=50, null=False, blank=False, db_column="UserPersona")
    assigned_on = models.DateTimeField(
        auto_now_add=False, null=False, db_column="AssignedOn")
    due_date = models.DateTimeField(
        auto_now_add=False, null=True, db_column="DueDate")
    completed_on = models.DateTimeField(
        auto_now_add=False, null=True, db_column="CompletedOn")
    is_secondary = models.BooleanField(
        default=False, null=False, blank=False, db_column="IsSecondary")
    is_final = models.BooleanField(
        default=False, null=False, blank=False, db_column="IsFinal")
    is_actionable = models.BooleanField(
        default=False, null=False, blank=False, db_column="IsActionable")
    attachment = models.TextField(
        null=True, default=None, db_column="Attachment")

    def __str__(self):
        return str(self.request_queue_version_id)

    class Meta:
        index_together = (('request_queue', 'version_num'))
        db_table = 'RequestQueue_History'


class RequestEditorRight(Delete):
    request_editor_right_id = models.BigAutoField(
        primary_key=True, null=False, db_column="RequestEditorRightID")
    request = models.ForeignKey(
        Request, on_delete=models.CASCADE, db_column="RequestID")
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, db_column="UserID")
    notification = models.ForeignKey(
        Notification, on_delete=models.CASCADE, db_column="NotificationID")

    def __str__(self):
        return str(self.request_editor_right_id)

    class Meta:
        db_table = 'RequestEditorRight'


class ImportFile(models.Model):
    id = models.UUIDField(
        auto_created=True,
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        serialize=False, verbose_name='Id')
    file_name = models.TextField(
        null=False, blank=False, db_column="FileName")
    request_section_id = models.TextField(
        null=True, blank=False, db_column="RequestSectionID")
    record_count = models.IntegerField(
        null=False, blank=False, db_column="RecordCount")
    uni_status = models.TextField(
        default="UNPROCESSED", null=False, blank=False, db_column="UniStatus")
    uni_type = models.TextField(default='UNDEFINED', null=False, blank=False, db_column="UniType")
    created_on = models.DateTimeField(
        auto_now_add=True, null=False, db_column="CreatedOn")
    updated_on = models.DateTimeField(
        auto_now_add=True, null=False, db_column="UpdatedOn")
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, null=False, db_column="CreatedBy", related_name="+")
    rate_type = models.TextField(default='UNDEFINED', null=False, blank=False, db_column="RateType")
    duplicate_lane_count = models.IntegerField(
        null=False, blank=False, default=0, db_column="DuplicateLaneCount")
    directional_lane_count = models.IntegerField(
        null=False, blank=False, default=0, db_column="DirectionalLaneCount")
    between_lane_count = models.IntegerField(
        null=False, blank=False, default=0, db_column="BetweenLaneCount")

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'ImportFile'


class RequestSectionLaneImportQueue(models.Model):
    id = models.UUIDField(
        auto_created=True,
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        serialize=False, verbose_name='Id')
    request_section_id = models.TextField(
        null=True, blank=False, db_column="RequestSectionID")
    section_name = models.TextField(
        null=True, blank=False, db_column="SectionName")
    request_section_lane_id = models.TextField(
        null=True, blank=False, db_column="RequestSectionLaneID")

    orig_group_type_id = models.TextField(
        RequestSectionLanePointType, null=True, db_column="OriginGroupTypeId")
    origin_group_type_name = models.TextField(
        null=True, blank=False, db_column="OriginGroupTypeName")

    origin_group_id = models.TextField(
        null=True, blank=False, db_column="OriginGroupId")
    origin_group_code = models.TextField(
        null=True, blank=False, db_column="OriginGroupCode")

    origin_point_type_id = models.TextField(
        null=True, blank=False, db_column="OriginPointTypeId")
    origin_point_type_name = models.TextField(
        null=True, blank=False, db_column="OriginPointTypeName")

    origin_point_id = models.TextField(
        null=True, blank=False, db_column="OriginPointId")
    origin_point_code = models.TextField(
        null=True, blank=False, db_column="OriginPointCode")

    destination_group_type_id = models.TextField(
        null=True, blank=False, db_column="DestinationGroupTypeId")
    destination_group_type_name = models.TextField(
        null=True, blank=False, db_column="DestinationGroupTypeName")

    destination_group_id = models.TextField(
        null=True, blank=False, db_column="DestinationGroupId")
    destination_group_code = models.TextField(
        null=True, blank=False, db_column="DestinationGroupCode")

    destination_point_type_id = models.TextField(
        null=True, blank=False, db_column="DestinationPointTypeId")
    destination_point_type_name = models.TextField(
        null=True, blank=False, db_column="DestinationPointTypeName")

    destination_point_id = models.TextField(
        null=True, blank=False, db_column="DestinationPointId")
    destination_point_code = models.TextField(
        null=True, blank=False, db_column="DestinationPointCode")

    is_between = models.TextField(
        null=True, blank=False, db_column="IsBetween")

    weight_break = models.TextField(
        blank=False, default="[]", db_column="WeightBreak")
    status_message = models.TextField(
        null=True, blank=False, db_column="StatusMessage")
    uni_status = models.TextField(
        default="UNPROCESSED", null=False, blank=False, db_column="UniStatus")
    uni_type = models.TextField(
        default="UNPROCESSED", null=False, blank=False, db_column="UniType")
    created_on = models.DateTimeField(
        auto_now_add=True, null=False, db_column="CreatedOn")
    updated_on = models.DateTimeField(
        auto_now_add=True, null=False, db_column="UpdatedOn")
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, null=False, db_column="CreatedBy", related_name="+")
    file = models.ForeignKey(ImportFile, related_name='ImportFile', on_delete=models.CASCADE, db_column="File")

    initial_rec_order = models.IntegerField(
        null=True, blank=False, db_column="InitialRecOrder")

    # + request_section_id = data.get("request_section_id")
    # + orig_group_type_id = data.get("orig_group_type_id")
    # + orig_group_id = data.get("orig_group_id")
    # orig_point_type_id = data.get("orig_point_type_id")
    # orig_point_id = data.get("orig_point_id")
    # dest_group_type_id = data.get("dest_group_type_id")
    # dest_group_id = data.get("dest_group_id")
    # dest_point_type_id = data.get("dest_point_type_id")
    # dest_point_id = data.get("dest_point_id")
    # is_between = data.get("is_between")

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'RequestSectionLaneImportQueue'


class RequestSectionLanePricingPointImportQueue(models.Model):
    id = models.UUIDField(
        auto_created=True,
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        serialize=False, verbose_name='Id')
    request_section_id = models.TextField(
        null=True, blank=False, db_column="RequestSectionID")
    section_name = models.TextField(
        null=True, blank=False, db_column="SectionName")
    request_section_lane_id = models.TextField(
        null=True, blank=False, db_column="RequestSectionLaneID")
    origin_point_code = models.TextField(
        null=True, blank=False, db_column="OriginPointCode")
    destination_point_code = models.TextField(
        null=True, blank=False, db_column="DestinationPointCode")
    request_section_lane_pricing_point_id = models.TextField(
        null=True, blank=False, db_column="RequestSectionLanePricingPointID")
    origin_post_code_id = models.TextField(
        null=True, blank=False, db_column="OriginPostCodeID")
    origin_postal_code_name = models.TextField(
        null=True, blank=False, db_column="OriginPostalCodeName")
    destination_post_code_id = models.TextField(
        null=True, blank=False, db_column="DestinationPostCodeID")
    destination_postal_code_name = models.TextField(
        null=True, blank=False, db_column="DestinationPostalCodeName")
    weight_break = models.TextField(
        blank=False, default="[]", db_column="WeightBreak")
    status_message = models.TextField(
        null=True, blank=False, db_column="StatusMessage")
    uni_status = models.TextField(
        default="UNPROCESSED", null=False, blank=False, db_column="UniStatus")
    uni_type = models.TextField(
        default="UNDEFINED", null=False, blank=False, db_column="UniType")
    created_on = models.DateTimeField(
        auto_now_add=True, null=False, db_column="CreatedOn")
    updated_on = models.DateTimeField(
        auto_now_add=True, null=False, db_column="UpdatedOn")
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, null=False, db_column="CreatedBy", related_name="+")
    file = models.ForeignKey(ImportFile, related_name='PricingPointsImportFile', on_delete=models.CASCADE,
                             db_column="File")
    origin_postal_code_id = models.IntegerField(
        null=True, blank=False, db_column="OriginPostalCodeId")
    destination_postal_code_id = models.IntegerField(
        null=True, blank=False, db_column="DestinationPostalCodeId")
    initial_rec_order = models.IntegerField(
        null=True, blank=False, db_column="InitialRecOrder")

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'RequestSectionLanePricingPointImportQueue'


class RequestEditorRightHistory(CommentUpdateDelete):
    request_editor_right_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="RequestEditorRightVersionID")
    request_editor_right = models.ForeignKey(
        RequestEditorRight, on_delete=models.CASCADE, db_column="RequestEditorRightID")
    request_version = models.ForeignKey(
        RequestHistory, on_delete=models.CASCADE, db_column="RequestVersionID")
    user_version = models.ForeignKey(
        UserHistory, on_delete=models.CASCADE, db_column="UserVersionID")
    notification_version = models.ForeignKey(
        NotificationHistory, on_delete=models.CASCADE, db_column="NotificationVersionID")

    def __str__(self):
        return str(self.request_editor_right_version_id)

    class Meta:
        db_table = 'RequestEditorRight_History'

@receiver(models.signals.post_save, sender=AccountTree)
@receiver(models.signals.post_save, sender=Currency)
@receiver(models.signals.post_save, sender=Customer)
@receiver(models.signals.post_save, sender=Language)
@receiver(models.signals.post_save, sender=RequestType)
@receiver(models.signals.post_save, sender=RequestAccessorials)
@receiver(models.signals.post_save, sender=RequestInformation)
@receiver(models.signals.post_save, sender=RequestLane)
@receiver(models.signals.post_save, sender=RequestProfile)
@receiver(models.signals.post_save, sender=Request)
@receiver(models.signals.post_save, sender=Tariff)
@receiver(models.signals.post_save, sender=RequestStatus)
@receiver(models.signals.post_save, sender=RequestStatusType)
@receiver(models.signals.post_save, sender=Zone)
@receiver(models.signals.post_save, sender=RequestSection)
@receiver(models.signals.post_save, sender=RateBase)
@receiver(models.signals.post_save, sender=EquipmentType)
@receiver(models.signals.post_save, sender=FreightClass)
@receiver(models.signals.post_save, sender=RequestSectionLane)
@receiver(models.signals.post_save, sender=RequestSectionLanePricingPoint)
@receiver(models.signals.post_save, sender=RequestSectionLanePointType)
@receiver(models.signals.post_save, sender=RequestQueue)
@receiver(models.signals.post_save, sender=RequestEditorRight)
def post_save_instance(sender, instance, created, **kwargs):
    from pac.helpers.functions import create_instance_history
    create_instance_history(sender, instance, globals())
