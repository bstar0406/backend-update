import json
import logging

from django.contrib.auth.models import AnonymousUser
from django.db import IntegrityError
from django.http import JsonResponse, HttpResponse, FileResponse
from pyodbc import ProgrammingError
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework_api_key.permissions import HasAPIKey

from pac.helpers.connections import pyodbc_connection
from pac.helpers.mixins import BatchUpdateMixin
from pac.models import Notification, User, Comment, CommentReply, Account
from pac.pre_costing.models import Lane
from pac.rrf.models import RequestQueue
from pac.serializers import (NotificationSerializer,
                             NotificationUpdateSerializer, CommentReplySerializer, AccountSerializer)
from pac.settings import settings
from pac.utils import (save_attachments_to_storage, get_attachment_from_storage, save_comment, get_comments,
                       update_comment, delete_comment)


@api_view(["GET"])
def get_metadata_pyodbc(request, *args, **kwargs):
    cnxn = pyodbc_connection()
    cursor = cnxn.cursor()
    queries = {"countries": "SELECT * FROM dbo.Country",
               "provinces": "SELECT * FROM dbo.Province",
               "regions": "SELECT * FROM dbo.Region",
               "terminals": """
                            SELECT DISTINCT L.*, ISNULL(LC.ServiceOfferingID, 0) as ServiceOfferingID
                            FROM dbo.Terminal L
                            LEFT OUTER JOIN dbo.TerminalCost LC ON LC.TerminalID = L.TerminalID
                """,
               "service_offerings": "SELECT * FROM dbo.ServiceOffering",
               "service_level": "SELECT * FROM dbo.ServiceLevel",
               "units": "SELECT * FROM dbo.Unit",
               "service_mode": "SELECT * FROM dbo.ServiceMode",
               "lane_cost_weight_break_level": "SELECT * FROM dbo.LaneCostWeightBreakLevel ORDER BY WeightBreakLowerBound",
               "terminal_cost_weight_break_level": "SELECT * FROM dbo.TerminalCostWeightBreakLevel ORDER BY WeightBreakLowerBound",
               "language": "SELECT * FROM dbo.Language",
               "currency": "SELECT * FROM dbo.Currency",
               "request_type": "SELECT * FROM dbo.RequestType",
               "request_status_type": "SELECT * FROM dbo.RequestStatusType",
               "freight_class": "SELECT * FROM dbo.FreightClass",
               "rate_base": "SELECT * FROM dbo.RateBase",
               "equipment_type": "SELECT * FROM dbo.EquipmentType",
               "sub_service_level": "SELECT * FROM dbo.SubServiceLevel",
               "basing_points": "SELECT * FROM dbo.BasingPoint",
               "request_section_lane_point_type": "SELECT * FROM dbo.RequestSEctionLanePointType",
               "user_groups": """
                        SELECT P.PersonaName as persona_name, U.UserID AS user_id, U.UserName As user_name
                        FROM dbo.[User] U
                        INNER JOIN dbo.[Persona] P ON U.PersonaID=P.PersonaID
                        WHERE U.IsActive = 1 and U.IsInactiveViewable = 1
                        order by p.PersonaName
               """,
               "personas": "SELECT * FROM dbo.Persona",
               "customer_lookup": """SELECT C.CustomerName as label, C.CustomerID as value, '' as descr
                    FROM dbo.[Customer] C WHERE C.CustomerName IS NOT NULL ORDER BY C.CustomerName ASC""",
               "service_level_lookup": """SELECT SL.ServiceLevelCode as label, SL.ServiceLevelID as value, SL.ServiceLevelName as descr
                                          FROM dbo.[ServiceLevel] SL ORDER BY SL.ServiceLevelCode ASC""",
               "sub_service_level_lookup": """SELECT ssl.SubServiceLevelCode as label, ssl.SubServiceLevelID as value,
                                        sl.ServiceOfferingID as parentId, ssl.SubServiceLevelName descr
                                        FROM dbo.[SubServiceLevel] ssl
                                        LEFT JOIN dbo.ServiceLevel sl ON sl.ServiceLevelID = ssl.ServiceLevelID
                                        ORDER BY ssl.SubServiceLevelCode ASC""",
               "sales_rep_lookup": """SELECT DISTINCT U.UserName as label, U.UserID as value, '' as descr
                    FROM dbo.[User] U
                    INNER JOIN dbo.RequestStatus RSU ON RSU.SalesRepresentativeID = U.UserID
                    ORDER BY U.UserName ASC""",
               "pricing_analyst_lookup": """SELECT DISTINCT U.UserName as label, U.UserID as value, '' as descr
                    FROM dbo.[User] U
                    INNER JOIN dbo.RequestStatus RSU ON RSU.PricingAnalystID = U.UserID
                    ORDER BY U.UserName""",
               "status_lookup": """SELECT RST.RequestStatusTypeName as label, RST.RequestStatusTypeID as value, '' as descr
                    FROM dbo.RequestStatusType RST
                    ORDER BY RST.RequestStatusTypeName ASC""",
               "gateway_terminals": """
                        SELECT T.*
                        FROM dbo.Terminal T
                        INNER JOIN dbo.City Y ON T.CityID = Y.CityID
                        INNER JOIN dbo.Province P ON Y.ProvinceID = P.ProvinceID
                        INNER JOIN dbo.Region R ON P.RegionID = R.RegionID
                        INNER JOIN dbo.Country C ON R.CountryID = C.CountryID
                        WHERE C.CountryCode LIKE 'US' """,
               "commodities": "SELECT * FROM dbo.Commodity",
               }

    payload = {}
    for data_model in queries:
        try:
            cursor.execute(queries[data_model])
            raw_data = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            data_rows = []
            for row in raw_data:
                data_rows.append(dict(zip(columns, row)))
            payload.update(
                {data_model: data_rows})
        except:
            logging.error(f'A lookup field from metadata could not be retrieved: {data_model}')
            payload.update({data_model: []})

    # user_id = self.request.user.user_id
    user_id = kwargs.get("user_id") if settings.DEBUG else 0
    user_id = user_id if user_id > 0 else request.user.user_id
    user = User.objects.filter(user_id=user_id).first()

    payload.update({"user": {"user_id": getattr(user, "user_id", ""), "user_name": getattr(user, "user_name", ""),
                             "user_email": getattr(user, "user_email", ""),
                             "has_self_assign": getattr(user, "has_self_assign", ""),
                             "persona_id": getattr(user.persona, "persona_id", None),
                             "persona_name": getattr(user.persona, "persona_name", None)}})

    return Response(payload, status=status.HTTP_200_OK)


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer

    def get_queryset(self):
        # user_id = self.request.user.user_id
        user_id = self.kwargs.get("user_id")
        user_id = user_id if user_id > 0 else self.request.user.user_id
        return Notification.objects.filter(is_active=True, user_id=user_id)


