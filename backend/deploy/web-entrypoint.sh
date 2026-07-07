#!/bin/sh
# Container start command for hosts without a pre-deploy hook (e.g. Render free
# tier, where Pre-Deploy Command is paid-only): apply migrations and ensure the
# bootstrap admin before serving. Both steps are idempotent, so re-running on
# every cold start is safe.
set -e

uv run python manage.py migrate --noinput
uv run python manage.py create_admin
exec uv run python manage.py runserver 0.0.0.0:8000
