import os
import sys
from pathlib import Path
import django

# Ensure project root is on PYTHONPATH so `food_bridge` package is importable
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'food_bridge.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
username = 'foodbridge'
email = 'wasilph12@gmail.com'
password = 'qwerty123456'

try:
    user = User.objects.get(username=username)
    user.email = email
    user.is_staff = True
    user.is_superuser = True
    user.is_active = True
    user.set_password(password)
    user.save()
    print('UPDATED', user.username, user.email, user.is_superuser)
except User.DoesNotExist:
    user = User.objects.create_superuser(username, email, password)
    print('CREATED', user.username, user.email, user.is_superuser)
