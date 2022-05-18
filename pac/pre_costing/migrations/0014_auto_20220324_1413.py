# Generated by Django 2.1.13 on 2022-03-24 18:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pac', '0010_auto_20210520_2039'),
        ('pre_costing', '0011_auto_20210517_2127'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='brokercontractcosthistory',
            name='service_level_version',
        ),
        migrations.RemoveField(
            model_name='lanehistory',
            name='service_level_version',
        ),
        migrations.AlterIndexTogether(
            name='brokercontractcost',
            index_together=set(),
        ),
        migrations.RemoveField(
            model_name='lane',
            name='service_level',
        ),
        migrations.AlterIndexTogether(
            name='lane',
            index_together={('origin_terminal', 'destination_terminal')},
        ),
        migrations.RemoveField(
            model_name='brokercontractcost',
            name='service_level',
        ),
    ]
