import uuid

from django import forms
from django.db import models
from django.dispatch import receiver

from core.models import User, UserHistory
from pac.helpers.base import CommentUpdateDelete, Delete


class Country(Delete):
    country_id = models.BigAutoField(
        primary_key=True, null=False, db_column="CountryID")
    country_name = models.CharField(
        max_length=50, unique=True, null=False, blank=False, db_column="CountryName")
    country_code = models.CharField(
        max_length=2, unique=True, null=False, blank=False, db_column="CountryCode")
    description = models.TextField(
        max_length=50, null=True, blank=False, db_column="Description")

    def __str__(self):
        return str(self.country_id)

    class Meta:
        db_table = 'Country'


class CountryHistory(CommentUpdateDelete):
    country_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="CountryVersionID")
    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, db_column="CountryID")
    country_name = models.CharField(
        max_length=50, null=False, blank=False, db_column="CountryName")
    country_code = models.CharField(
        max_length=2, null=False, blank=False, db_column="CountryCode")
    description = models.TextField(
        max_length=50, null=True, blank=False, db_column="Description")

    def __str__(self):
        return str(self.country_version_id)

    class Meta:
        index_together = (('country', 'version_num'))
        db_table = 'Country_History'


def create_country_history(instance):
    history_instance = CountryHistory()
    previous_history_instance = CountryHistory.objects.filter(
        country=instance, is_latest_version=True).first()

    history_instance.country = instance

    for field in ["country_name", "country_code", "is_active"]:
        setattr(history_instance, field, getattr(instance, field))

    if previous_history_instance:
        history_instance.version_num = previous_history_instance.version_num + 1
        previous_history_instance.is_latest_version = False
        previous_history_instance.save()

    history_instance.save()


class Region(Delete):
    region_id = models.BigAutoField(
        primary_key=True, null=False, db_column="RegionID")
    region_name = models.CharField(
        max_length=50, unique=True, blank=False, null=False, db_column="RegionName")
    region_code = models.CharField(
        max_length=4, unique=True, blank=False, null=False, db_column="RegionCode")
    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, db_column="CountryID")
    description = models.TextField(
        max_length=50, null=True, blank=False, db_column="Description")

    def __str__(self):
        return str(self.region_id)

    class Meta:
        db_table = 'Region'


class RegionHistory(CommentUpdateDelete):
    region_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="RegionVersionID")
    region = models.ForeignKey(
        Region, on_delete=models.CASCADE, db_column="RegionID")
    region_name = models.CharField(
        max_length=50, blank=False, null=False, db_column="RegionName")
    region_code = models.CharField(
        max_length=4, blank=False, null=False, db_column="RegionCode")
    country_version = models.ForeignKey(
        CountryHistory, on_delete=models.CASCADE, db_column="CountryVersionID")
    description = models.TextField(
        max_length=50, null=True, blank=False, db_column="Description")

    def __str__(self):
        return str(self.region_version_id)

    class Meta:
        index_together = (("region", "version_num"))
        db_table = 'Region_History'


class Province(Delete):
    province_id = models.BigAutoField(
        primary_key=True, null=False, db_column="ProvinceID")
    province_name = models.CharField(
        max_length=50, unique=True, null=False, blank=False, db_column="ProvinceName")
    province_code = models.CharField(
        max_length=2, unique=True, null=False, blank=False, db_column="ProvinceCode")
    region = models.ForeignKey(
        Region, on_delete=models.CASCADE, db_column="RegionID")
    description = models.TextField(
        max_length=50, null=True, blank=False, db_column="Description")

    def __str__(self):
        return str(self.province_id)

    class Meta:
        db_table = 'Province'


class ProvinceHistory(CommentUpdateDelete):
    province_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="ProvinceVersionID")
    province = models.ForeignKey(
        Province, on_delete=models.CASCADE, db_column="ProvinceID")
    province_name = models.CharField(
        max_length=50, null=False, blank=False, db_column="ProvinceName")
    province_code = models.CharField(
        max_length=2, null=False, blank=False, db_column="ProvinceCode")
    region_version = models.ForeignKey(
        RegionHistory, on_delete=models.CASCADE, db_column="RegionVersionID")
    description = models.TextField(
        max_length=50, null=True, blank=False, db_column="Description")

    def __str__(self):
        return str(self.province_version_id)

    class Meta:
        index_together = (('province', 'version_num'))
        db_table = 'Province_History'


