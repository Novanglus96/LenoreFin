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

python manage.py loaddata accounts/fixtures/account_types
python manage.py loaddata administration/fixtures/error_levels
python manage.py loaddata reminders/fixtures/repeats
python manage.py loaddata transactions/fixtures/transaction_statuses
python manage.py loaddata transactions/fixtures/transaction_types
python manage.py loaddata tags/fixtures/tag_types
python manage.py loaddata accounts/fixtures/banks
python manage.py loaddata tags/fixtures/maintags
python manage.py loaddata tags/fixtures/subtags
python manage.py loaddata tags/fixtures/tags
python manage.py scheduletasks
python manage.py load_version_fixture
python manage.py loaddata administration/fixtures/graph_types
python manage.py load_options

gunicorn backend.wsgi:application --bind 0.0.0.0:8000
