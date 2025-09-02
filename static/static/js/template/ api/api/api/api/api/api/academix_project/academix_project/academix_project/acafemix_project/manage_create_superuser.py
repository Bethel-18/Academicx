# safe script to auto-create superuser if ADMIN_USERNAME and ADMIN_PASSWORD env vars set
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'academix_project.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

username = os.environ.get('ADMIN_USERNAME')
password = os.environ.get('ADMIN_PASSWORD')
email = os.environ.get('ADMIN_EMAIL', '')

if username and password:
    if not User.objects.filter(username=username).exists():
        print("Creating superuser", username)
        User.objects.create_superuser(username=username, email=email, password=password)
    else:
        print("Superuser already exists:", username)
else:
    print("ADMIN_USERNAME or ADMIN_PASSWORD not set — skipping superuser creation")