def create_province_history(instance):
    history_instance = ProvinceHistory()
    previous_history_instance = ProvinceHistory.objects.filter(
        province=instance, is_latest_version=True).first()

    history_instance.province = instance

    for field in ["province_name", "province_code", "is_active"]:
        setattr(history_instance, field, getattr(instance, field))

    region_history_instance = RegionHistory.objects.filter(
        region=instance.region, is_latest_version=True).first()
    if region_history_instance:
        history_instance.region_version = region_history_instance

    if previous_history_instance:
        history_instance.version_num = previous_history_instance.version_num + 1
        previous_history_instance.is_latest_version = False
        previous_history_instance.save()

    history_instance.save()


class City(Delete):
    city_id = models.BigAutoField(
        primary_key=True, null=False, db_column="CityID")
    city_name = models.CharField(
        max_length=50, null=False, db_column="CityName")
    province = models.ForeignKey(
        Province, on_delete=models.CASCADE, db_column="ProvinceID")
    city_code = models.CharField(
        max_length=10, unique=True, null=True, blank=False, default="Test", db_column="CityCode")
    description = models.TextField(
        max_length=50, null=True, blank=False, db_column="Description")

    def __str__(self):
        return str(self.city_id)

    class Meta:
        index_together = (('city_name', 'province'))
        db_table = 'City'


class CityHistory(CommentUpdateDelete):
    city_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="CityVersionID")
    city = models.ForeignKey(
        City, on_delete=models.CASCADE, db_column="CityID")
    city_name = models.CharField(
        max_length=50, null=False, blank=False, db_column="CityName")
    province_version = models.ForeignKey(
        ProvinceHistory, on_delete=models.CASCADE, db_column="ProvinceVersionID")
    city_code = models.CharField(
        max_length=10, unique=True, null=True, blank=False, default="Test", db_column="CityCode")
    description = models.TextField(
        max_length=50, null=True, blank=False, db_column="Description")

    def __str__(self):
        return str(self.city_version_id)

    class Meta:
        index_together = (('city', 'version_num'))
        db_table = 'City_History'


def create_city_history(instance):
    history_instance = CityHistory()
    previous_history_instance = CityHistory.objects.filter(
        city=instance, is_latest_version=True).first()

    history_instance.city = instance

    for field in ["city_name", "is_active"]:
        setattr(history_instance, field, getattr(instance, field))

    province_history_instance = ProvinceHistory.objects.filter(
        province=instance.province, is_latest_version=True).first()
    if province_history_instance:
        history_instance.province_version = province_history_instance

    if previous_history_instance:
        history_instance.version_num = previous_history_instance.version_num + 1
        previous_history_instance.is_latest_version = False
        previous_history_instance.save()

    history_instance.save()


class ServiceOffering(Delete):
    service_offering_id = models.BigAutoField(
        primary_key=True, null=False, db_column="ServiceOfferingID")
    service_offering_name = models.CharField(
        max_length=50, unique=True, blank=False, null=False, db_column="ServiceOfferingName")

    def __str__(self):
        return str(self.service_offering_id)

    class Meta:
        db_table = 'ServiceOffering'


class ServiceOfferingHistory(CommentUpdateDelete):
    service_offering_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="ServiceOfferingVersionID")
    service_offering = models.ForeignKey(
        ServiceOffering, on_delete=models.CASCADE, db_column="ServiceOfferingID")
    service_offering_name = models.CharField(
        max_length=50, blank=False, null=False, db_column="ServiceOfferingName")

    def __str__(self):
        return str(self.service_offering_version_id)

    class Meta:
        index_together = (("service_offering", "version_num"))
        db_table = 'ServiceOffering_History'


class Terminal(Delete):
    terminal_id = models.BigAutoField(
        primary_key=True, null=False, db_column="TerminalID")
    terminal_code = models.CharField(
        max_length=3, blank=False, null=False, db_column="TerminalCode")
    terminal_name = models.CharField(
        max_length=40, blank=False, null=False, db_column="TerminalName")
    city = models.ForeignKey(
        City, on_delete=models.CASCADE, db_column="CityID")
    region = models.ForeignKey(
        Region, on_delete=models.CASCADE, db_column="RegionID")
    description = models.TextField(
        max_length=50, null=True, blank=False, db_column="Description")

    def __str__(self):
        return str(self.terminal_id)

    class Meta:
        index_together = (("terminal_name", "city"),
                          ("terminal_code", "city"),)
        db_table = 'Terminal'


