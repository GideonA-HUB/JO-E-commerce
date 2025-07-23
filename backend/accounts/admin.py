from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import UserProfile

# Only allow superusers (owner) to access admin
class OwnerOnlyAdminSite(admin.AdminSite):
    def has_permission(self, request):
        return request.user.is_active and request.user.is_superuser

admin_site = OwnerOnlyAdminSite(name='owneradmin')

# Register User and UserProfile for owner only
admin_site.register(User, UserAdmin)
admin_site.register(UserProfile)
