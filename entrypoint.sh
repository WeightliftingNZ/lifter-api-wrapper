#!/bin/bash
pipenv run python manage.py makemigrations --no-input
pipenv run python manage.py migrate
pipenv run python manage.py collectstatic --no-input

pipenv run gunicorn config.wsgi:application --workers 1 --bind 0.0.0.0:8000 --log-level debug
