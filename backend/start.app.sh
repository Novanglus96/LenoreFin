#!/bin/bash

python manage.py makemigrations --no-input
python manage.py migrate --no-input
python manage.py collectstatic --no-input

if [ "$DJANGO_SUPERUSER_USERNAME" ]; then
    (python manage.py createsuperuser \
        --noinput \
        --username "$DJANGO_SUPERUSER_USERNAME" \
        --email "$DJANGO_SUPERUSER_EMAIL") || true
    python manage.py assign_superuser_group
fi

python manage.py loaddata accounts/fixtures/account_types
python manage.py loaddata reminders/fixtures/repeats
python manage.py loaddata transactions/fixtures/transaction_statuses
python manage.py loaddata transactions/fixtures/transaction_types
python manage.py loaddata tags/fixtures/tag_types
python manage.py loaddata accounts/fixtures/banks
python manage.py loaddata tags/fixtures/maintags
python manage.py loaddata tags/fixtures/subtags
python manage.py loaddata tags/fixtures/tags
python manage.py loaddata administration/fixtures/graph_types
python manage.py scheduletasks
python manage.py load_version_fixture
python manage.py load_options
python manage.py load_backup_config
python manage.py load_caches

# Inject runtime env vars for the Vue frontend
cat <<EOF > /usr/share/nginx/html/config.js
window.__APP_CONFIG__ = {
  VITE_API_KEY: "${VITE_API_KEY}",
  VITE_OPT_FEATURES: "${VITE_OPT_FEATURES:-false}"
};
EOF

exec /usr/bin/supervisord -n -c /etc/supervisor/conf.d/supervisord.conf
