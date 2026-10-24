#!/usr/bin/env bash
set -euo pipefail
# Safe for the initial single-instance deployment to a new Neon database.
python manage.py migrate --no-input
exec gunicorn SEBMS.wsgi:application --bind "0.0.0.0:${PORT:-8000}" --workers 2 --timeout 120 --access-logfile -
