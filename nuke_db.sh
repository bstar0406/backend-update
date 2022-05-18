#!/bin/bash
set -x

# Remove migrations
#rm -rf pac/migrations/* pac/pre_costing/migrations/* pac/rrf/migrations/* auth/migrations/*

# Make migrations
python manage.py makemigrations core pac pre_costing rrf 
python manage.py migrate