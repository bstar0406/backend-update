from pac.settings.settings import *

DATABASES = {
    'default': {
        'ENGINE': 'sql_server.pyodbc',
        'NAME': os.getenv('AZURE_UAT_MSSQL_DB_NAME'),
        'USER': os.getenv('AZURE_UAT_MSSQL_USERNAME'),
        'PASSWORD': os.getenv('AZURE_UAT_MSSQL_PASSWORD'),
        'HOST': os.getenv('AZURE_UAT_MSSQL_HOST'),
        'PORT': os.getenv('AZURE_UAT_MSSQL_PORT'),

        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
            'extra_params': 'Trusted_Connection=No'
        },
    },
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'core.authentication.AzureActiveDirectoryAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
        # 'core.permissions.IsAuthorized',
    ],
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema'
}

# DEBUG = False
