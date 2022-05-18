import multiprocessing as mp

from django.db import transaction

from pac.helpers.functions import batches
from pac.pre_costing.models import (Country, CountryHistory, Province,
                                    ProvinceHistory, create_province_history)
from pac.pre_costing.serializers import ProvinceSerializer
from pac.settings.settings import CPU_COUNT


@transaction.atomic
def bulk_create_province2(data):
    pool = mp.Pool(processes=CPU_COUNT)
    pool.map(batch_create_province, batches(data))
    pool.close()
    pool.join()


@transaction.atomic
def bulk_create_province(data):
    provinces_list = []
    countries_queryset = Country.objects.filter(
        country_code__in=[obj["country_code"] for obj in data])
    countries_dict = {
        instance.country_code: instance for instance in countries_queryset}
    for obj in data:
        if obj["country_code"] in countries_dict:
            obj["country"] = countries_dict[obj["country_code"]]
            del obj["country_code"]
            provinces_list.append(Province(**obj))
    provinces_list = Province.objects.bulk_create(provinces_list)
    country_history_queryset = CountryHistory.objects.filter(country_id__in=[
                                                             province.country_id for province in provinces_list], is_latest_version=True)
    country_history_dict = {
        instance.country_id: instance for instance in country_history_queryset}
    ProvinceHistory.objects.bulk_create(
        [create_province_history_instance(province, country_history_dict) for province in provinces_list])


def create_province_history_instance(instance, country_history_dict):
    history_instance = ProvinceHistory()
    history_instance.province = instance

    for field in ["province_name", "province_code"]:
        setattr(history_instance, field, getattr(instance, field))

    if instance.country_id in country_history_dict:
        history_instance.country_version = country_history_dict[instance.country_id]
    return history_instance
