from django.db import migrations, connection
from pac.helpers.migrations import partition_script
import os

def load_data_from_sql(apps, schema_editor):
    folder = os.path.join(os.path.dirname(__file__), '0005_Stored_Procedures')
    print('')
    print(f'Loading Folder: {folder}')
    for filename in os.listdir(folder):
        print(f'Migrating Stored Procedures: {filename}')
        with open(os.path.join(folder, filename), 'r', encoding='utf-8-sig') as f:
            with connection.cursor() as c:
                for part in partition_script(f.read()):
                    c.execute(part)

class Migration(migrations.Migration):

    dependencies = [
        ('pac', '0004_functions'),
    ]

    operations = [
        migrations.RunPython(load_data_from_sql),
    ]
