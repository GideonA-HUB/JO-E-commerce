#!/usr/bin/env python
import os
import sys
import django

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from accounts.models import UserProfile

print("=== Owner Accounts ===")
owners = UserProfile.objects.filter(role='owner')
if owners.exists():
    for up in owners:
        print(f"Email: {up.user.email}")
        print(f"User ID: {up.user.id}")
        print(f"Role: {up.role}")
        print("---")
else:
    print("No owner accounts found.")

print("\n=== Staff Accounts ===")
staff = UserProfile.objects.filter(role='staff')
if staff.exists():
    for up in staff:
        print(f"Email: {up.user.email}")
        print(f"User ID: {up.user.id}")
        print(f"Role: {up.role}")
        print("---")
else:
    print("No staff accounts found.")

print("\n=== All Users ===")
all_users = UserProfile.objects.all()
if all_users.exists():
    for up in all_users:
        print(f"Email: {up.user.email}")
        print(f"User ID: {up.user.id}")
        print(f"Role: {up.role}")
        print("---")
else:
    print("No users found.") 