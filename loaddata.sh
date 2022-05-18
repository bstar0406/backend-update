#!/bin/bash
set -x

# Load fixtures
python manage.py loaddata pac/fixtures/*.json

gunicorn --bind=0.0.0.0 --timeout 600 pac.wsgi