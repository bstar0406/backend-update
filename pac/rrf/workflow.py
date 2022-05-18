import json

from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response

from core.models import User
from pac.email import send_email
from pac.models import Notification
from pac.rrf.models import (LastAssignedUser, RequestEditorRight, RequestQueue,
                            RequestStatusType, UserServiceLevel)
from pac.rrf.serializers import LastAssignedUserSerializer
from pac.rrf.service_bus import queue_pricing_engine


class WorkflowManager():
    def __init__(
            self, request, request_status, current_request_status_type=None, next_request_status_type=None,
            pricing_engine_rating_filters=None):
        self.current_request_status_type = current_request_status_type
        self.next_request_status_type = next_request_status_type
        self.request_status = request_status
        self.request = request
        self.request_status_kwargs = {}
        self.pricing_engine_rating_filters = pricing_engine_rating_filters
        self.request_status_type_system_calculators = {"RRF Submitted": self._rrf_submitted_system_calculator,
                                                       "Assign Credit Analyst": self._assign_credit_analyst_system_calculator,
                                                       "Credit Approved": self._credit_approved_system_calculator,
                                                       "Cost+ Approved": self._cost_plus_approved_system_calculator,
                                                       "Assign Pricing Analyst": self._assign_pricing_analyst_system_calculator,
                                                       "Reassign to SCS": self._reassign_to_scs_system_calculator,
                                                       #    "With Pricing Engine": self._with_pricing_engine_system_calculator,
                                                       #    "Partner Approved": self._partner_approved_system_calculator,
                                                       "Submitted to Publish": self._submitted_to_publish_system_calculator,
                                                       #    "Pending Publish": self._pending_publish_system_calculator,
                                                       #    "Published Successfully", self._published_succesfully_system_calculator
                                                       "Publishing Failed": self._publishing_failed_system_calculator,
                                                       "RRF Reactivated": self._rrf_reactivated_system_calculator,
                                                       "Speed Sheet Reactivated": self._speed_sheet_reactivated_system_calculator
                                                       }
        self.request_status_type_triggers = {"PC Approved": self._pc_approved_trigger,
                                             "EPT Declined": self._ept_declined_trigger,
                                             "With Pricing Engine": self._with_pricing_engine_trigger,
                                             "RRF Archived": self._rrf_archived_trigger,
                                             "Speed Sheet Archived": self.speed_sheet_archived_trigger
                                             }

        self.request_status_email_trigger = {
            'Pending Credit Approval',
            'Pending EPT Approval',
            'Cost+ Declined',
            'Credit Declined',
            'Pending Sales Approval',
            'Pending Cost+ Approval',
            'Pending DRM Approval',
            'Pending PC Approval',
            'Pending PCR Approval',
            'Pending GRI Customer Response'
        }

    def close_request_queue(self):
        if not self.current_request_status_type:
            raise Exception("Current RequestStatusType not found.")
        current_time = timezone.now()
        for request_queue_instance in RequestQueue.objects.filter(request=self.request,
                                                                  request_status_type=self.current_request_status_type,
                                                                  completed_on__isnull=True, is_active=True):
            request_queue_instance.completed_on = current_time
            request_queue_instance.save()

    def generate_request_queue(self, current_editor=None):
        if not self.next_request_status_type:
            raise Exception("Next RequestStatusType not found.")

        user_mapping = {"Sales Representative": self._find_sales_representative,
                        "Pricing Analyst": self._find_pricing_analyst,
                        "Pricing Manager": self._find_pricing_manager,
                        "Sales Manager": self._find_sales_manager,
                        "Credit Analyst": self._find_credit_analyst,
                        "Credit Manager": self._find_credit_manager,
                        "Partner Carrier": self._find_partner_carrier,
                        "Sales Coordinator": self._find_sales_coordinator,
                        "Account Owner": self._find_account_owner}

        personas = [persona for persona in json.loads(self.next_request_status_type.queue_personas)]
        request_status_type_is_secondary = self.next_request_status_type.is_secondary
        assigned_persona = self.next_request_status_type.assigned_persona
        current_time = timezone.now()

        actionable_users = []

        for persona in personas:
            users = user_mapping.get(persona)()

            if not users:
                continue

            if not isinstance(users, list):
                users = [users]

            for user in users:
                if request_status_type_is_secondary is False:
                    if not current_editor and assigned_persona == persona:
                        self.request_status_kwargs["current_editor"] = user

                is_actionable = False
                if assigned_persona == persona:
                    is_actionable = True
                    actionable_users.append(user)

                # This is to fix the fact that when EPT has been already approved it keeps sending pending EPT approval to Credit Manager when Sales Rep re-submits request
                # if RequestQueue.objects.filter(Request = self.Request, request_status_type = "EPT Approved") and self.next_request_status_type = "Pending EPT Approval"
                # continue

                RequestQueue.objects.create(
                    request=self.request,
                    user=user,
                    user_persona=persona if persona != "Account Owner" else user.persona.persona_name,
                    request_status_type=self.next_request_status_type,
                    is_secondary=request_status_type_is_secondary,
                    is_final=self.next_request_status_type.is_final,
                    is_actionable=is_actionable,
                    assigned_on=current_time,
                    completed_on=current_time if self.next_request_status_type.is_final else None)

        if request_status_type_is_secondary is False:
            self.request_status_kwargs["request_status_type"] = self.next_request_status_type

            if current_editor:
                self.request_status_kwargs["current_editor"] = current_editor
            elif self.next_request_status_type.editor == "System Calculator":
                self.request_status_kwargs["current_editor"] = None

        if self.request_status_kwargs:
            for k, v in self.request_status_kwargs.items():
                setattr(self.request_status, k, v)
            self.request_status.save()

        if self.next_request_status_type.request_status_type_name in self.request_status_type_system_calculators:
            new_next_request_status_type = self.request_status_type_system_calculators[
                self.next_request_status_type.request_status_type_name]()
            new_workflow_manager = WorkflowManager(request_status=self.request_status, request=self.request,
                                                   current_request_status_type=self.next_request_status_type,
                                                   next_request_status_type=new_next_request_status_type)
            new_workflow_manager.close_request_queue()
            new_workflow_manager.generate_request_queue()
        if self.next_request_status_type.request_status_type_name in self.request_status_type_triggers:
            self.request_status_type_triggers[self.next_request_status_type.request_status_type_name]()

        # Send emails
        if self.next_request_status_type.request_status_type_name in self.request_status_email_trigger:
            send_email.send_email_workflow(self.next_request_status_type.request_status_type_name, actionable_users)

        return actionable_users

    def _find_sales_representative(self):
        self.sales_representative = getattr(
            self, "sales_representative", self.request_status.sales_representative)
        if not self.sales_representative:
            raise Exception("Sales Representative does not exist.")
        return self.sales_representative

    def _find_pricing_analyst(self):
        self.pricing_analyst = getattr(self, "pricing_analyst", None)

        if self.next_request_status_type.request_status_type_name == "Reassign to SCS":
            self.pricing_analyst = assign_round_robin_user(
                self.request, "Pricing Analyst", **{"can_process_requests": True, "can_process_scs": True})
            if not self.pricing_analyst:
                raise Exception(
                    f"{self.next_request_status_type.request_status_type_name} status Pricing Analyst round-robin assignment failed.")

        if not self.pricing_analyst:
            self.pricing_analyst = self.request_status.pricing_analyst

        if not self.pricing_analyst and self.next_request_status_type.request_status_type_name == "Assign Pricing Analyst":
            self.pricing_analyst = assign_round_robin_user(
                self.request, "Pricing Analyst", **{"can_process_requests": True})
            if not self.pricing_analyst:
                raise Exception(
                    f"{self.next_request_status_type.request_status_type_name} status Pricing Analyst round-robin assignment failed.")

        self.request_status_kwargs["pricing_analyst"] = self.pricing_analyst
        return self.pricing_analyst

    def _find_pricing_manager(self):
        self.pricing_manager = getattr(self, "pricing_manager", None)
        if not self.pricing_manager:
            self.pricing_analyst = getattr(
                self, "pricing_analyst", self._find_pricing_analyst())
            if not self.pricing_analyst:
                return None
            elif self.pricing_analyst.persona.persona_name == "Pricing Manager":
                self.pricing_manager = self.pricing_analyst
            else:
                self.pricing_manager = self.pricing_analyst.user_manager
                if not self.pricing_manager:
                    raise Exception(
                        "Pricing Manager does not exist and Pricing Analyst does not have Pricing Manager persona.")
        return self.pricing_manager

    def _find_credit_manager(self):
        self.credit_manager = getattr(self, "credit_manager", None)

        if not self.credit_manager:
            self.credit_analyst = getattr(
                self, "credit_analyst", self._find_credit_analyst())
            if self.credit_analyst.persona.persona_name == "Credit Manager":
                self.credit_manager = self.credit_analyst
            else:
                self.credit_manager = self.credit_analyst.user_manager

        if not self.credit_manager:
            raise Exception(
                "Credit Manager does not exist and Credit Analyst does not have Credit Manager rights.")
        return self.credit_manager

    def _find_sales_manager(self):
        self.sales_manager = getattr(self, "sales_manager", None)
        if not self.sales_manager:
            self.sales_representative = getattr(
                self, "sales_representative", self._find_sales_representative())
            sales_representative_persona = self.sales_representative.persona.persona_name
            if self.sales_representative and not sales_representative_persona.startswith("Sales"):
                return
            self.sales_manager = self.sales_representative.user_manager
            if not self.sales_manager:
                if sales_representative_persona == "Sales Manager":
                    self.sales_manager = self.sales_representative
                else:
                    raise Exception(
                        "Sales Manager does not exist and Sales Representative does not have Sales Manager nor Sales Coordinator persona.")
        return self.sales_manager

    def _find_credit_analyst(self):
        self.credit_analyst = getattr(
            self, "credit_analyst", self.request_status.credit_analyst)

        if not self.credit_analyst:
            assignment_kwargs = {"Assign Credit Analyst": {
                "can_process_requests": True}, "Pending EPT Approval": {"can_process_requests": True}}
            if self.next_request_status_type.request_status_type_name in assignment_kwargs:
                self.credit_analyst = assign_round_robin_user(
                    self.request, "Credit Analyst",
                    **assignment_kwargs[self.next_request_status_type.request_status_type_name])
                if not self.credit_analyst:
                    raise Exception(
                        f"{self.next_request_status_type.request_status_type_name} status Credit Analyst round-robin assignment failed.")
                self.request_status_kwargs["credit_analyst"] = self.credit_analyst
            else:
                raise Exception("Credit Analyst does not exist.")

        return self.credit_analyst

    def _find_partner_carrier(self):
        # talk to ish about logic
        # still need to determine logic.
        self.partner_carrier = getattr(self, "partner_carrier", "")
        self.partner_carrier = list(User.objects.filter(persona__persona_name="Partner Carrier"))

        if not self.partner_carrier:
            raise Exception("Partner Carrier does not exist.")
        return self.partner_carrier

    def _find_sales_coordinator(self):
        self.sales_representative = getattr(self, "sales_representative", self._find_sales_representative())
        sales_representative_persona = self.sales_representative.persona.persona_name
        if sales_representative_persona.startswith("Pricing"):
            self.sales_coordinator = None
        elif sales_representative_persona == "Sales Manager":
            self.sales_coordinator = list(User.objects.filter(
                user_manager=self.sales_representative, persona__persona_name="Sales Coordinator"))
        elif sales_representative_persona in ["Sales Representative", "Sales Coordinator"]:
            self.sales_coordinator = list(User.objects.filter(
                user_manager=self.sales_representative.user_manager, persona__persona_name="Sales Coordinator"))
        return self.sales_coordinator

    def _find_account_owner(self):
        account = self.request.request_information.customer.account
        if not account or not getattr(account, "account_owner", None):
            return
        return account.account_owner

    def _rrf_submitted_system_calculator(self):
        if not self.request.request_information.customer.account:
            return RequestStatusType.objects.filter(request_status_type_name="Assign Credit Analyst").first()
        elif self.request.request_information.request_type.request_type_name == "Cost+" and not RequestQueue.objects.filter(
                request=self.request, request_status_type__request_status_type_name="Cost+ Approved", is_active=True,
                completed_on__isnull=False).exists():
            if not self.sales_manager:
                return RequestStatusType.objects.filter(request_status_type_name="Cost+ Approved").first()
            return RequestStatusType.objects.filter(request_status_type_name="Pending Cost+ Approval").first()
        else:
            return RequestStatusType.objects.filter(request_status_type_name="Assign Pricing Analyst").first()

    def _assign_credit_analyst_system_calculator(self):
        return RequestStatusType.objects.filter(request_status_type_name="Pending Credit Approval").first()

    def _credit_approved_system_calculator(self):
        if self.request.request_information.request_type.request_type_name == "Cost+" and not RequestQueue.objects.filter(
                request=self.request, request_status_type__request_status_type_name="Cost+ Approved", is_active=True,
                completed_on__isnull=False).exists():
            return RequestStatusType.objects.filter(request_status_type_name="Pending Cost+ Approval").first()
        else:
            return RequestStatusType.objects.filter(request_status_type_name="Assign Pricing Analyst").first()

    def _cost_plus_approved_system_calculator(self):
        return RequestStatusType.objects.filter(request_status_type_name="Assign Pricing Analyst").first()

    def _assign_pricing_analyst_system_calculator(self):
        return RequestStatusType.objects.filter(request_status_type_name="RRF with Pricing").first()

    def _reassign_to_scs_system_calculator(self):
        return RequestStatusType.objects.filter(request_status_type_name="RRF with Pricing").first()

    # def _with_pricing_engine_system_calculator(self):
    #     return RequestStatusType.objects.filter(request_status_type_name="In Analysis").first()
    #
    # def _partner_approved_system_calculator(self):
    #     return RequestStatusType.objects.filter(request_status_type_name="In Analysis").first()

    def _submitted_to_publish_system_calculator(self):
        return RequestStatusType.objects.filter(request_status_type_name="Pending Publish").first()

    def _publishing_failed_system_calculator(self):
        return RequestStatusType.objects.filter(request_status_type_name="In Analysis").first()

    def _rrf_reactivated_system_calculator(self):
        self.request.is_active = True
        self.request.save()
        # PAC-706 request here RequestQueue table to find latest status before archiving and reactivating, excluding statuse
        # 31 and 34, ordered descending by date
        exclude_list = ['21','31', '34', '33']
        request_queue = RequestQueue.objects \
            .filter(request__request_id=self.request.request_id) \
            .exclude(request_status_type__request_status_type_id__in=exclude_list) \
            .order_by('-assigned_on') \
            .first()
        if not request_queue:
            return RequestStatusType.objects.filter(request_status_type_name="RRF Initiated").first()

        return request_queue.request_status_type


    def _speed_sheet_reactivated_system_calculator(self):
        self.request.is_active = True
        self.request.save()
        return RequestStatusType.objects.filter(request_status_type_name="Speed Sheet Active").first()

    def _pc_approved_trigger(self):
        request_information = self.request.request_information
        request_information.priority = 1
        request_information.save()
        self.request.save()

    def _ept_declined_trigger(self):
        request_information = self.request.request_information
        request_information.is_extended_payment = False
        request_information.save()
        self.request.save()

    def _with_pricing_engine_trigger(self):
        print('Sending message to Pricing Engine')
        if queue_pricing_engine(
                self.request.request_id,
                self.current_request_status_type.request_status_type_id,
                self.pricing_engine_rating_filters):
            print('Message sent successfully')
            pass
        # return RequestStatusType.objects.filter(request_status_type_name="With Pricing Engine").first()
        else:
            print('Message send failed')
            pass
            # TODO: Add error on MQ Message not being sent
            # Return to previous status
            # return self.current_request_status_type

    def _rrf_archived_trigger(self):
        print('RRF Archived Trigger')

        # import pdb
        # pdb.set_trace()

        self.request.is_active = False
        self.request.save()

        # import pdb
        # pdb.set_trace()

    def speed_sheet_archived_trigger(self):
        self.request.is_active = False
        self.request.save()


