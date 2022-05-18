import json
import random

from django.test import TestCase
from django.urls import reverse
from model_bakery import baker
from rest_framework.test import APIClient, APITestCase
from unittest import skip


from core.models import Persona, User
from pac.models import (Account, City, Notification, ServiceLevel,
                        SubServiceLevel, WeightBreakHeader)
from pac.rrf.models import (Currency, Customer, EquipmentType, FreightClass,
                            Language, RateBase, Request, RequestAccessorials,
                            RequestHistory, RequestInformation,
                            RequestInformationHistory, RequestLane,
                            RequestLaneHistory, RequestProfile,
                            RequestProfileHistory, RequestQueue,
                            RequestSection, RequestStatus, RequestStatusType,
                            RequestType, UserServiceLevel)
from pac.rrf.serializers import (CustomerSerializer,
                                 RequestInformationSerializer,
                                 RequestLaneSerializer,
                                 RequestProfileSerializer,
                                 RequestSectionSerializer)

class PreCostingMockTest(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.request_number_set = set()

    def generate_request_number(self):
        request_number = random.randint(1, 999999)
        if request_number in self.request_number_set:
            request_number = self.generate_request_number()
        self.request_number_set.add(request_number)
        return request_number

    def test_request_information_update(self):
        request_number = self.generate_request_number()
        service_level = baker.make(ServiceLevel)
        city = baker.make(City)
        account_owner = baker.make(User)
        account = baker.make(Account, account_owner=account_owner)
        customer = baker.make(
            Customer, service_level=service_level, city=city, account=account, customer_name="Test 1")
        request_type = baker.make(RequestType)
        language = baker.make(Language)
        currency = baker.make(Currency)
        request_information = baker.make(
            RequestInformation, request_number=request_number, customer=customer, request_type=request_type, language=language, currency=currency, extended_payment_days=1)
        request_profile = baker.make(
            RequestProfile, request_number=request_number)
        request_lane = baker.make(RequestLane, request_number=request_number)
        request_accessorials = baker.make(
            RequestAccessorials, request_number=request_number)
        initiated_by = baker.make(User)
        submitted_by = baker.make(User)

        request = baker.make(
            Request, request_number=request_number, request_information=request_information, request_profile=request_profile, request_lane=request_lane, request_accessorials=request_accessorials, initiated_by=initiated_by, submitted_by=submitted_by)

        customer.customer_name = "Test 2"
        request_information.extended_payment_days = 2

        payload = {"customer": CustomerSerializer(customer).data, "request_information": RequestInformationSerializer(
            request_information).data, "is_macro_save": True}

        response = self.client.put(
            reverse('request-info-update'), payload, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Customer.objects.filter(
            customer_id=customer.customer_id).first().customer_name, "Test 2")
        self.assertEqual(RequestInformation.objects.filter(
            request_information_id=request_information.request_information_id).first().extended_payment_days, 2)
        self.assertEqual(RequestHistory.objects.filter(request=request, is_latest_version=True).first().request_information_version_id,
                         RequestInformationHistory.objects.filter(request_information=request_information, is_latest_version=True).first().pk)

    def test_request_profile_update(self):
        request_number = self.generate_request_number()
        request_type = baker.make(RequestType)
        request_information = baker.make(RequestInformation)
        request_profile = baker.make(
            RequestProfile, avg_weight_density=1.0, request_number=request_number)
        request_lane = baker.make(RequestLane)
        request_accessorials = baker.make(RequestAccessorials)
        initiated_by = baker.make(User)
        submitted_by = baker.make(User)

        request = baker.make(
            Request, request_number=request_number, request_information=request_information, request_profile=request_profile, request_lane=request_lane, request_accessorials=request_accessorials, initiated_by=initiated_by, submitted_by=submitted_by)

        request_profile.avg_weight_density = 2.0

        payload = {"request_profile": RequestProfileSerializer(
            request_profile).data, "is_macro_save": True}

        response = self.client.put(
            reverse('request-profile-update'), payload, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(RequestProfile.objects.filter(
            request_profile_id=request_profile.request_profile_id).first().avg_weight_density, 2.0)
        self.assertEqual(RequestHistory.objects.filter(request=request, is_latest_version=True).first().request_profile_version_id,
                         RequestProfileHistory.objects.filter(request_profile=request_profile, is_latest_version=True).first().pk)

    def test_request_retrieve_history(self):
        request_number = self.generate_request_number()
        request = baker.make(
            Request, request_number=request_number, is_active=False)

        for i in range(5):
            request.save()

        self.assertFalse(request.is_active)

        request.is_active = True
        request.save()

        self.assertTrue(request.is_active)

        response = self.client.get(
            reverse('request-history', kwargs={"request_id": request.request_id}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 7)
        self.assertFalse(response.data[5]["is_active"])
        self.assertTrue(response.data[6]["is_active"])

    @skip("Broken Stored Proc - dbo.RequestLane_Revert - Invalid column name 'Cost'.")
    def test_request_revert_version(self):
        request_number = self.generate_request_number()
        # request = baker.make(Request, request_number=request_number, is_active=False, request_profile__is_valid_data=True)
        request = baker.make(Request, request_number=request_number, is_active=False, 
            request_information__is_valid_data=True,
            request_profile__is_valid_data=True,
            request_accessorials__is_valid_data=True,
            request_lane__is_valid_data=True)

        for i in range(5):
            request.save()

        self.assertFalse(request.is_active)

        request.is_active = True
        request.save()

        self.assertTrue(request.is_active)

        latest_request_history_version = RequestHistory.objects.filter(
            request=request, is_latest_version=True).first()

        self.assertIsInstance(latest_request_history_version, RequestHistory)
        self.assertEqual(latest_request_history_version.version_num, 7)
        self.assertIsNone(latest_request_history_version.base_version)

        response = self.client.put(
            reverse('request-revert', kwargs={"request_id": request.request_id, "version_num": 3}))

        request = Request.objects.filter(request_id=request.request_id).first()
        latest_request_history_version = RequestHistory.objects.filter(
            request=request, is_latest_version=True).first()

        self.assertEqual(response.status_code, 200)
        self.assertFalse(request.is_active)
        self.assertEqual(latest_request_history_version.base_version, 3)

    def test_request_reassign(self):
        request_number = self.generate_request_number()
        old_sales_representative = baker.make(User)
        old_pricing_analyst = baker.make(User)
        current_editor = baker.make(User)
        request = baker.make(Request, request_number=request_number, request_information__is_extended_payment=False)
        # request_status_type_next = baker.make(RequestStatusType, request_status_type_name="Pending EPT Approval", is_secondary=False)
        request_status_type = baker.make(RequestStatusType)
        request_status = baker.make(RequestStatus, request=request, request_status_type=request_status_type,
                                    sales_representative=old_sales_representative, pricing_analyst=old_pricing_analyst, 
                                    current_editor=current_editor)
        request_queue = baker.make(RequestQueue, request=request, is_secondary=True, request_status_type=request_status_type)

        new_sales_representative = baker.make(User)
        new_pricing_analyst = baker.make(User)

        payload = {"sales_representative": new_sales_representative.user_id,
                   "pricing_analyst": new_pricing_analyst.user_id}

        self.assertEqual(request_status.sales_representative.user_id,
                         old_sales_representative.user_id)
        self.assertEqual(request_status.pricing_analyst.user_id,
                         old_pricing_analyst.user_id)

        response = self.client.patch(reverse(
            'request-reassign', kwargs={"request_id": request.request_id}), payload, format='json')

        request_status = RequestStatus.objects.filter(request=request).first()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(request_status.sales_representative.user_id,
                         new_sales_representative.user_id)
        self.assertEqual(request_status.pricing_analyst.user_id,
                         new_pricing_analyst.user_id)

    def test_request_lane_retrieve_history_version(self):
        request_number = self.generate_request_number()
        request_lane = baker.make(
            RequestLane, request_number=request_number, num_sections=1)
        request_profile = baker.make(
            RequestProfile, request_number=request_number)
        request = baker.make(
            Request, request_number=request_number, request_lane=request_lane, request_profile=request_profile)

        for i in range(2, 7):
            request_lane.num_sections = i
            request_lane.save()
            request.save()

        response = self.client.get(reverse('request-lane-number-history-get', kwargs={
                                   "request_number": request_number, "version_num": 4}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["num_sections"], 4)

    @skip("Broken Stored Proc - dbo.RequestLane_History_Update - Invalid column name 'Cost'.")
    def test_request_lane_update(self):
        request_number = self.generate_request_number()
        request_type = baker.make(RequestType)
        request_information = baker.make(RequestInformation)
        request_profile = baker.make(
            RequestProfile, request_number=request_number)
        request_lane = baker.make(
            RequestLane, is_valid_data=False, request_number=request_number)
        request_accessorials = baker.make(RequestAccessorials)
        initiated_by = baker.make(User)
        submitted_by = baker.make(User)

        request = baker.make(
            Request, request_number=request_number, request_information=request_information, request_profile=request_profile, request_lane=request_lane, request_accessorials=request_accessorials, initiated_by=initiated_by, submitted_by=submitted_by)

        request_lane.is_valid_data = True

        payload = {"request_lane": RequestLaneSerializer(
            request_lane).data, "is_macro_save": True}

        response = self.client.put(
            reverse('request-lane-update'), payload, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(RequestLane.objects.filter(
            request_lane_id=request_lane.request_lane_id).first().is_valid_data)
        self.assertEqual(RequestHistory.objects.filter(request=request, is_latest_version=True).first().request_lane_version_id,
                         RequestLaneHistory.objects.filter(request_lane=request_lane, is_latest_version=True).first().pk)

    def test_request_section_retrieve_history_version(self):
        request_number = self.generate_request_number()
        request_lane = baker.make(
            RequestLane, request_number=request_number, num_sections=1)
        request = baker.make(
            Request, request_number=request_number, request_lane=request_lane)

        rate_base = baker.make(RateBase)
        override_class = baker.make(FreightClass)
        equipment_type = baker.make(EquipmentType)
        sub_service_level = baker.make(SubServiceLevel)

        for i in range(5):
            request_section = baker.make(
                RequestSection, request_lane=request_lane, rate_base=rate_base, override_class=override_class, equipment_type=equipment_type, sub_service_level=sub_service_level)
            request.save()

        response = self.client.get(reverse('request-section-number-history-list', kwargs={
            "request_number": request_number, "version_num": 3}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 5)

    def test_request_section_create_update_duplicate(self):
        request_lane = baker.make(RequestLane, num_sections=0)
        rate_base = baker.make(RateBase)
        override_class = baker.make(FreightClass)
        equipment_type = baker.make(EquipmentType)
        sub_service_level = baker.make(SubServiceLevel)
        weight_break_header = baker.make(WeightBreakHeader)
        request_section = baker.make(RequestSection, section_name="test", request_lane=request_lane, rate_base=rate_base, override_class=override_class,
                                     equipment_type=equipment_type, sub_service_level=sub_service_level, weight_break_header=weight_break_header)
        request_section.section_name = "passed"

        payload = {"request_sections": [RequestSectionSerializer(baker.prepare(RequestSection, request_lane=request_lane, rate_base=rate_base, override_class=override_class, equipment_type=equipment_type,
                                                                               sub_service_level=sub_service_level, weight_break_header=weight_break_header)).data for i in range(5)] + [RequestSectionSerializer(request_section).data]}
        response = self.client.put(
            reverse('request-section-create-update-duplicate'), payload, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(RequestSection.objects.filter(
            request_section_id=request_section.request_section_id).first().section_name, "passed")
        self.assertEqual(len(RequestSection.objects.all()), 6)
        self.assertEqual(RequestLane.objects.filter(request_lane_id=request_lane.request_lane_id).first(
        ).num_sections, RequestSection.objects.filter(request_lane=request_lane, is_active=True).count())

    def test_request_section_list(self):
        request_number = self.generate_request_number()
        request_lane = baker.make(RequestLane, request_number=request_number)
        rate_base = baker.make(RateBase)
        override_class = baker.make(FreightClass)
        equipment_type = baker.make(EquipmentType)
        sub_service_level = baker.make(SubServiceLevel)
        request_section = baker.make(RequestSection, request_lane=request_lane, rate_base=rate_base,
                                     override_class=override_class, equipment_type=equipment_type, sub_service_level=sub_service_level, _quantity=5)
        request_lane = baker.make(RequestLane)
        request_section = baker.make(RequestSection, request_lane=request_lane, rate_base=rate_base,
                                     override_class=override_class, equipment_type=equipment_type, sub_service_level=sub_service_level, _quantity=5)

        response = self.client.get(
            reverse('request-section-list', kwargs={"request_number": request_number}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 5)

    @skip("RequestApproval Model Changed")
    def test_request_approval_deal_review_meeting_approved(self):
        request = baker.make(Request, request_information__is_valid_data=True)
        pricing_analyst = baker.make(User)
        sales_representative = baker.make(User)
        request_status = baker.make(RequestStatus, request=request,
                                    pricing_analyst=pricing_analyst, sales_representative=sales_representative)
        request_approval = baker.make(
            RequestApproval, request=request, deal_review_meeting_approved=None)

        self.assertEqual(Notification.objects.all().count(), 0)

        request_approval.deal_review_meeting_approved = True
        request_approval.save()

        response = self.client.get(
            reverse('notification-list', kwargs={"user_id": sales_representative.user_id}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

        response = self.client.get(
            reverse('notification-list', kwargs={"user_id": pricing_analyst.user_id}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    @skip("RequestApproval Model Changed")
    def test_request_approval_pricing_committee_review_approved(self):
        request = baker.make(Request, request_information__is_valid_data=True,
            request_profile__is_valid_data=True,
            request_accessorials__is_valid_data=True,
            request_lane__is_valid_data=True,
            request_information__is_extended_payment=False)
        pricing_analyst = baker.make(User)
        sales_representative = baker.make(User)
        request_status = baker.make(RequestStatus, request=request,
                                    pricing_analyst=pricing_analyst, sales_representative=sales_representative)
        request_approval = baker.make(
            RequestApproval, request=request, pricing_committee_review_approved=None)

        self.assertEqual(Notification.objects.all().count(), 0)

        request_approval.pricing_committee_review_approved = True
        request_approval.save()

        response = self.client.get(
            reverse('notification-list', kwargs={"user_id": sales_representative.user_id}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

        response = self.client.get(
            reverse('notification-list', kwargs={"user_id": pricing_analyst.user_id}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    @skip("RequestApproval Model Changed")
    def test_request_approval_priority_increase_approved(self):
        request = baker.make(Request, request_information__is_valid_data=True, request_information__is_extended_payment=False)
        pricing_analyst = baker.make(User)
        sales_representative = baker.make(User)
        # request_information = baker.make(RequestInformation)
        request_status = baker.make(RequestStatus, request=request,
                                    pricing_analyst=pricing_analyst, sales_representative=sales_representative)
        request_approval = baker.make(RequestApproval, request=request, priority_increase_approved=None)
        request_status_type = baker.make(RequestStatusType)
        request_queue = baker.make(RequestQueue, request=request, is_secondary=True, request_status_type=request_status_type)


        self.assertEqual(Notification.objects.all().count(), 0)

        request_approval.priority_increase_approved = True
        request_approval.save()

        response = self.client.get(
            reverse('notification-list', kwargs={"user_id": sales_representative.user_id}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

        response = self.client.get(
            reverse('notification-list', kwargs={"user_id": pricing_analyst.user_id}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    @skip("RequestApproval Model Changed")
    def test_request_approval_deal_review_meeting_attachment(self):
        request = baker.make(Request, request_information__is_valid_data=True)
        pricing_analyst = baker.make(User)
        sales_representative = baker.make(User)
        request_status = baker.make(RequestStatus, request=request,
                                    pricing_analyst=pricing_analyst, sales_representative=sales_representative)
        request_approval = baker.make(
            RequestApproval, request=request, deal_review_meeting_attachment=None)

        self.assertEqual(Notification.objects.all().count(), 0)

        request_approval.deal_review_meeting_attachment = "file"
        request_approval.save()

        response = self.client.get(
            reverse('notification-list', kwargs={"user_id": sales_representative.user_id}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

        response = self.client.get(
            reverse('notification-list', kwargs={"user_id": pricing_analyst.user_id}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    @skip("RequestApproval Model Changed")
    def test_request_approval_pricing_committee_review_attachment(self):
        request = baker.make(Request, request_information__is_valid_data=True)
        pricing_analyst = baker.make(User)
        sales_representative = baker.make(User)
        request_status = baker.make(RequestStatus, request=request,
                                    pricing_analyst=pricing_analyst, sales_representative=sales_representative)
        request_approval = baker.make(
            RequestApproval, request=request, pricing_committee_review_attachment=None)

        self.assertEqual(Notification.objects.all().count(), 0)

        request_approval.pricing_committee_review_attachment = "file"
        request_approval.save()

        response = self.client.get(
            reverse('notification-list', kwargs={"user_id": sales_representative.user_id}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

        response = self.client.get(
            reverse('notification-list', kwargs={"user_id": pricing_analyst.user_id}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_request_queue_secondary_workflow_pending_pc_approval(self):
        pricing_analyst_persona = baker.make(
            Persona, persona_name="Pricing Analyst")
        sales_representative_persona = baker.make(
            Persona, persona_name="Sales Representative")
        sales_manager_persona = baker.make(
            Persona, persona_name="Sales Manager")
        pricing_analyst_user = baker.make(
            User, persona=pricing_analyst_persona)
        sales_manager_user = baker.make(User, persona=sales_manager_persona)
        sales_representative_user = baker.make(User, persona=sales_representative_persona, user_manager=sales_manager_user)
        # sales_representative_user_tree = baker.make(
        #     UserTree, user=sales_representative_user, sales_manager=sales_manager_user)
        primary_request_status_type = baker.make(
            RequestStatusType, request_status_type_name="Credit Approved")
        secondary_request_status_type = baker.make(RequestStatusType, request_status_type_name="Pending PC Approval", queue_personas=json.dumps(
            ["Pricing Analyst", "Sales Representative", "Sales Manager"]), is_secondary=True)
        request = baker.make(Request, request_information__is_valid_data=True,
            request_profile__is_valid_data=True,
            request_accessorials__is_valid_data=True,
            request_lane__is_valid_data=True,
            request_information__is_extended_payment=False,
            request_information__customer__account__account_name="ABC")
        request_status = baker.make(RequestStatus, request=request, request_status_type=primary_request_status_type,
                                    pricing_analyst=pricing_analyst_user, sales_representative=sales_representative_user)
        baker.make(RequestQueue, _quantity=5,
                   request_status_type=primary_request_status_type, completed_on=None)

        payload = {"next_request_status_type_id": secondary_request_status_type.pk,
                   "request_id": request.pk}

        response = self.client.post(
            reverse('workflow-post'), payload, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(RequestQueue.objects.filter(user=sales_manager_user).exists())
        self.assertTrue(RequestQueue.objects.filter(user=sales_representative_user).exists())
        self.assertTrue(RequestQueue.objects.filter(user=pricing_analyst_user).exists())
        self.assertEqual(Notification.objects.filter(user=sales_manager_user).count(), 1)
        self.assertEqual(RequestStatus.objects.filter(request_status_id=request_status.pk).first(
        ).request_status_type_id, primary_request_status_type.pk)
        self.assertEqual(RequestQueue.objects.filter(
            request_status_type=primary_request_status_type, completed_on__isnull=True).count(), 5)
        self.assertEqual(request_status.request_status_type, primary_request_status_type)

    def test_request_queue_primary_workflow_pending_cost_plus_approval(self):
        pricing_analyst_persona = baker.make(Persona, persona_name="Pricing Analyst")
        sales_representative_persona = baker.make(Persona, persona_name="Sales Representative")
        sales_manager_persona = baker.make(Persona, persona_name="Sales Manager")
        pricing_manager_persona = baker.make(Persona, persona_name="Pricing Manager")
        pricing_manager_user = baker.make(User, persona=pricing_manager_persona)
        pricing_analyst_user = baker.make(User, persona=pricing_analyst_persona, user_manager=pricing_manager_user)
        sales_manager_user = baker.make(User, persona=sales_manager_persona)
        sales_representative_user = baker.make(User, persona=sales_representative_persona, user_manager=sales_manager_user)
        # sales_representative_user_tree = baker.make(
        #     UserTree, user=sales_representative_user, sales_manager=sales_manager_user)
        # pricing_analyst_user_tree = baker.make(
        #     UserTree, user=pricing_analyst_user, user_manager=pricing_manager_user)
        current_request_status_type = baker.make(
            RequestStatusType, request_status_type_name="Credit Approved")
        next_request_status_type = baker.make(RequestStatusType, request_status_type_name="Pending Cost+ Approval", 
            assigned_persona="Sales Manager", queue_personas=json.dumps(
            ["Pricing Analyst", "Sales Representative", "Sales Manager", "Pricing Manager"]), is_secondary=False)
        request = baker.make(Request, request_information__is_valid_data=True,
            request_profile__is_valid_data=True,
            request_accessorials__is_valid_data=True,
            request_lane__is_valid_data=True,
            request_information__is_extended_payment=False,
            request_information__customer__service_level__service_level_name="ABC",
            request_information__customer__account__account_name="CDF")
        request_status = baker.make(RequestStatus, request=request, request_status_type=current_request_status_type,
                                    pricing_analyst=pricing_analyst_user, sales_representative=sales_representative_user)
        baker.make(RequestQueue, request=request, _quantity=5,
                   request_status_type=current_request_status_type, completed_on=None)

        payload = {"next_request_status_type_id": next_request_status_type.pk,
                   "current_request_status_type_id": current_request_status_type.pk, "request_id": request.pk}

        response = self.client.post(
            reverse('workflow-post'), payload, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(RequestQueue.objects.filter(
            user=sales_manager_user).exists())
        self.assertTrue(RequestQueue.objects.filter(
            user=pricing_manager_user).exists())
        self.assertTrue(RequestQueue.objects.filter(
            user=sales_representative_user).exists())
        self.assertTrue(RequestQueue.objects.filter(
            user=pricing_analyst_user).exists())
        self.assertEqual(Notification.objects.filter(
            user=sales_manager_user).count(), 1)
        self.assertEqual(RequestQueue.objects.filter(
            request_status_type=current_request_status_type, request=request, completed_on__isnull=True).count(), 0)

        request_status = RequestStatus.objects.filter(
            request_status_id=request_status.pk).first()
        self.assertEqual(request_status.current_editor, sales_manager_user)
        self.assertEqual(request_status.request_status_type,
                         next_request_status_type)

    def test_request_queue_primary_workflow_pricing_analyst_round_robin(self):
        service_level = baker.make(ServiceLevel)
        pricing_analyst_persona = baker.make(
            Persona, persona_name="Pricing Analyst")
        pricing_analyst_user = baker.make(
            User, persona=pricing_analyst_persona, can_process_requests=True)
        pricing_analyst_user_service_level = baker.make(
            UserServiceLevel, user=pricing_analyst_user, service_level=service_level)
        next_request_status_type = baker.make(RequestStatusType, request_status_type_name="Assign Pricing Analyst",
                                              assigned_persona="Pricing Analyst", queue_personas=json.dumps(["Pricing Analyst"]), is_secondary=False)
        next_next_request_status_type = baker.make(RequestStatusType, request_status_type_name="RRF With Pricing",
                                                   assigned_persona="Pricing Analyst", queue_personas=json.dumps(["Pricing Analyst"]), is_secondary=False)
        customer = baker.make(Customer, service_level=service_level)
        request_information = baker.make(RequestInformation, customer=customer, is_extended_payment=False)
        request = baker.make(Request, request_information=request_information)
        request_status = baker.make(RequestStatus, request=request,
                                    request_status_type=next_request_status_type, pricing_analyst=None)

        payload = {"next_request_status_type_id": next_request_status_type.pk,
                   "request_id": request.pk}

        response = self.client.post(
            reverse('workflow-post'), payload, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(RequestStatus.objects.filter(
            request_status_id=request_status.pk).first().pricing_analyst, pricing_analyst_user)

    def test_request_queue_primary_workflow_scs_pricing_analyst_round_robin(self):
        service_level = baker.make(ServiceLevel)
        pricing_analyst_persona = baker.make(
            Persona, persona_name="Pricing Analyst")
        pricing_analyst_user = baker.make(
            User, persona=pricing_analyst_persona, can_process_requests=True, can_process_scs=True)
        pricing_analyst_user_service_level = baker.make(
            UserServiceLevel, user=pricing_analyst_user, service_level=service_level)
        next_request_status_type = baker.make(RequestStatusType, request_status_type_name="Reassign to SCS",
                                              assigned_persona="Pricing Analyst", queue_personas=json.dumps(["Pricing Analyst"]), is_secondary=False)
        next_next_request_status_type = baker.make(RequestStatusType, request_status_type_name="RRF With Pricing",
                                                   assigned_persona="Pricing Analyst", queue_personas=json.dumps(["Pricing Analyst"]), is_secondary=False)
        # request_status_type_next = baker.make(RequestStatusType, request_status_type_name="Pending EPT Approval")
        customer = baker.make(Customer, service_level=service_level)
        request_information = baker.make(RequestInformation, customer=customer, is_extended_payment=False)
        request = baker.make(Request, request_information=request_information)
        request_status = baker.make(RequestStatus, request=request,
                                    request_status_type=next_request_status_type, pricing_analyst=None)

        request_queue = baker.make(RequestQueue, request=request, is_secondary=True, request_status_type=next_request_status_type)


        payload = {"next_request_status_type_id": next_request_status_type.pk,
                   "request_id": request.pk}

        response = self.client.post(
            reverse('workflow-post'), payload, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(RequestStatus.objects.filter(
            request_status_id=request_status.pk).first().pricing_analyst, pricing_analyst_user)

    def test_request_queue_secondary_workflow_initiate_pending(self):
        pricing_analyst_persona = baker.make(Persona, persona_name="Pricing Analyst")
        sales_representative_persona = baker.make(Persona, persona_name="Sales Representative")
        sales_manager_persona = baker.make(Persona, persona_name="Sales Manager")
        pricing_analyst_user = baker.make(User, persona=pricing_analyst_persona)
        sales_manager_user = baker.make(User, persona=sales_manager_persona)
        sales_representative_user = baker.make(User, persona=sales_representative_persona, user_manager=sales_manager_user)
        # sales_representative_user_tree = baker.make(
        #     UserTree, user=sales_representative_user, sales_manager=sales_manager_user)
        primary_request_status_type = baker.make(
            RequestStatusType, request_status_type_name="Credit Approved")
        secondary_request_status_type = baker.make(RequestStatusType, request_status_type_name="Pending PC Approval", queue_personas=json.dumps(
            ["Pricing Analyst", "Sales Representative", "Sales Manager"]), is_secondary=True)
        request = baker.make(Request, request_information__is_valid_data=True,
            request_profile__is_valid_data=True,
            request_accessorials__is_valid_data=True,
            request_lane__is_valid_data=True,
            request_information__is_extended_payment=False,
            request_information__customer__service_level__service_level_name="ABC",
            request_information__customer__account__account_name="CDF")
        request_status = baker.make(RequestStatus, request=request, request_status_type=primary_request_status_type,
                                    pricing_analyst=pricing_analyst_user, sales_representative=sales_representative_user)

        payload = {"secondary_pending_pc": True,
                   "request_id": request.pk}
        response = self.client.post(
            reverse('workflow-post'), payload, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertGreater(RequestQueue.objects.filter(
            request_status_type=secondary_request_status_type, request=request).count(), 0)

    def test_customer_account_synchronize(self):
        request_number = self.generate_request_number()
        account_number = random.randint(0, 999999)
        service_level = baker.make(ServiceLevel)
        customer = baker.make(
            Customer, service_level=service_level, city=None, account=None, phone=None)
        request_information = baker.make(
            RequestInformation, customer=customer, request_number=request_number)
        
        city = baker.make(City, city_name="Montreal")
        account = baker.make(Account, city=city,
                             account_number=account_number)

        response = self.client.put(
            reverse('customer-account-synchronize', kwargs={"account_number": account_number, "request_number": request_number}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Customer.objects.get(
            customer_id=customer.pk).city, Account.objects.get(account_id=account.pk).city)
        self.assertEqual(Customer.objects.get(
            customer_id=customer.pk).account, account)

        request_number = self.generate_request_number()
        account_number = random.randint(0, 999999)
        service_level = baker.make(ServiceLevel)
        account = baker.make(Account, phone="123456",
                             account_number=account_number)
        customer = baker.make(
            Customer, service_level=service_level, account=None, phone=None)
        customer_preexisting = baker.make(
            Customer, service_level=service_level, account=account)
        request_information = baker.make(
            RequestInformation, customer=customer, request_number=request_number)

        response = self.client.put(
            reverse('customer-account-synchronize', kwargs={"account_number": account_number, "request_number": request_number}))

        self.assertEqual(response.status_code, 400)

    def test_request_queue_primary_workflow_sales_coordinator(self):
        service_level = baker.make(ServiceLevel)
        sales_manager_persona = baker.make(Persona, persona_name="Sales Manager")
        sales_rep_persona = baker.make(Persona, persona_name="Sales Representative")
        sales_coordinator_persona = baker.make(Persona, persona_name="Sales Coordinator")
        sales_manager_user = baker.make(User, persona=sales_manager_persona)
        sales_rep_user = baker.make(User, persona=sales_rep_persona, can_process_requests=True, user_manager=sales_manager_user)
        sales_coordinator_users = baker.make(User, persona=sales_coordinator_persona, user_manager=sales_manager_user, _quantity=10)
        # sales_rep_user_tree = baker.make(
        #     UserTree, user_manager=sales_manager_user, user=sales_rep_user)
        # for sales_coordinator_user in sales_coordinator_users:
        #     baker.make(UserTree, user=sales_coordinator_user,
        #                user_manager=sales_manager_user)
        next_request_status_type = baker.make(RequestStatusType, request_status_type_name="RRF with Sales",
                                              assigned_persona="Sales Representative", queue_personas=json.dumps(["Sales Representative", "Sales Coordinator", "Sales Manager"]), is_secondary=False)
        
        request = baker.make(Request, request_information__is_valid_data=True,
            request_profile__is_valid_data=True,
            request_accessorials__is_valid_data=True,
            request_lane__is_valid_data=True,
            request_information__is_extended_payment=False,
            request_information__customer__account__account_name='ABC')
        request_status = baker.make(RequestStatus, request=request,
                                    request_status_type=next_request_status_type, sales_representative=sales_rep_user)

        payload = {"next_request_status_type_id": next_request_status_type.pk,
                   "request_id": request.pk}

        response = self.client.post(
            reverse('workflow-post'), payload, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(RequestQueue.objects.filter(
            request=request, completed_on__isnull=True, user_persona="Sales Coordinator").count(), 10)