class TerminalHistory(CommentUpdateDelete):
    terminal_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="TerminalVersionID")
    terminal = models.ForeignKey(
        Terminal, on_delete=models.CASCADE, db_column="TerminalID")
    terminal_code = models.CharField(
        max_length=3, blank=False, null=False, db_column="TerminalCode")
    terminal_name = models.CharField(
        max_length=40, blank=False, null=False, db_column="TerminalName")
    city_version = models.ForeignKey(
        CityHistory, on_delete=models.CASCADE, db_column="CityVersionID")
    region_version = models.ForeignKey(
        RegionHistory, on_delete=models.CASCADE, db_column="RegionVersionID")
    description = models.TextField(
        max_length=50, null=True, blank=False, db_column="Description")

    def __str__(self):
        return str(self.terminal_version_id)

    class Meta:
        index_together = (("terminal", "version_num"))
        db_table = 'Terminal_History'


class ServiceLevel(Delete):
    service_level_id = models.BigAutoField(
        primary_key=True, null=False, db_column="ServiceLevelID")
    service_offering = models.ForeignKey(
        ServiceOffering, on_delete=models.CASCADE, db_column="ServiceOfferingID")
    service_level_name = models.CharField(
        max_length=50, null=False, db_column="ServiceLevelName")
    service_level_code = models.CharField(
        max_length=3, null=False, db_column="ServiceLevelCode")
    pricing_type = models.CharField(
        max_length=50, null=False, db_column="PricingType")

    def __str__(self):
        return str(self.service_level_id)

    class Meta:
        index_together = (('service_offering', 'service_level_name'),
                          ('service_offering', 'service_level_code'))
        db_table = 'ServiceLevel'


class ServiceLevelHistory(CommentUpdateDelete):
    service_level_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="ServiceLevelVersionID")
    service_level = models.ForeignKey(
        ServiceLevel, on_delete=models.CASCADE, db_column="ServiceLevelID")
    service_offering_version = models.ForeignKey(
        ServiceOfferingHistory, on_delete=models.CASCADE, db_column="ServiceOfferingVersionID")
    service_level_name = models.CharField(
        max_length=50, null=False, db_column="ServiceLevelName")
    service_level_code = models.CharField(
        max_length=3, null=False, db_column="ServiceLevelCode")
    pricing_type = models.CharField(
        max_length=50, null=False, db_column="PricingType")

    def __str__(self):
        return str(self.service_level_version_id)

    class Meta:
        index_together = (('service_level', 'version_num'))
        db_table = 'ServiceLevel_History'


class SubServiceLevel(Delete):
    sub_service_level_id = models.BigAutoField(
        primary_key=True, null=False, db_column="SubServiceLevelID")
    service_level = models.ForeignKey(
        ServiceLevel, on_delete=models.CASCADE, db_column="ServiceLevelID")
    sub_service_level_name = models.CharField(
        max_length=50, null=False, db_column="SubServiceLevelName")
    sub_service_level_code = models.CharField(
        max_length=2, null=False, db_column="SubServiceLevelCode")

    def __str__(self):
        return str(self.sub_service_level_id)

    class Meta:
        db_table = 'SubServiceLevel'
        unique_together = [['service_level', 'sub_service_level_name', 'sub_service_level_code']]


class SubServiceLevelHistory(CommentUpdateDelete):
    sub_service_level_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="SubServiceLevelVersionID")
    sub_service_level = models.ForeignKey(
        SubServiceLevel, on_delete=models.CASCADE, db_column="SubServiceLevelID")
    service_level_version = models.ForeignKey(
        ServiceLevelHistory, on_delete=models.CASCADE, db_column="ServiceLevelVersionID")
    sub_service_level_name = models.CharField(
        max_length=50, null=False, db_column="SubServiceLevelName")
    sub_service_level_code = models.CharField(
        max_length=2, null=False, db_column="SubServiceLevelCode")

    def __str__(self):
        return str(self.sub_service_level_version_id)

    class Meta:
        index_together = (('sub_service_level', 'version_num'))
        db_table = 'SubServiceLevel_History'


