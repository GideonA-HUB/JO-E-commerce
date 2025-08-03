"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.conf import settings
from api.models import SiteSettings

@csrf_exempt
def api_root(request):
    """Welcome page for the API"""
    return JsonResponse({
        'message': 'Welcome to TASTY FINGERS API',
        'endpoints': {
            'products': '/api/products/',
            'orders': '/api/orders/',
            'admin': '/admin/',
        },
        'status': 'running'
    })

def main_site(request):
    """Serve the main website"""
    context = {}
    if request.user.is_authenticated:
        context['user'] = request.user
    
    # Get site settings from database
    try:
        site_settings = SiteSettings.get_settings()
        context['site_settings'] = site_settings
    except:
        # Fallback to default values if no settings exist
        context['site_settings'] = None
    
    # Add Paystack public key to context
    context['paystack_public_key'] = settings.PAYSTACK_PUBLIC_KEY
    
    return render(request, 'main_site.html', context)

urlpatterns = [
    path('', main_site, name='main_site'),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('accounts/', include('accounts.urls')),
]
