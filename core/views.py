from django.db.models import Prefetch
from rest_framework import generics, serializers, status, views
from rest_framework.response import Response

from core.models import Persona, User
from core.serializers import UserRetrieveSerializer, UserUpdateSerializer
from pac.rrf.models import UserServiceLevel, RequestSectionLane, Request, RequestStatus, RequestStatusType
from pac.rrf.workflow import WorkflowManager
from pac.notifications import NotificationManager

from Function_PricingCalculator.utils import RequestCalculator

from Function_BaseRate_RateWare_Load.utils import RateWareTariffLoader
from rest_framework.permissions import AllowAny
from core.serializers import LoginSerializer, UserSerializer
from django.contrib.auth import login as django_login
import time
import json


class UserListView(generics.ListAPIView):
    serializer_class = UserRetrieveSerializer
    queryset = User.objects.filter(azure_is_active=True).select_related('persona', 'user_manager__persona').prefetch_related(
        Prefetch('userservicelevel_set', queryset=UserServiceLevel.objects.filter(is_active=True).select_related('service_level')))


class UserUpdateView(generics.UpdateAPIView):
    serializer_class = UserUpdateSerializer
    queryset = User.objects.filter(azure_is_active=True)
    lookup_field = 'user_id'

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_update(serializer)
        data = UserRetrieveSerializer(instance).data
        return Response(data)

    def perform_update(self, serializer):
        return serializer.save()


class UserHeaderView(views.APIView):

    def get(self, request, *args, **kwargs):
        total_users = User.objects.filter(azure_is_active=True).count()
        active_users = User.objects.filter(
            azure_is_active=True, is_active=True).count()
        inactive_users = User.objects.filter(
            azure_is_active=True, is_active=False).count()
        new_users = User.objects.filter(persona__isnull=True).count()

        payload = {
            "total_users": total_users,
            "active_users": active_users,
            "inactive_users": inactive_users,
            "new_users": new_users
        }

        return Response(payload, status=status.HTTP_200_OK)


class DevelopView(views.APIView):
    def get(self, request, *args, **kwargs):

        # Rateware
        # loader = RateWareTariffLoader()
        # loader.load_available_tariffs(True)
        # loader.load_db_base_rates(True)
        # loader.update_db_rate_bases(True)
        # loader.save_rate_bases(True)
        #522, 536 and 540 and 543

        
        # 738 - filters
        # pricing_engine_rating_filters = '{"is_calculate_all": false, "context_id": "93153ee8d4144951baefb87414a0dccf", "request_number": "50E0F697811140499E96CAD920749357", "request_sections": [{"request_section_id": 559, "request_section_lanes": [{"request_section_lane_id": 80309, "weight_breaks": ["0", "5000", "20000"]}]}]}'
        pricing_engine_rating_filters = '{"is_calculate_all": true, "context_id": "42363478d6d14089aa1872adeff349ad", "request_number": "77E9F9CF5D06414D9246E11270338496", "request_sections": []}'

        print('Hi')

        #732 - lots of lanes - broken        
        #733 - lots of lanes

        # Pricing Calc 728
        start_time = time.time()
        calc = RequestCalculator(740, json.loads(pricing_engine_rating_filters))
        calc.pre_run_clear_data(True)
        calc.pre_run_validate_data(True)
        calc.request_setup(True)
        calc.calculate_lane_density(True)
        calc.calculate_line_haul_cost(True)
        calc.calculate_dock_cost(True)
        calc.calculate_pickup_cost(True)
        calc.calculate_delivery_cost(True)
        calc.calculate_fak_rate(True)
        calc.calculate_splits_all(True)
        calc.calculate_margin(True)
        calc.calculate_profitability(True)
        calc.calculate_rates(True)
        calc.save_data()

        # Workflow
        # Return Workflow to return_request_status
        # request_id = 580
        # return_request_status = 36

        # request_instance = Request.objects.filter(
        #     request_id=request_id
        # ).select_related(
        #     'request_information__customer__account',
        #     'request_information__request_type'
        # ).first()

        # request_status_instance = RequestStatus.objects.filter(request=request_instance).first()

        # current_request_status_type_instance = RequestStatusType.objects.filter(
        #     request_status_type_name="With Pricing Engine").first()

        # next_request_status_type_instance = RequestStatusType.objects.filter(
        #     request_status_type_id=return_request_status).first()

        # workflow_manager = WorkflowManager(request_status=request_status_instance,
        #                                    request=request_instance,
        #                                    current_request_status_type=current_request_status_type_instance,
        #                                    next_request_status_type=next_request_status_type_instance,
        #                                    pricing_engine_rating_filters=None)

        # if current_request_status_type_instance:
        #     workflow_manager.close_request_queue()
        # if next_request_status_type_instance:
        #     actionable_users = workflow_manager.generate_request_queue()

        # for user in actionable_users:
        #     NotificationManager.send_notification(user, f"Request {request_id} Pricing Engine processing is complete")

        # import pdb
        # pdb.set_trace()

        print("--- Calculator completed in %s seconds ---" % (time.time() - start_time))

        return Response(None, status=status.HTTP_200_OK)


class LoginAPI(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        django_login(request, user)
        token_str = request.META.get('HTTP_X_CSRFTOKEN', '')
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": token_str
        })