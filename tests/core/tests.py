import json
import random

from django.test import TestCase
from django.urls import reverse
from model_bakery import baker
from rest_framework.test import APIClient, APITestCase

from core.models import Persona, User
from pac.models import ServiceLevel
from pac.rrf.models import UserServiceLevel


class PreCostingMockTest(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.request_number_set = set()

    def test_user_list(self):
        user_persona = baker.make(Persona, persona_name="Sales Representative")
        user_manager_persona = baker.make(
            Persona, persona_name="Sales Manager")
        user_manager = baker.make(User, persona=None)
        user = baker.make(User, persona=user_persona,
                          user_manager=user_manager)
        # user_tree = baker.make(UserTree, user=user, user_manager=user_manager)
        # user_manager_tree = baker.make(UserTree, user=user_manager)
        service_level = baker.make(ServiceLevel)
        user_service_level = baker.make(
            UserServiceLevel, service_level=service_level, user=user)

        response = self.client.get(reverse('user-list'))

        self.assertEqual(response.status_code, 200)

    def test_user_update(self):
        user = baker.make(User)
        service_level_1 = baker.make(ServiceLevel)
        service_level_2 = baker.make(ServiceLevel)
        service_level_3 = baker.make(ServiceLevel)
        user_service_level_1 = baker.make(
            UserServiceLevel, user=user, service_level=service_level_1)
        user_service_level_2 = baker.make(
            UserServiceLevel, user=user, service_level=service_level_2, is_active=False)

        payload = {"service_levels": [{"service_level_id": service_level_2.pk}, {
            "service_level_id": service_level_3.pk}]}

        response = self.client.patch(reverse(
            'user-update', kwargs={"user_id": user.pk}), payload, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertFalse(UserServiceLevel.objects.get(
            pk=user_service_level_1.pk).is_active)
        self.assertTrue(UserServiceLevel.objects.get(
            pk=user_service_level_2.pk).is_active)
        self.assertTrue(UserServiceLevel.objects.filter(
            user=user, service_level=service_level_3, is_active=True).exists())

        user = baker.make(User)
        service_level_1 = baker.make(ServiceLevel)
        service_level_2 = baker.make(ServiceLevel)
        service_level_3 = baker.make(ServiceLevel)
        user_service_level_1 = baker.make(
            UserServiceLevel, user=user, service_level=service_level_1)
        user_service_level_2 = baker.make(
            UserServiceLevel, user=user, service_level=service_level_2)
        user_service_level_3 = baker.make(
            UserServiceLevel, user=user, service_level=service_level_3)

        payload = {"service_levels": []}

        response = self.client.patch(
            reverse('user-update', kwargs={"user_id": user.pk}), payload, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(UserServiceLevel.objects.filter(
            user=user, is_active=True).count(), 0)
        self.assertEqual(UserServiceLevel.objects.filter(
            user=user, is_active=False).count(), 3)

    def test_user_header(self):
        persona = baker.make(Persona)
        is_active_count = random.randint(1, 30)
        is_inactive_count = random.randint(1, 30)
        is_new_count = random.randint(1, 30)
        users_active = baker.make(
            User, is_active=True, _quantity=is_active_count, persona=persona)
        users_inactive = baker.make(
            User, is_active=False, _quantity=is_inactive_count, persona=persona)
        users_new = baker.make(User, is_active=True,
                               _quantity=is_new_count, persona=None)

        response = self.client.get(reverse('user-header'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data['total_users'], is_active_count + is_inactive_count + is_new_count)
        self.assertEqual(response.data['new_users'], is_new_count)
        self.assertEqual(
            response.data['active_users'], is_active_count + is_new_count)
        self.assertEqual(response.data['inactive_users'], is_inactive_count)