class ServiceMode(Delete):
    service_mode_id = models.BigAutoField(
        primary_key=True, null=False, db_column="ServiceModeID")
    service_offering = models.ForeignKey(
        ServiceOffering, on_delete=models.CASCADE, db_column="ServiceOfferingID")
    service_mode_name = models.CharField(
        max_length=50, null=False, db_column="ServiceModeName")
    service_mode_code = models.CharField(
        max_length=1, null=False, db_column="ServiceModeCode")

    def __str__(self):
        return str(self.service_mode_id)

    class Meta:
        index_together = (('service_offering', 'service_mode_name'),
                          ('service_offering', 'service_mode_code'))
        db_table = 'ServiceMode'


class ServiceModeHistory(CommentUpdateDelete):
    service_mode_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="ServiceModeVersionID")
    service_offering_version = models.ForeignKey(
        ServiceOfferingHistory, on_delete=models.CASCADE, db_column="ServiceOfferingVersionID")
    service_mode = models.ForeignKey(
        ServiceMode, on_delete=models.CASCADE, db_column="ServiceModeID")
    service_mode_name = models.CharField(
        max_length=50, null=False, db_column="ServiceModeName")
    service_mode_code = models.CharField(
        max_length=1, null=False, db_column="ServiceModeCode")

    def __str__(self):
        return str(self.service_mode_version_id)

    class Meta:
        index_together = (('service_mode', 'version_num'))
        db_table = 'ServiceMode_History'


class BasingPoint(Delete):
    basing_point_id = models.BigAutoField(
        primary_key=True, null=False, db_column="BasingPointID")
    basing_point_name = models.CharField(
        max_length=50, unique=True, null=False, blank=False, db_column="BasingPointName")
    province = models.ForeignKey(
        Province, on_delete=models.CASCADE, db_column="ProvinceID")
    basing_point_code = models.CharField(
        max_length=10, unique=True, null=True, blank=False, default="Test", db_column="BasingPointCode")
    description = models.TextField(
        max_length=50, null=True, blank=False, db_column="Description")

    def __str__(self):
        return str(self.basing_point_id)

    class Meta:
        db_table = 'BasingPoint'


class BasingPointHistory(CommentUpdateDelete):
    basing_point_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="BasingPointVersionID")
    basing_point = models.ForeignKey(
        BasingPoint, on_delete=models.CASCADE, db_column="BasingPointID")
    basing_point_name = models.CharField(
        max_length=50, null=False, blank=False, db_column="BasingPointName")
    province_version = models.ForeignKey(
        ProvinceHistory, on_delete=models.CASCADE, db_column="ProvinceVersionID")
    basing_point_code = models.CharField(
        max_length=10, unique=True, null=True, blank=False, default="Test", db_column="BasingPointCode")
    description = models.TextField(
        max_length=50, null=True, blank=False, db_column="Description")

    def __str__(self):
        return str(self.basing_point_version_id)

    class Meta:
        index_together = (('basing_point', 'version_num'))
        db_table = 'BasingPoint_History'


class ServicePoint(Delete):
    service_point_id = models.BigAutoField(
        primary_key=True, null=False, db_column="ServicePointID")
    service_point_name = models.CharField(
        max_length=50, unique=True, null=False, blank=False, db_column="ServicePointName")
    province = models.ForeignKey(
        Province, on_delete=models.CASCADE, db_column="ProvinceID")
    basing_point = models.ForeignKey(
        BasingPoint, on_delete=models.CASCADE, null=True, db_column="BasingPointID")

    def __str__(self):
        return str(self.service_point_id)

    class Meta:
        db_table = "ServicePoint"


class ServicePointHistory(CommentUpdateDelete):
    service_point_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="ServicePointVersionID")
    service_point = models.ForeignKey(
        ServicePoint, on_delete=models.CASCADE, db_column="ServicePointID")
    service_point_name = models.CharField(
        max_length=50, unique=True, null=False, blank=False, db_column="ServicePointName")

    province_version = models.ForeignKey(
        ProvinceHistory, on_delete=models.CASCADE, db_column="ProvinceVersionID")
    basing_point_version = models.ForeignKey(
        BasingPointHistory, on_delete=models.CASCADE, db_column="BasingPointVersionID")

    def __str__(self):
        return str(self.service_point_version_id)

    class Meta:
        index_together = (('service_point', 'version_num'))
        db_table = "ServicePoint_History"


