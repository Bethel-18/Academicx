#!/usr/bin/env bash
set -e

# install python deps (Render also runs this if you put it in Build Command)
pip install -r requirements.txt

# run migrations (DB must be accessible before this step)
python manage.py migrate --noinput

# create a superuser automatically from env vars (script below)
python manage_create_superuser.py || true

# collect static files for production
python manage.py collectstatic --noinput
