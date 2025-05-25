#!/bin/sh

echo "running migrations"
sleep 2
export DJANGO_SETTINGS_MODULE=RendezVous.settings.prod
python manage.py makemigrations
python manage.py migrate
echo "loading data..."
find / -name doctors.json 2>/dev/null
sleep 2
cat /app/tests/doctors.json
python manage.py loaddata /app/tests/app/doctors.json
python manage.py collectstatic --noinput
gunicorn RendezVous.wsgi --bind 0.0.0.0:8000 --workers=5