class NotificationBatchUpdateView(generics.GenericAPIView, BatchUpdateMixin):
    serializer_class = NotificationUpdateSerializer
    queryset = Notification.objects.all()
    lookup_field = "notification_id"

    def patch(self, request, *args, **kwargs):
        return super().batch_update(request, *args, **kwargs)


@api_view(["POST", "GET", "PATCH", "DELETE"])
def comment_handler(request, *args, **kwargs):
    rrf_id = kwargs.get("rrf_id")
    comment_id = kwargs.get("comment_id")

    if request.method == 'GET':
        return JsonResponse(get_comments(rrf_id).data,
                            safe=False,
                            status=status.HTTP_200_OK)
    elif request.method == 'PATCH':
        try:
            serializer = update_comment(request, comment_id)
            return JsonResponse(serializer.data, status=200, safe=False)
        except ValidationError:
            return JsonResponse({"reason": "Comment malformed"}, status=400)
    elif request.method == 'POST':
        try:
            save_comment(request, rrf_id)

            return JsonResponse(get_comments(rrf_id).data,
                                safe=False,
                                status=status.HTTP_200_OK)
        except Exception as error:
            return JsonResponse({"reason": str(error)}, status=500)
    elif request.method == 'DELETE':
        try:
            delete_comment(comment_id)
            return JsonResponse(get_comments(rrf_id).data,
                                safe=False,
                                status=status.HTTP_200_OK)
        except Exception as error:
            return JsonResponse({"reason": str(error)}, status=404)


@api_view(["GET"])
def comment_file_handler(request, *args, **kwargs):
    rrf_id = kwargs.get("rrf_id")
    comment_id = kwargs.get("comment_id")
    file_name = kwargs.get("file_name")

    user_id = kwargs.get("user_id") or 0
    user_id = user_id if user_id > 0 else request.user.user_id

    # UserPersona check on RequestQueue if required
    if RequestQueue.objects.filter(completed_on=None, request__request_number=rrf_id).count():
        comment = Comment.objects.filter(id=comment_id).first()
        if not comment:
            comment = CommentReply.objects.filter(id=comment_id).first()

        if comment:
            if comment.attachments:
                attachment = next((x for x in json.loads(comment.attachments) if x['name'] == file_name), None)
                if attachment:
                    comment_file = get_attachment_from_storage(attachment['container'], attachment['blob'])

                    if comment_file:
                        return FileResponse(comment_file, as_attachment=True, filename=file_name)
                    else:
                        return HttpResponse("Comment File not downloaded", status=status.HTTP_404_NOT_FOUND)
                else:
                    return HttpResponse("Comment does not have this attachment file name",
                                        status=status.HTTP_404_NOT_FOUND)
            else:
                return HttpResponse("Comment has no attachments", status=status.HTTP_404_NOT_FOUND)
        else:
            return HttpResponse("Comment not found", status=status.HTTP_404_NOT_FOUND)
    else:
        return HttpResponse("User does not have access to Request", status=status.HTTP_401_UNAUTHORIZED)


