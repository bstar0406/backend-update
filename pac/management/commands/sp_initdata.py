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
    help = 'Init PAC Stored Procedures'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        print("CONNECTING TO MSSQL USING PYODBC...")
        try:
            # NOTE: Insert your DB connection settings here
            cnxn = pyodbc.connect(
                '''DRIVER={{ODBC Driver 17 for SQL Server}};
                SERVER=localhost;
                DATABASE=pac;
                UID=sa;
                PWD={0}'''.format(os.getenv("MSSQL_PASSWORD")))
            cnxn.setencoding('utf-8')
        except Exception as e:
            print(f"CONNECTION FAILED DUE TO {str(e)}")
            return
        print("CONNECTED SUCCESFULLY")
        cursor = cnxn.cursor()

        print("START: LOADING COUNTRIES")

        csv_file = open("pac/fixtures/bulk_create/Country.csv",
                        "r+", encoding='utf-8-sig')
        csv_reader = csv.DictReader(
            csv_file, fieldnames=["country_name", "country_code"])
        country_data = [row for row in csv_reader]

        time_start = time.time()
        sql = """ DECLARE @CountryTableType as CountryTableType
        INSERT INTO @CountryTableType VALUES
        """
        for country in country_data:
            sql += "\n(" + country["country_name"].replace(",", "") + ", " + \
                country["country_code"] + "),"
        sql = sql.rstrip(',')
        sql += """\nEXEC [dbo].[Country_Insert_Bulk] @CountryTableType"""
        cursor.execute(sql)
        time_finish = time.time()

        print(f"END: LOADING COUNTRIES IN {time_finish - time_start} SECONDS")

        print("START: LOADING PROVINCES")

        csv_file = open("pac/fixtures/bulk_create/Province.csv",
                        "r+", encoding='utf-8-sig')
        csv_reader = csv.DictReader(
            csv_file, fieldnames=["province_name", "province_code", "country_code"])
        province_data = [row for row in csv_reader]

        time_start = time.time()
        sql = """ DECLARE @ProvinceTableType as ProvinceTableType
        INSERT INTO @ProvinceTableType VALUES
        """
        for province in province_data:
            sql += "\n(" + province["province_name"].replace(",", "") + ", " + \
                province["province_code"] + ", " + \
                province["country_code"] + "),"
        sql = sql.rstrip(',')
        sql += """\nEXEC [dbo].[Province_Insert_Bulk] @ProvinceTableType"""
        cursor.execute(sql)
        time_finish = time.time()

        print(f"END: LOADING PROVINCES IN {time_finish - time_start} SECONDS")

        print("START: LOADING CITIES")

        csv_file = open("pac/fixtures/bulk_create/City.csv",
                        "r+", encoding='utf-8-sig')
        csv_reader = csv.DictReader(
            csv_file, fieldnames=["city_name", "province_code"])
        city_data = [row for row in csv_reader]

        time_start = time.time()
        sql = """ DECLARE @CityTableType as CityTableType
        INSERT INTO @CityTableType VALUES
        """
        for city in city_data:
            sql += "\n(" + city["city_name"].replace(",", "") + ", " + \
                city["province_code"] + "),"
        sql = sql.rstrip(',')
        sql += """\nEXEC [dbo].[City_Insert_Bulk] @CityTableType"""
        cursor.execute(sql)
        time_finish = time.time()

        print(f"END: LOADING CITIES IN {time_finish - time_start} SECONDS")
