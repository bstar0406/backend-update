from django.db import transaction
from django.contrib.auth import authenticate
from rest_framework import serializers
from core.models import Persona, User
from pac.rrf.models import UserServiceLevel
from pac.serializers import (ServiceLevelIdSerializer,
                             ServiceLevelNameSerializer)


class PersonaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Persona
        fields = ['persona_id', 'persona_name']


class UserManagerRetrieveSerializer(serializers.ModelSerializer):
    persona = PersonaSerializer(required=False)

    class Meta:
        model = User
        fields = ['user_id', 'user_name', 'persona']


class UserRetrieveSerializer(serializers.ModelSerializer):
    service_levels = serializers.SerializerMethodField()
    persona = PersonaSerializer(required=False)
    user_manager = UserManagerRetrieveSerializer(required=False)

    def get_service_levels(self, obj):
        service_levels = [
            user_service_level.service_level for user_service_level in obj.userservicelevel_set.all()]
        if service_levels:
            return ServiceLevelNameSerializer(service_levels, many=True).data

    class Meta:
        model = User
        fields = [field.name for field in User._meta.get_fields(
        )if field.concrete and field.name not in ['password', 'azure_id', 'azure_is_active']] + ['service_levels']


class UserUpdateSerializer(serializers.ModelSerializer):
    service_levels = ServiceLevelIdSerializer(many=True)
    # manager = serializers.IntegerField()

    @transaction.atomic
    def update(self, instance, validated_data):
        service_levels = validated_data.pop('service_levels', None)
        instance = super().update(instance, validated_data)

        if service_levels is not None:
            if service_levels:
                deleted_user_service_levels = UserServiceLevel.objects.filter(user=instance, is_active=True).exclude(
                    service_level_id__in=[service_level["service_level_id"] for service_level in service_levels])

                for deleted_user_service_level_instance in deleted_user_service_levels:
                    deleted_user_service_level_instance.is_active = False
                    deleted_user_service_level_instance.save()

                for service_level in service_levels:
                    user_service_level_instance, user_service_level_created = UserServiceLevel.objects.get_or_create(
                        service_level_id=service_level["service_level_id"], user=instance)
                    if not user_service_level_created and not user_service_level_instance.is_active:
                        user_service_level_instance.is_active = True
                        user_service_level_instance.save()
            else:
                deleted_user_service_levels = UserServiceLevel.objects.filter(
                    user=instance, is_active=True)
                for deleted_user_service_level_instance in deleted_user_service_levels:
                    deleted_user_service_level_instance.is_active = False
                    deleted_user_service_level_instance.save()

        return instance

    class Meta:
        model = User
        fields = ['persona', 'service_levels', 'user_manager',
                  'is_active', 'has_self_assign', 'is_away']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('user_email',"user_name")

class LoginSerializer(serializers.Serializer):
    user_email = serializers.CharField()
    user_name = serializers.CharField()
    def validate(self, data):
        user_email = data.get("user_email", "")
        user_name = data.get("user_name", "")

        if user_email and user_name:
            user = User.objects.get(user_email=user_email)
            if not user:
                msg = ('Unable to log in with provided credentials')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = ('Must include "user_email" which exists in database')
            raise serializers.ValidationError(msg, code='authorization')

        data['user'] = user
        return data