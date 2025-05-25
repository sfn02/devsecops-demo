#!/bin/sh

echo "Hello from entrypont"
export DJANGO_SETTINGS_MODULE=RendezVous.settings.prod
python manage.py makemigrations
python manage.py migrate
echo "loading data..."
cat doctors.json
python manage.py loaddata doctors.json
python manage.py collectstatic --noinput
gunicorn RendezVous.wsgi --bind 0.0.0.0:8000 --workers=5