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
python manage.py loaddata transactions/fixtures/error_levels
python manage.py loaddata transactions/fixtures/options
python manage.py loaddata reminders/fixtures/repeats
python manage.py loaddata transactions/fixtures/transaction_statuses
python manage.py loaddata transactions/fixtures/transaction_types
python manage.py loaddata tags/fixtures/tag_types
python manage.py loaddata accounts/fixtures/banks
python manage.py loaddata tags/fixtures/tags
python manage.py scheduletasks
# test data load
python manage.py loaddata accounts/fixtures/my_banks
python manage.py loaddata accounts/fixtures/my_accounts
python manage.py loaddata tags/fixtures/my_tags

python manage.py runserver 0.0.0.0:8001