class PostalCode(Delete):
    postal_code_id = models.BigAutoField(
        primary_key=True, null=False, db_column="PostalCodeID")
    postal_code_name = models.CharField(
        max_length=10, null=False, blank=False, db_column="PostalCodeName")
    service_point = models.ForeignKey(
        ServicePoint, on_delete=models.CASCADE, null=False, db_column="ServicePointID")

    def __str__(self):
        return str(self.postal_code_id)

    class Meta:
        db_table = 'PostalCode'


class PostalCodeHistory(CommentUpdateDelete):
    postal_code_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="PostalCodeVersionID")
    postal_code = models.ForeignKey(
        PostalCode, on_delete=models.CASCADE, null=False, db_column="PostalCodeID")
    postal_code_name = models.CharField(
        max_length=10, null=False, blank=False, db_column="PostalCodeName")
    service_point_version = models.ForeignKey(
        ServicePointHistory, on_delete=models.CASCADE, null=False, db_column="ServicePointVersionID")

    def __str__(self):
        return str(self.postal_code_version_id)

    class Meta:
        index_together = (('postal_code', 'version_num'))
        db_table = 'PostalCode_History'


class Unit(Delete):
    unit_id = models.BigAutoField(
        primary_key=True, null=False, db_column="UnitID")
    unit_name = models.CharField(
        max_length=50, null=False, db_column="UnitName")
    unit_symbol = models.CharField(
        max_length=50, null=False, db_column="UnitSymbol")
    unit_type = models.CharField(
        max_length=50, null=False, db_column="UnitType")

    def __str__(self):
        return str(self.unit_id)

    class Meta:
        db_table = 'Unit'


class UnitHistory(CommentUpdateDelete):
    unit_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="UnitVersionID")
    unit = models.ForeignKey(
        Unit, on_delete=models.CASCADE, db_column="UnitID")
    unit_name = models.CharField(
        max_length=50, null=False, db_column="UnitName")
    unit_symbol = models.CharField(
        max_length=50, null=False, db_column="UnitSymbol")
    unit_type = models.CharField(
        max_length=50, null=False, db_column="UnitType")

    def __str__(self):
        return str(self.unit_version_id)

    class Meta:
        index_together = (('unit', 'version_num'))
        db_table = 'Unit_History'


class Account(Delete):
    account_id = models.BigAutoField(
        primary_key=True, null=False, db_column="AccountID")
    account_number = models.CharField(
        max_length=50, null=False, blank=False, db_column="AccountNumber")
    account_owner = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, db_column="AccountOwnerID")
    city = models.ForeignKey(
        City, on_delete=models.CASCADE, null=True, db_column="CityID")
    account_name = models.CharField(
        max_length=100, unique=False, null=False, blank=False, db_column="AccountName")
    account_alias = models.CharField(
        max_length=100, unique=False, null=True, blank=False, db_column="AccountAlias")
    address_line_1 = models.CharField(
        max_length=100, unique=False, null=False, blank=False, db_column="AddressLine1")
    address_line_2 = models.CharField(
        max_length=100, unique=False, null=True, blank=False, db_column="AddressLine2")
    postal_code = models.CharField(
        max_length=10, unique=False, null=False, blank=False, db_column="PostalCode")
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
    external_erp_id = models.CharField(
        max_length=100, unique=False, null=True, blank=True, db_column="ExternalERPID")
    external_city_name = models.CharField(
        max_length=100, unique=False, null=True, blank=True, db_column="ExternalCityName")

    def __str__(self):
        return str(self.account_id)

    class Meta:
        db_table = 'Account'


