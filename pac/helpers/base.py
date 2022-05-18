"""
This script provides extended functionality to Django's base Models by adding
reused fields for tracking changes.
"""
from django.db import models
from django.utils import timezone


class Update(models.Model):
    version_num = models.IntegerField(
        null=False, default=1, db_column="VersionNum")
    is_latest_version = models.BooleanField(
        null=False, default=True, db_column="IsLatestVersion")
    updated_on = models.DateTimeField(
        auto_now_add=True, null=False, db_column="UpdatedOn")
    updated_by = models.CharField(
        max_length=50, null=False, default="", db_column="UpdatedBy")
    base_version = models.IntegerField(
        null=True, default=None, db_column="BaseVersion")

    class Meta:
        abstract = True


class CommentUpdate(Update):
    comments = models.CharField(
        max_length=4000, null=False, default="", db_column="Comments")

    class Meta:
        abstract = True


class Delete(models.Model):
    is_active = models.BooleanField(
        null=False, default=True, db_column="IsActive")
    is_inactive_viewable = models.BooleanField(
        null=False, default=True, db_column="IsInactiveViewable")

    class Meta:
        abstract = True


class CommentUpdateDelete(CommentUpdate):
    is_active = models.BooleanField(
        null=False, default=True, db_column="IsActive")
    is_inactive_viewable = models.BooleanField(
        null=False, default=True, db_column="IsInactiveViewable")

    class Meta:
        abstract = True
