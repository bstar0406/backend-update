# Generated by Django 2.1.13 on 2022-04-07 16:04

from django.db import migrations


# Method to insert values in ServiceType required for PAC 2429
def add_service_types(apps, schema_editor):
    servicetype = apps.get_model('rrf', 'ServiceType')

    field_names = ('is_active', 'is_inactive_viewable', 'service_class', 'service_type_name', 'service_type_description')

    new_service_type_data = [
        (1, 1, 'Direct', 'CARTAGE', 'Direct Cartage'),
        (1, 1, 'Direct', 'DIRECT', 'Direct'),
        (1, 1, 'Indirect', 'EMBARGO', 'Temporary Embargo Zone'),
        (1, 1, 'Indirect', 'INDIRECT', 'Indirect'),
        (1, 1, 'Indirect', 'NOSERVICE', 'No Service Zone'),
        (1, 1, 'Indirect', 'QUOTERQD', 'Requires Quote'),
        (1, 1, 'Direct', 'TEST', 'Test Service Type'),
    ]

    service_types = [servicetype(**dict(zip(field_names, d))) for d in new_service_type_data]

    # insert data
    servicetype.objects.bulk_create(service_types)


class Migration(migrations.Migration):
    dependencies = [
        ('rrf', '0035_auto_20220407_1245'),
    ]

    operations = [
        migrations.RunPython(add_service_types)
    ]