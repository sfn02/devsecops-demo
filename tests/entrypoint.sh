#!/bin/sh


python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput

gunicorn RendezVous.wsgi --bind 0.0.0.0:8000 --workers=5