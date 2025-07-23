from django.urls import path
from .views import login_view, logout_view, dashboard_view, staff_management_view, register_view, staff_register_view, staff_login_view

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('staff-management/', staff_management_view, name='staff_management'),
    path('register/', register_view, name='register'),
    path('staff-register/', staff_register_view, name='staff_register'),
    path('staff-login/', staff_login_view, name='staff_login'),
] 