def assign_round_robin_user(request_instance, persona_name, **kwargs):
    service_level_id = request_instance.request_information.customer.service_level.service_level_id

    candidate_users_instances = []

    if persona_name == "Credit Analyst":
        candidate_users_instances = User.objects.filter(
            persona__persona_name=persona_name, **kwargs).order_by('user_id')
    else:
        candidate_users_instances = User.objects.filter(persona__persona_name=persona_name, **kwargs,
                                                        user_id__in=UserServiceLevel.objects.filter(
                                                            service_level_id=service_level_id, is_active=True,
                                                            is_inactive_viewable=True).values_list(
                                                            'user__user_id')).order_by('user_id')

    if not candidate_users_instances:
        raise Exception('Cannot find users of persona {0} to be assigned service level {1}'.format(
            persona_name, service_level_id))

    last_assigned_user_instance = LastAssignedUser.objects.filter(
        persona_name=persona_name, service_level_id=service_level_id).first()

    if not last_assigned_user_instance:
        user = candidate_users_instances.first()
        serializer = LastAssignedUserSerializer(
            data={"persona_name": persona_name, "service_level": service_level_id, "user": user.pk})
    else:
        user = candidate_users_instances.first()

        if len(candidate_users_instances) > 1:
            last_assigned_user_id = last_assigned_user_instance.user_id
            short_listed_user_instance = candidate_users_instances.filter(
                user_id__gt=last_assigned_user_id).order_by('user_id').first()

            if not short_listed_user_instance:
                short_listed_user_instance = candidate_users_instances.exclude(
                    user_id=last_assigned_user_id).order_by('user_id').first()

            user = short_listed_user_instance
        serializer = LastAssignedUserSerializer(last_assigned_user_instance, data={
            "user": user.pk}, partial=True)

    serializer.is_valid(raise_exception=True)
    serializer.save()

    return user