class AccountHistory(CommentUpdateDelete):
    account_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="AccountVersionID")
    account = models.ForeignKey(
        Account, on_delete=models.CASCADE, db_column="AccountID")
    account_number = models.CharField(
        max_length=50, null=False, blank=False, db_column="AccountNumber")
    account_owner_version = models.ForeignKey(
        UserHistory, on_delete=models.CASCADE, null=True, db_column="AccountOwnerVersionID")
    city_version = models.ForeignKey(
        CityHistory, on_delete=models.CASCADE, null=True, db_column="CityVersionID")
    account_name = models.CharField(
        max_length=100, unique=False, null=False, blank=False, db_column="AccountName")
    account_alias = models.CharField(
        max_length=100, unique=False, null=True, blank=False, db_column="AccountAlias")
    address_line_1 = models.CharField(
        max_length=100, unique=False, null=False, blank=False, db_column="AddressLine1")
    address_line_2 = models.CharField(
        max_length=100, unique=False, null=True, blank=False, db_column="AddressLine2")
    postal_code = models.CharField(
        max_length=10, unique=False, null=False, blank=False, db_column="PostalCode")
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
    external_erp_id = models.CharField(
        max_length=100, unique=False, null=True, blank=True, db_column="ExternalERPID")
    external_city_name = models.CharField(
        max_length=100, unique=False, null=True, blank=True, db_column="ExternalCityName")

    def __str__(self):
        return str(self.account_version_id)

    class Meta:
        index_together = (('account', 'version_num'))
        db_table = 'Account_History'


class Notification(Delete):
    notification_id = models.BigAutoField(
        primary_key=True, null=False, db_column="NotificationID")
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=False, db_column="UserID")
    message = models.TextField(
        null=False, blank=False, default="", db_column="Message")
    timestamp = models.DateTimeField(
        auto_now_add=True, null=False, blank=False, db_column="Timestamp")
    is_read = models.BooleanField(
        null=False, default=False, db_column="IsRead")
    meta = models.TextField(
        null=True, blank=True, default="", db_column="Meta")

    def __str__(self):
        return str(self.notification_id)

    class Meta:
        db_table = 'Notification'


class NotificationHistory(CommentUpdateDelete):
    notification_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="NotificationVersionID")
    notification = models.ForeignKey(
        Notification, on_delete=models.CASCADE, null=False, db_column="NotificationID")
    user_version = models.ForeignKey(
        UserHistory, on_delete=models.CASCADE, null=False, db_column="UserVersionID")
    message = models.TextField(
        null=False, blank=False, default="", db_column="Message")
    timestamp = models.DateTimeField(
        null=False, blank=False, db_column="Timestamp")
    is_read = models.BooleanField(
        null=False, db_column="IsRead")

    def __str__(self):
        return str(self.notification_version_id)

    class Meta:
        index_together = (('notification', 'version_num'))
        db_table = 'Notification_History'


class WeightBreakHeader(Delete):
    weight_break_header_id = models.BigAutoField(
        primary_key=True, null=False, db_column="WeightBreakHeaderID")
    weight_break_header_name = models.CharField(
        max_length=50, unique=False, null=False, blank=False, db_column="WeightBreakHeaderName")
    unit_factor = models.DecimalField(
        max_digits=19, decimal_places=6, null=False, db_column="UnitFactor")
    maximum_value = models.DecimalField(
        max_digits=19, decimal_places=6, null=False, db_column="MaximumValue")
    as_rating = models.BooleanField(
        null=False, default=True, db_column="AsRating")
    has_min = models.BooleanField(
        null=False, default=True, db_column="HasMin")
    has_max = models.BooleanField(
        null=False, default=True, db_column="HasMax")
    base_rate = models.BooleanField(
        null=False, default=True, db_column="BaseRate")
    levels = models.TextField(null=False, blank=False,
                              default="[]", db_column="Levels")
    service_level = models.ForeignKey(
        ServiceLevel, on_delete=models.CASCADE, db_column="ServiceLevelID")
    unit = models.ForeignKey(
        Unit, on_delete=models.CASCADE, db_column="UnitID")

    def __str__(self):
        return str(self.weight_break_header_id)

    class Meta:
        db_table = "WeightBreakHeader"


