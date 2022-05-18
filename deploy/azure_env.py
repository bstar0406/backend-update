#! /usr/bin/env python3
import os
import subprocess
import sys


REQUIRED_ENV_VARS = (
    'AZURE_GROUP',
    'AZURE_LOCATION',
    'APP_SERVICE_APP_NAME',
    'AZURE_MSSQL_USERNAME',
    'AZURE_MSSQL_DB_NAME',
    'AZURE_MSSQL_PASSWORD',
    'AZURE_MSSQL_HOST',
    'AZURE_MSSQL_PORT',
    'RATEWARE_USERNAME',
    'RATEWARE_PASSWORD',
    'RATEWARE_LICENSE_KEY'
)


def verify_environment():
    missing = []
    for v in REQUIRED_ENV_VARS:
        if v not in os.environ:
            missing.append(v)
    if missing:
        print("Required Environment Variables Unset:")
        print("\t" + "\n\t".join(missing))
        print("Exiting.")
        exit()


verify_environment()

SETTINGS_KEYS = (
    'AZURE_GROUP',
    'AZURE_LOCATION',
    'APP_SERVICE_APP_NAME',
    'AZURE_MSSQL_USERNAME',
    'AZURE_MSSQL_DB_NAME',
    'AZURE_MSSQL_PASSWORD',
    'AZURE_MSSQL_HOST',
    'AZURE_MSSQL_PORT',
    'DJANGO_SETTINGS_MODULE',
    'RATEWARE_USERNAME',
    'RATEWARE_PASSWORD',
    'RATEWARE_LICENSE_KEY'
)
settings_pairs = ['{}={}'.format(k, os.getenv(k)) for k in SETTINGS_KEYS]

# https://docs.microsoft.com/en-us/cli/azure/webapp/config/appsettings?view=azure-cli-latest#az-webapp-config-appsettings-set
settings_command = [
    'az', 'webapp', 'config', 'appsettings', 'set',
    '--name', os.getenv('APP_SERVICE_APP_NAME'),
    '--resource-group', os.getenv('AZURE_GROUP'),
    '--settings',
] + settings_pairs


update_settings = input('Update App Settings? [y/n]: ')
if update_settings == 'y':
    sys.stdout.write("Updating App Settings... ")
    sys.stdout.flush()
    subprocess.check_output(settings_command)
    print("Done")
