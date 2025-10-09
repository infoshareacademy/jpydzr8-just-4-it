#!/usr/bin/env bash
set -e

cd /app

# Migrations
python manage.py migrate --noinput

# Create superuser if env provided
if [ -n "$SUPERUSER_EMAIL" ] && [ -n "$SUPERUSER_PASSWORD" ]; then
python - <<'PY'
import os
from django.core.management import execute_from_command_line
os.environ.setdefault('DJANGO_SETTINGS_MODULE','coworking.settings')
import django
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
email = os.environ['SUPERUSER_EMAIL']
pwd = os.environ['SUPERUSER_PASSWORD']
full = os.environ.get('SUPERUSER_FULL_NAME','Admin')
u, created = User.objects.get_or_create(email=email, defaults={'full_name': full, 'is_staff': True, 'is_superuser': True})
if created or not u.has_usable_password():
    u.set_password(pwd)
    u.is_staff = True
    u.is_superuser = True
    u.save()
print("Superuser ready:", email)
PY
fi

# Collect static (noop for now)
python manage.py collectstatic --noinput || true

# Run server (gunicorn if available else Django)
python - <<'PY' || true
import importlib.util, sys, os, subprocess
spec = importlib.util.find_spec('gunicorn')
if spec is None:
    sys.exit(1)
subprocess.run(['gunicorn','coworking.wsgi:application','--bind','0.0.0.0:8000','--workers','3'])
PY

# fallback to runserver
python manage.py runserver 0.0.0.0:8000
