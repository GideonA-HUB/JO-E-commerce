#!/usr/bin/env python
"""
Debug server script with enhanced logging for redirect issues
"""
import os
import sys
import django
from django.core.management import execute_from_command_line
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

def setup_debug_logging():
    """Setup enhanced logging for debugging"""
    import logging
    
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Enable Django debug logging
    django_logger = logging.getLogger('django')
    django_logger.setLevel(logging.DEBUG)
    
    # Enable middleware logging
    middleware_logger = logging.getLogger('django.middleware')
    middleware_logger.setLevel(logging.DEBUG)

def print_server_info():
    """Print server configuration information"""
    print("🚀 Starting Django Debug Server")
    print("=" * 50)
    print(f"DEBUG: {settings.DEBUG}")
    print(f"SECURE_SSL_REDIRECT: {getattr(settings, 'SECURE_SSL_REDIRECT', 'Not set')}")
    print(f"APPEND_SLASH: {getattr(settings, 'APPEND_SLASH', 'Not set')}")
    print(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
    print(f"STATIC_URL: {settings.STATIC_URL}")
    print(f"STATIC_ROOT: {settings.STATIC_ROOT}")
    print("=" * 50)

if __name__ == '__main__':
    setup_debug_logging()
    print_server_info()
    
    # Run the development server with debug output
    sys.argv = ['manage.py', 'runserver', '0.0.0.0:3000', '--verbosity=2']
    execute_from_command_line(sys.argv)
