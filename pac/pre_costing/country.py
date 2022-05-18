from pac.pre_costing.models import Country, CountryHistory, create_country_history
from pac.pre_costing.serializers import CountrySerializer

from django.db import transaction


@transaction.atomic
def bulk_create_country(data):
    countries_list = Country.objects.bulk_create(
        [Country(**obj) for obj in data])
    CountryHistory.objects.bulk_create(
        [create_country_history_instance(obj) for obj in countries_list])


def create_country_history_instance(instance):
    history_instance = CountryHistory()
    history_instance.country_id = instance

    for field in ["country_name", "country_code"]:
        setattr(history_instance, field, getattr(instance, field))

    return history_instance
