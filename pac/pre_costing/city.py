from pac.pre_costing.models import City, Province, CityHistory, ProvinceHistory
from pac.pre_costing.serializers import CitySerializer

from django.db import transaction


@transaction.atomic
def bulk_create_city(data):
    cities_list = []
    provinces_queryset = Province.objects.filter(
        province_code__in=[obj["province_code"] for obj in data])
    provinces_dict = {
        instance.province_code: instance for instance in provinces_queryset}
    for obj in data:
        if obj["province_code"] in provinces_dict:
            obj["province"] = provinces_dict[obj["province_code"]]
            del obj["province_code"]
            cities_list.append(City(**obj))
    cities_list = City.objects.bulk_create(cities_list)
    province_history_queryset = ProvinceHistory.objects.filter(province_id__in=[
                                                               city.province_id for city in cities_list], is_latest_version=True)
    province_history_dict = {
        instance.province_id: instance for instance in province_history_queryset}
    CityHistory.objects.bulk_create([create_city_history_instance(
        city, province_history_dict) for city in cities_list])


def create_city_history_instance(instance, province_history_dict):
    history_instance = CityHistory()

    history_instance.city = instance
    history_instance.city_name = instance.city_name

    if instance.province_id in province_history_dict:
        history_instance.province_version = province_history_dict[instance.province_id]

    return history_instance
