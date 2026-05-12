#!/bin/bash

mkdir -p /backups

python manage.py makemigrations --no-input
python manage.py migrate --no-input
python manage.py qcluster