@api_view(["POST"])
def add_comment_reply(request, *args, **kwargs):
    rrf_id = kwargs.get("rrf_id")
    comment_id = kwargs.get("comment_id")
    # workaround to work locally without JWT, only for debugging
    if settings.DEBUG:
        user_name = "Anonymous User" if isinstance(request.user, AnonymousUser) else request.user.user_name

    try:
        Comment.objects.get(id=comment_id)

    except Comment.DoesNotExist:
        return HttpResponse("Comment not found.", status=404)

    attachments = save_attachments_to_storage(request)

    comment_reply_serializer = CommentReplySerializer(data=request.data, many=False,
                                                      context={"attachments": attachments,
                                                               "comment_id": comment_id,
                                                               "entity_uuid": rrf_id,
                                                               "username": user_name
                                                               })
    if comment_reply_serializer.is_valid():
        comment_reply_serializer.save()
        return Response(comment_reply_serializer.data, status=status.HTTP_200_OK)
    return Response(comment_reply_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PATCH"])
def add_cost_override(request, *args, **kwargs):
    # rrf_id = kwargs.get("rrf_id")
    try:
        lanes = request.data["request_section_lane_ids"]
        cnxn = pyodbc_connection()
        cursor = cnxn.cursor()
        request_data = request.data

        request_section_lane_ids = ','.join(map(str, lanes))
        cost_override_pickup_count = request_data.get("cost_override_pickup_count", 0)
        cost_override_delivery_count = request_data.get("cost_override_delivery_count")
        cost_override_dock_adjustment = request_data["cost_override_dock_adjustment"]
        cost_override_margin = json.dumps(request_data["cost_override_margin"])
        cost_override_density = json.dumps(request_data["cost_override_density"])
        cost_override_pickup_cost = json.dumps(request_data["cost_override_pickup_cost"])
        cost_override_delivery_cost = json.dumps(request_data["cost_override_delivery_cost"])
        cost_override_accessorials_value = json.dumps(request_data["cost_override_accessorials_value"])
        cost_override_accessorials_percentage = json.dumps(request_data["cost_override_accessorials_percentage"])

        cursor.execute(
            "EXEC [dbo].[RequestSectionLane_Cost_Override] ?, ?, ?, ?, ?, ?, ?, ?, ?, ?",
            request_section_lane_ids,
            cost_override_pickup_count,
            cost_override_delivery_count,
            cost_override_dock_adjustment,
            cost_override_margin,
            cost_override_density,
            cost_override_pickup_cost,
            cost_override_delivery_cost,
            cost_override_accessorials_value,
            cost_override_accessorials_percentage)
        cursor.commit()

        return Response(status=status.HTTP_200_OK)

    except ProgrammingError as e:
        logging.error("{} {}".format(type(e).__name__, e.args))
        return JsonResponse({"Exception": {"code": e.args[0], "reason": e.args[1]}}, status=500)
    finally:
        pass


@api_view(["POST", "GET", "PATCH"])
@permission_classes([HasAPIKey])
def account_handler(request, *args, **kwargs):
    external_erp_id = kwargs.get("external_erp_id")
    if request.method == 'GET':
        account = Account.objects.filter(external_erp_id=external_erp_id).first()
        if account:
            account_serializer = AccountSerializer(account, many=False)
            return JsonResponse(account_serializer.data,
                                safe=False,
                                status=status.HTTP_200_OK)
        else:
            return JsonResponse({"reason": "account not found"},
                                safe=False,
                                status=status.HTTP_404_NOT_FOUND)

    elif request.method == 'PATCH':

        account = Account.objects.get(external_erp_id=external_erp_id)
        data = JSONParser().parse(request)
        serializer = AccountSerializer(account,
                                       data=data,
                                       partial=True)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data,
                                safe=False,
                                status=status.HTTP_200_OK)
        return JsonResponse(safe=False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    elif request.method == 'POST':
        data = request.data
        account_serializer = AccountSerializer(data=request.data,
                                               many=False)
        if account_serializer.is_valid():
            try:
                account_serializer.save()
                return JsonResponse(account_serializer.data, status=status.HTTP_200_OK)
            except Exception as exception:
                if isinstance(exception, IntegrityError):
                    return JsonResponse(
                        data={"reason": "integrity constraint violation", "details": exception.args[1]},
                        status=status.HTTP_422_UNPROCESSABLE_ENTITY)

            return JsonResponse(safe=False, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
def service_service_migration(request, *args, **kwargs):
    lanes = list(Lane.objects.all())
    print("dsd")
