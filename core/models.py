from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from django.db.models import Q
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from core.managers import UserManager
from pac.helpers.base import CommentUpdateDelete, Delete


class Persona(Delete):
    persona_id = models.BigAutoField(
        primary_key=True, null=False, db_column="PersonaID")
    persona_name = models.CharField(
        max_length=50, null=False, blank=False, db_column="PersonaName")

    def __str__(self):
        return str(self.persona_id)

    class Meta:
        db_table = 'Persona'


class PersonaHistory(CommentUpdateDelete):
    persona_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="PersonaVersionID")
    persona = models.ForeignKey(
        Persona, on_delete=models.CASCADE, null=False, db_column="PersonaID")
    persona_name = models.CharField(
        max_length=50, null=False, blank=False, db_column="PersonaName")

    def __str__(self):
        return str(self.persona_version_id)

    class Meta:
        db_table = 'Persona_History'


class User(AbstractBaseUser, Delete):
    user_id = models.BigAutoField(
        primary_key=True, null=False, db_column="UserID")
    user_name = models.CharField(
        max_length=50, null=False, blank=False, db_column="UserName")
    user_email = models.CharField(
        max_length=50, unique=True, null=False, blank=False, db_column="UserEmail")
    azure_is_active = models.BooleanField(
        default=True, null=False, db_column="AzureIsActive")
    is_away = models.BooleanField(
        default=False, null=False, db_column="IsAway")
    has_self_assign = models.BooleanField(
        default=False, null=False, db_column="HasSelfAssign")
    can_process_scs = models.BooleanField(
        default=False, null=False, db_column="CanProcessSCS")
    can_process_requests = models.BooleanField(
        default=False, null=False, db_column="CanProcessRequests")
    can_process_reviews = models.BooleanField(
        default=False, null=False, db_column="CanProcessReviews")
    azure_id = models.CharField(
        max_length=36, null=True, blank=False, db_column="AzureID")
    persona = models.ForeignKey(
        Persona, on_delete=models.CASCADE, null=True, db_column="PersonaID")
    user_manager = models.ForeignKey(
        "User", on_delete=models.CASCADE, null=True, db_column="UserManagerID")

    def __str__(self):
        return str(self.user_id)

    objects = UserManager()

    EMAIL_FIELD = 'user_email'
    USERNAME_FIELD = 'user_email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        db_table = 'User'


class UserHistory(AbstractBaseUser, CommentUpdateDelete):
    user_version_id = models.BigAutoField(
        primary_key=True, null=False, db_column="UserVersionID")
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=False, db_column="UserID")
    user_name = models.CharField(
        max_length=50, null=False, blank=False, db_column="UserName")
    user_email = models.CharField(
        max_length=50, null=False, blank=False, db_column="UserEmail")
    azure_id = models.CharField(
        max_length=36, null=True, blank=False, db_column="AzureID")
    azure_is_active = models.BooleanField(
        default=True, null=False, db_column="AzureIsActive")
    is_away = models.BooleanField(
        default=False, null=False, db_column="IsAway")
    has_self_assign = models.BooleanField(
        default=False, null=False, db_column="HasSelfAssign")
    can_process_scs = models.BooleanField(
        default=False, null=False, db_column="CanProcessSCS")
    can_process_requests = models.BooleanField(
        default=False, null=False, db_column="CanProcessRequests")
    can_process_reviews = models.BooleanField(
        default=False, null=False, db_column="CanProcessReviews")
    persona_version = models.ForeignKey(
        PersonaHistory, on_delete=models.CASCADE, null=True, db_column="PersonaVersionID")
    user_manager_version = models.ForeignKey(
        "UserHistory", on_delete=models.CASCADE, null=True, db_column="UserManagerVersionID")

    def __str__(self):
        return str(self.user_version_id)

    class Meta:
        db_table = 'User_History'


@receiver(models.signals.post_save, sender=User)
@receiver(models.signals.post_save, sender=Persona)
def post_save_instance(sender, instance, created, **kwargs):
    from pac.helpers.functions import create_instance_history
    create_instance_history(sender, instance, globals())
