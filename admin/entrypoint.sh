#!/bin/sh

python manage.py migrate --noinput
python manage.py collectstatic --noinput

python manage.py createsuperuser --noinput || true

gunicorn --bind 0.0.0.0:8000 config.wsgi:application