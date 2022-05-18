import csv
import time
import pyodbc
import os

from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand
from django.urls import reverse

from pac.pre_costing.country import bulk_create_country
from pac.pre_costing.province import bulk_create_province
from pac.pre_costing.city import bulk_create_city


class Command(BaseCommand):
    help = 'Init PAC'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        print("START: LOADING COUNTRIES")

        csv_file = open("pac/fixtures/bulk_create/Country.csv",
                        "r+", encoding='utf-8-sig')
        csv_reader = csv.DictReader(
            csv_file, fieldnames=["country_name", "country_code"])
        country_data = [row for row in csv_reader]

        time_start = time.time()
        bulk_create_country(country_data.copy())
        time_finish = time.time()

        print(f"END: LOADING COUNTRIES IN {time_finish - time_start} SECONDS")

        print("START: LOADING PROVINCES")

        csv_file = open("pac/fixtures/bulk_create/Province.csv",
                        "r+", encoding='utf-8-sig')
        csv_reader = csv.DictReader(
            csv_file, fieldnames=["province_name", "province_code", "country_code"])
        province_data = [row for row in csv_reader]

        time_start = time.time()
        bulk_create_province(province_data.copy())
        time_finish = time.time()

        print(f"END: LOADING PROVINCES IN {time_finish - time_start} SECONDS")

        print("START: LOADING CITIES")
        csv_file = open("pac/fixtures/bulk_create/City.csv",
                        "r+", encoding='utf-8-sig')
        csv_reader = csv.DictReader(
            csv_file, fieldnames=["city_name", "province_code"])
        city_data = [row for row in csv_reader]

        time_start = time.time()
        bulk_create_city(city_data.copy())
        time_finish = time.time()

        print(f"END: LOADING CITIES IN {time_finish - time_start} SECONDS")
