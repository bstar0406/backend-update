import json

from rest_framework import serializers

from pac.models import Notification, ServiceLevel, Comment, CommentReply, Account


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"


class NotificationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["is_read", "is_inactive_viewable", "is_active"]


class ServiceLevelNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceLevel
        fields = ['service_level_id', 'service_level_name']


class ServiceLevelIdSerializer(serializers.Serializer):
    service_level_id = serializers.IntegerField(required=True)


# class EntityFileSerializer(serializers.ModelSerializer):
#     def create(self, validated_data):
#         return EntityFile.objects.all
#         # return EntityFile.objects.create(**validated_data)
#
#     def update(self, instance, validated_data):
#         return instance
#
#     class Meta:
#         model = EntityFile
#         fields = ['id', 'entity', 'file_url', 'status', 'created_on', 'created_by', 'comment']


class CommentReplySerializer(serializers.ModelSerializer):
    attachments = serializers.SerializerMethodField()
    comment = serializers.SerializerMethodField
    created_by = serializers.CharField

    def get_attachments(self, obj):
        return json.loads(str(obj.attachments))

    def create(self, validated_data):
        validated_data['created_by'] = self.context.get("username")
        validated_data['attachments'] = self.context.get("attachments")
        return CommentReply.objects.create(**validated_data)

    def update(self, instance, validated_data):
        return instance

    class Meta:
        model = CommentReply
        fields = ['id', 'content', 'created_on', 'created_by', 'comment', 'attachments']


class CommentSerializer(serializers.ModelSerializer):
    # replies = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    replies = CommentReplySerializer(many=True, read_only=True)
    attachments = serializers.SerializerMethodField()
    file_field = serializers.FileField(required=False)
    entity_uuid = serializers.SerializerMethodField()
    created_by = serializers.CharField

    # files = EntityFileSerializer(many=True, read_only=True)
    def get_attachments(self, obj):
        attachments_dict = json.loads(obj.attachments)

        # Remove AzureBlob key data
        for attachment in attachments_dict:
            attachment.pop('container', None)
            attachment.pop('blob', None)

        return attachments_dict

    def get_entity_uuid(self, obj):
        return obj.entity_uuid

    def create(self, validated_data, *args, **kwargs):
        validated_data['created_by'] = self.context.get("username")
        validated_data['entity_uuid'] = self.context.get("entity_uuid")
        validated_data['attachments'] = self.context.get("attachments")
        return Comment.objects.create(**validated_data)

    def update(self, instance, validated_data):
        if self.context.get("attachments") is not None:
            validated_data['attachments'] = json.dumps(self.context.get("attachments"))
        return super().update(instance, validated_data)

    class Meta:
        model = Comment
        fields = "__all__"


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = "__all__"
