#!/bin/bash

python manage.py makemigrations --no-input
python manage.py migrate --no-input
python manage.py collectstatic --no-input
#python manage.py createcachetable

if [ "$DJANGO_SUPERUSER_USERNAME" ]; then
    (python manage.py createsuperuser \
        --noinput \
        --username $DJANGO_SUPERUSER_USERNAME \
        --email $DJANGO_SUPERUSER_EMAIL) ||
        true
fi

python manage.py loaddata account_types
python manage.py loaddata error_levels
python manage.py loaddata options
python manage.py loaddata repeats
python manage.py loaddata transaction_statuses
python manage.py loaddata transaction_types
python manage.py populate_calendar
python manage.py loaddata calendar_fixture
python manage.py loaddata tag_types
python manage.py loaddata banks

gunicorn backend.wsgi:application --bind 0.0.0.0:8000
