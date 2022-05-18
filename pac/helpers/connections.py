import importlib
import os

import pyodbc


def pyodbc_connection():
    env = os.getenv("DJANGO_SETTINGS_MODULE")
    if not env:
        from pac.settings.settings import DATABASES
    else:
        DATABASES = importlib.import_module(env).DATABASES

    try:
        cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=' +
                              DATABASES["default"]["HOST"] + ';DATABASE=' + DATABASES["default"]["NAME"] + ';UID=' + DATABASES["default"]["USER"] + ';PWD=' + DATABASES["default"]["PASSWORD"])
    except Exception as e:
        raise e
    return cnxn
