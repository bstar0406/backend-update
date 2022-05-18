from django.db import transaction
from django.db.models.query import QuerySet
from rest_framework import status
from rest_framework.response import Response

from pac.helpers.functions import (archive_instance, camel_to_snake,
                                   delete_instance, revert_instance,
                                   unarchive_instance)

# state 1 -> state 2 -> state 3
# active -> archived -> deleted
# True, True -> False, True -> False, False
# state 1 -> state 2 -> state 3
#       archive    delete
# state 1 -> state 3
#        delete
# state 2 -> state 1
#     unarchive


class ArchiveMixin:
    def archive(self, request):
        instance = self.get_object()
        archive_instance(instance)
        return Response(status=status.HTTP_200_OK)


class UnarchiveMixin:
    def unarchive(self, request):
        instance = self.get_object()
        unarchive_instance(instance)
        return Response(status=status.HTTP_200_OK)


class RevertVersionMixin:
    def revert_version(self, request, *args, **kwargs):
        instance = self.get_object()
        history_instance = self.queryset_history.filter(**kwargs).first()
        if not history_instance:
            return Response("History instance not found, check version number.", status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer_class()

        serializer_data = revert_instance(
            instance, history_instance, serializer)

        return Response(serializer_data, status=status.HTTP_200_OK)


class RetrieveHistoryMixin:
    def retrieve_history(self, request, *args, **kwargs):
        queryset = self.get_queryset().filter(
            **{self.lookup_field: self.kwargs[self.lookup_field]})
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class RetrieveHistoryVersionMixin:
    def retrieve_history_version(self, reques, *args, **kwargs):
        history_instance = self.get_queryset().filter(**kwargs).first()
        if not history_instance:
            return Response("History instance not found, check version number.", status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(history_instance)
        return Response(serializer.data)


class BulkCreateMixin:
    def bulk_create(self, request, bulk_create_method):
        serializer = self.get_serializer(data=request.data, many=True)
        if serializer.is_valid():
            try:
                bulk_create_method(serializer.validated_data)
            except Exception as e:
                return Response(str(e), status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetQuerySetMixin:
    def get_queryset(self):
        assert self.queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method."
            % self.__class__.__name__
        )
        queryset = self.queryset

        if self.action in ["retrieve_history", "retrieve_history_version"]:
            assert self.queryset_history is not None, (
                "'%s' should either include a `queryset_history` attribute, "
                "or override the `get_queryset()` method."
                % self.__class__.__name__
            )
            queryset = self.queryset_history

        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()

        action_filter_kwargs = {"unarchive": {
            "is_active": False, "is_inactive_viewable": True}, "retrieve_history": {}, "retrieve_history_version": {}}
        if self.action in action_filter_kwargs:
            return queryset.filter(**action_filter_kwargs[self.action])
        return queryset.filter(is_inactive_viewable=True)


class GetSerializerClassMixin:
    def get_serializer_class(self):
        if self.action in ["retrieve_history", "retrieve_history_version"]:
            return self.serializer_class_history
        assert self.serializer_class is not None, (
            "'%s' should either include a `serializer_class` attribute, "
            "or override the `get_serializer_class()` method."
            % self.__class__.__name__
        )
        return self.serializer_class


class BatchUpdateMixin:
    @transaction.atomic
    def batch_update(self, request, *args, **kwargs):
        for obj in request.data:
            obj_id = obj.get(self.lookup_field, None)
            if not obj_id:
                return Response(f"Missing primary key: {self.lookup_field}", status=status.HTTP_400_BAD_REQUEST)
            instance = self.get_queryset().filter(
                **{self.lookup_field: obj_id}).first()
            if not instance:
                return Response(f"Object with primary key '{obj_id}' does not exist", status=status.HTTP_400_BAD_REQUEST)
            serializer = self.get_serializer(
                instance, data=obj, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return Response({"status": "Success"}, status=status.HTTP_200_OK)


class BatchCreateUpdateMixin:
    def batch_create_update(self, request, *args, **kwargs):
        for obj in request.data:
            obj_id = obj.get(self.lookup_field)
            if not obj_id:
                serializer = self.get_serializer(data=obj)
            else:
                instance = self.get_queryset().filter(
                    **{self.lookup_field: obj_id}).first()
                if not instance:
                    return Response(f"Object with primary key '{obj_id} does not exist", status=status.HTTP_400_BAD_REQUEST)
                serializer = self.get_serializer(
                    instance, data=obj, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return Response({"status": "Success"}, status=status.HTTP_200_OK)


class BatchDeleteMixin:
    def batch_delete(self, request, *args, **kwargs):
        for obj in request.data:
            obj_id = obj.get(self.lookup_field, None)
            if not obj_id:
                return Response(f"Missing primary key: {self.lookup_field}", status=status.HTTP_400_BAD_REQUEST)
            instance = self.get_queryset().filter(
                **{self.lookup_field: obj_id}).first()
            if not instance:
                return Response(f"Object with primary key '{obj_id}' does not exist or has already been deleted", status=status.HTTP_400_BAD_REQUEST)
            delete_instance(instance)
        return Response({"status": "Success"}, status=status.HTTP_200_OK)
