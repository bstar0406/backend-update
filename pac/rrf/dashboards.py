import io
import json
import logging
logging.getLogger().setLevel(logging.INFO)
import uuid
from datetime import datetime, timezone
import pdb
import openpyxl
from django.db import connection, transaction
from django.db.models import Count
from django.http import JsonResponse, HttpResponse
from rest_framework import generics, mixins, status, views, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response

import pac.rrf.queries as queries
import pac.rrf.dashboard_queries as dQueries
from core.models import User
from pac.helpers.connections import pyodbc_connection
from pac.rrf import enums
import pac.validation as validation
from django.core import serializers
from core.schemas import (DashboardRequestSchema)
from jsonschema import validate
from core.app_view import AppView

class GetDashboardRequestHeader(views.APIView):
    # get the counts of values related to the Request Dashboard for display above the dashboard
    def get(self, request, *args, **kwargs):
        # user_id = self.request.user.user_id
        user_id = kwargs.get("user_id")
        user_id = user_id if user_id > 0 else self.request.user.user_id
        cnxn = pyodbc_connection()
        cursor = cnxn.cursor()
        query = queries.GET_DASHBOARD_HEADER.format(user_id)

        cursor.execute(query)
        raw_data = cursor.fetchone()
        payload = json.loads(raw_data[0]) if raw_data[0] else []

        return Response(payload, status=status.HTTP_200_OK)

class RequestFilteredView(AppView):
    PRIMARY_TABLE = 'dbo.Request'
    PRIMARY_KEY = 'r.RequestID'
    COLUMN_MAPPING = dQueries.ColumnMapping
    schema = DashboardRequestSchema
    GET_FILTERED_QUERY = dQueries.GET_FILTERED_QUERY

    def prepare_filter(self, data, kwargs):
        service_offering_id = kwargs.get("service_offering_id")
        self.GET_FILTERED_QUERY = self.GET_FILTERED_QUERY.format(
            service_offering_id=service_offering_id,
            type_filter=""" AND R.UniType IS NULL""",
            user_id = 59 #self.request.user.user_id
        )
        return data


class SpeedsheetFilteredView(AppView):
    PRIMARY_TABLE = 'dbo.Request'
    PRIMARY_KEY = 'r.RequestID'
    COLUMN_MAPPING = dQueries.ColumnMapping
    schema = DashboardRequestSchema
    GET_FILTERED_QUERY = dQueries.GET_FILTERED_QUERY

    def prepare_filter(self, data, kwargs):
        service_offering_id = kwargs.get("service_offering_id")
        self.GET_FILTERED_QUERY = self.GET_FILTERED_QUERY.format(
            service_offering_id=service_offering_id,
            type_filter=""" AND R.UniType = 'SPEEDSHEET' """,
            user_id = 59 #self.request.user.user_id
        )
        return data

class GetRequestHeaderPyodbcView(views.APIView):
    # gets counts related to a specific request for the header above the request
    def get(self, request, *args, **kwargs):
        # user_id = self.request.user.user_id
        user_id = kwargs.get("user_id")
        user_id = user_id if user_id > 0 else self.request.user.user_id

        request_number = kwargs.get("request_number")
        cnxn = pyodbc_connection()
        cursor = cnxn.cursor()
        query = queries.GET_REQUEST_HEADER.format(request_number, user_id)

        cursor.execute(query)
        raw_data = cursor.fetchone()
        payload = json.loads(raw_data[0]) if raw_data[0] else []

        return Response(payload, status=status.HTTP_200_OK)

def __init__(self):
    pass
