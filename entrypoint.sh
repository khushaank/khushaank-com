#!/bin/sh
set -eu

python manage.py migrate --noinput

if [ -n "${DJANGO_SUPERUSER_USERNAME:-}" ] && [ -n "${DJANGO_SUPERUSER_EMAIL:-}" ] && [ -n "${DJANGO_SUPERUSER_PASSWORD:-}" ]; then
  python manage.py ensure_superuser
fi

exec gunicorn config.wsgi:application --bind "0.0.0.0:${PORT:-8000}" --workers "${GUNICORN_WORKERS:-3}"
