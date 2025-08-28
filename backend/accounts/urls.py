from django.urls import path
from .views import (
    login_view, logout_view, dashboard_view, staff_management_view, 
    register_view, staff_register_view, staff_login_view,
    order_management, update_order_status, subscriber_management,
    newsletter_management, create_newsletter_campaign, send_newsletter_campaign
)

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('staff-management/', staff_management_view, name='staff_management'),
    path('register/', register_view, name='register'),
    path('staff-register/', staff_register_view, name='staff_register'),
    path('staff-login/', staff_login_view, name='staff_login'),
    
    # Order Management
    path('order-management/', order_management, name='order_management'),
    path('update-order-status/<int:order_id>/', update_order_status, name='update_order_status'),
    
    # Subscriber Management
    path('subscriber-management/', subscriber_management, name='subscriber_management'),
    
    # Newsletter Management
    path('newsletter-management/', newsletter_management, name='newsletter_management'),
    path('create-newsletter-campaign/', create_newsletter_campaign, name='create_newsletter_campaign'),
    path('send-newsletter-campaign/<int:campaign_id>/', send_newsletter_campaign, name='send_newsletter_campaign'),
] 