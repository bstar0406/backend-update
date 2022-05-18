# Generated by Django 2.1.13 on 2020-12-22 21:11

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('rrf', '0020_auto_20201217_0452'),
    ]

    operations = [
        migrations.AddField(
            model_name='request',
            name='request_owner',
            field=models.ForeignKey(db_column='RequestOwner', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
    ]