class WeightBreakHeaderHistory(CommentUpdateDelete):
    weight_break_header_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="WeightBreakHeaderVersionID")
    weight_break_header = models.ForeignKey(
        WeightBreakHeader, on_delete=models.CASCADE, db_column="WeightBreakHeaderID")
    weight_break_header_name = models.CharField(
        max_length=50, null=False, blank=False, db_column="WeightBreakHeaderName")
    unit_factor = models.DecimalField(
        max_digits=19, decimal_places=6, null=False, db_column="UnitFactor")
    maximum_value = models.DecimalField(
        max_digits=19, decimal_places=6, null=False, db_column="MaximumValue")
    as_rating = models.BooleanField(
        null=False, default=True, db_column="AsRating")
    has_min = models.BooleanField(
        null=False, default=True, db_column="HasMin")
    has_max = models.BooleanField(
        null=False, default=True, db_column="HasMax")
    base_rate = models.BooleanField(
        null=False, default=True, db_column="BaseRate")
    levels = models.TextField(null=False, blank=False,
                              default="[]", db_column="Levels")
    service_level_version = models.ForeignKey(
        ServiceLevelHistory, on_delete=models.CASCADE, db_column="ServiceLevelVersionID")
    unit_version = models.ForeignKey(
        UnitHistory, on_delete=models.CASCADE, db_column="UnitVersionID")

    def __str__(self):
        return str(self.weight_break_header_version_id)

    class Meta:
        index_together = (('weight_break_header', 'version_num'))
        db_table = "WeightBreakHeader_History"


class Comment(models.Model):
    id = models.UUIDField(
        auto_created=True,
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        serialize=False, verbose_name='Id')
    entity_uuid = models.CharField(db_column='EntityId', max_length=36)
    entity_version = models.IntegerField(db_column='EntityVersion', null=False)
    tag = models.CharField(db_column='Tag', max_length=100, null=True)
    status = models.CharField(db_column='Status', max_length=25, null=True, default='ACTIVE')
    type = models.CharField(db_column='Type', max_length=25, null=True)
    content = models.TextField(db_column='Content', null=False, blank=False, )
    created_on = models.DateTimeField(
        auto_now_add=True, null=False, blank=False, db_column="CreatedOn")
    created_by = models.CharField(db_column='CreatedBy', max_length=100, null=True)
    attachments = models.TextField(db_column='Attachments', default="[]", null=False)
    files = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'Comment'


class CommentReply(models.Model):
    id = models.UUIDField(
        auto_created=True,
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        serialize=False, verbose_name='Id')
    comment = models.ForeignKey(Comment, related_name='replies', on_delete=models.CASCADE, db_column="Comment")
    status = models.CharField(db_column='Status', max_length=25, null=True, default='ACTIVE')
    content = models.TextField(db_column='Content', null=False, blank=False, )
    created_on = models.DateTimeField(
        auto_now_add=True, null=False, blank=False, db_column="CreatedOn")
    created_by = models.CharField(db_column='CreatedBy', max_length=100, null=True)
    attachments = models.TextField(db_column='Attachments', default="[]", null=False)
    files = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'CommentReply'


# class File(models.Model):
#     id = models.UUIDField(
#         auto_created=True,
#         primary_key=True,
#         default=uuid.uuid4,
#         editable=False,
#         serialize=False,
#         verbose_name='Id',
#         max_length=36)
#     url = models.CharField(
#         db_column='Url',
#         max_length=36)
#     parent_entity = models.UUIDField(
#         editable=True,
#         serialize=True,
#         verbose_name='ParentEntity',
#         max_length=36)
#     created_on = models.DateTimeField(
#         auto_now_add=True, null=False, blank=False, db_column="CreatedOn")
#
#     def __str__(self):
#         return str(self.id)
#
#     class Meta:
#         db_table = 'File'
#

@receiver(models.signals.post_save, sender=Country)
@receiver(models.signals.post_save, sender=Province)
@receiver(models.signals.post_save, sender=City)
@receiver(models.signals.post_save, sender=Region)
@receiver(models.signals.post_save, sender=ServiceOffering)
@receiver(models.signals.post_save, sender=Terminal)
@receiver(models.signals.post_save, sender=ServiceMode)
@receiver(models.signals.post_save, sender=ServiceLevel)
@receiver(models.signals.post_save, sender=Unit)
@receiver(models.signals.post_save, sender=Account)
@receiver(models.signals.post_save, sender=SubServiceLevel)
@receiver(models.signals.post_save, sender=Notification)
@receiver(models.signals.post_save, sender=BasingPoint)
@receiver(models.signals.post_save, sender=ServicePoint)
@receiver(models.signals.post_save, sender=PostalCode)
@receiver(models.signals.post_save, sender=WeightBreakHeader)
def post_save_instance(sender, instance, created, **kwargs):
    from pac.helpers.functions import create_instance_history
    create_instance_history(sender, instance, globals())