def request_editor_right_update(action, request_status_instance, new_current_editor_instance):
    old_current_editor_instance = request_status_instance.current_editor
    current_time = timezone.now()

    if action == "Decline":
        Notification.objects.create(
            user=new_current_editor_instance,
            message=f"{old_current_editor_instance.user_name} has declined Editor Rights transfer of RRF {request_status_instance.request.request_code}")
        request_editor_right_instance = RequestEditorRight.objects.filter(
            user=new_current_editor_instance, request=request_status_instance.request, is_active=True).first()
        request_editor_right_instance.is_active = False
        request_editor_right_instance.notification.is_active = False
        request_editor_right_instance.save()
        request_editor_right_instance.notification.save()
        return Response({"status": "Success"}, status=status.HTTP_201_CREATED)

    notification_instance = Notification(
        user=new_current_editor_instance,
        message=f"Your request for Editor Rights for Request No. {request_status_instance.request.request_code} for {request_status_instance.request.request_information.customer.customer_name} have been approved")

    # This logic approved by Ish Habib, for speedsheets, since there is no request_type for speedsheets
    request_type = request_status_instance.request.request_information.request_type
    request_type_name = (None if request_type is None else request_type.request_type_name)

    if request_type_name == "Cost+" and not RequestQueue.objects.filter(
            request=request_status_instance.request, request_status_type__request_status_type_name="Cost+ Approved",
            completed_on__isnull=False).exists():
        workflow_manager = WorkflowManager(request=request_status_instance.request,
                                           request_status=request_status_instance,
                                           current_request_status_type=request_status_instance.request_status_type,
                                           next_request_status_type=RequestStatusType.objects.filter(
                                               request_status_type_name="Pending Cost+ Approval").first())
        workflow_manager.close_request_queue()
        workflow_manager.generate_request_queue()
        notification_instance.message += " but you cannot receive this request since the system has moved it to Cost+"
    elif new_current_editor_instance.persona.persona_name.startswith(
            "Sales") and request_status_instance.request_status_type.request_status_type_name != "RRF with Sales":
        workflow_manager = WorkflowManager(request=request_status_instance.request,
                                           request_status=request_status_instance,
                                           current_request_status_type=request_status_instance.request_status_type,
                                           next_request_status_type=RequestStatusType.objects.filter(
                                               request_status_type_name="RRF with Sales").first())
        workflow_manager.close_request_queue()
        workflow_manager.generate_request_queue(
            current_editor=new_current_editor_instance)
    elif new_current_editor_instance.persona.persona_name.startswith(
            "Pricing") and request_status_instance.request_status_type.request_status_type_name != "RRF with Pricing":
        workflow_manager = WorkflowManager(request=request_status_instance.request,
                                           request_status=request_status_instance,
                                           current_request_status_type=request_status_instance.request_status_type,
                                           next_request_status_type=RequestStatusType.objects.filter(
                                               request_status_type_name="RRF with Pricing").first())
        workflow_manager.close_request_queue()
        workflow_manager.generate_request_queue(
            current_editor=new_current_editor_instance)
    else:
        request_status_instance.current_editor = new_current_editor_instance
        request_status_instance.save()

    for request_editor_right_instance in RequestEditorRight.objects.filter(request=request_status_instance.request,
                                                                           is_active=True).select_related(
        'notification'):
        request_editor_right_instance.is_active = False
        request_editor_right_instance.notification.is_active = False
        request_editor_right_instance.save()
        request_editor_right_instance.notification.save()
        if request_editor_right_instance.user != new_current_editor_instance:
            Notification.objects.create(
                user=request_editor_right_instance.user,
                message=f"{old_current_editor_instance} has declined Editor Rights transfer of RRF {request_status_instance.request.request_code}")

    notification_instance.save()

    return Response({"status": "Success"}, status=status.HTTP_201_CREATED)
