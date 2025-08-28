#!/usr/bin/env python
import os
import django
from django.conf import settings

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

# Test database connection
from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        print("✅ Database connection successful!")
except Exception as e:
    print(f"❌ Database connection failed: {e}")

# Test Django setup
try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
    print("✅ Django setup successful!")
except Exception as e:
    print(f"❌ Django setup failed: {e}")
