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

python manage.py loaddata transactions/fixtures/account_types
python manage.py loaddata transactions/fixtures/error_levels
python manage.py loaddata transactions/fixtures/options
python manage.py loaddata transactions/fixtures/repeats
python manage.py loaddata transactions/fixtures/transaction_statuses
python manage.py loaddata transactions/fixtures/transaction_types
python manage.py loaddata transactions/fixtures/tag_types
python manage.py loaddata transactions/fixtures/banks
python manage.py loaddata transactions/fixtures/tags
python manage.py scheduletasks

gunicorn backend.wsgi:application --bind 0.0.0.0:8000
