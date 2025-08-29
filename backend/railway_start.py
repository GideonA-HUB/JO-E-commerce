#!/usr/bin/env python
"""
Railway startup script for TASTY FINGERS
Handles deployment environment and prevents 301 redirects
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

# Set Django settings module for Railway
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.railway_settings')

def setup_environment():
    """Setup Railway environment variables"""
    print("🚀 Setting up Railway environment...")
    
    # Set environment variables if not already set
    if not os.environ.get('DEBUG'):
        os.environ['DEBUG'] = 'False'
    
    if not os.environ.get('SECURE_SSL_REDIRECT'):
        os.environ['SECURE_SSL_REDIRECT'] = 'False'
    
    if not os.environ.get('CORS_ALLOW_ALL_ORIGINS'):
        os.environ['CORS_ALLOW_ALL_ORIGINS'] = 'False'
    
    print("✅ Environment variables set")

def run_migrations():
    """Run database migrations"""
    print("🗄️ Running database migrations...")
    try:
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Migrations completed successfully")
    except Exception as e:
        print(f"❌ Migration error: {e}")
        sys.exit(1)

def collect_static():
    """Collect static files"""
    print("📦 Collecting static files...")
    try:
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
        print("✅ Static files collected successfully")
    except Exception as e:
        print(f"❌ Static collection error: {e}")
        sys.exit(1)

def add_sample_data():
    """Add sample data if needed"""
    print("🎯 Adding sample data...")
    try:
        execute_from_command_line(['manage.py', 'add_sample_data'])
        print("✅ Sample data added successfully")
    except Exception as e:
        print(f"⚠️ Sample data error (continuing): {e}")

def start_server():
    """Start the Gunicorn server"""
    print("🌐 Starting Gunicorn server...")
    print("✅ Server should now be running without 301 redirects!")
    print("📍 Access your application at: https://tasty-fingers.up.railway.app")
    print("🔧 Admin panel at: https://tasty-fingers.up.railway.app/admin")
    print("📊 API endpoints at: https://tasty-fingers.up.railway.app/api/")
    
    # Start Gunicorn with Railway configuration
    os.system("gunicorn backend.wsgi --config railway_gunicorn.conf.py")

if __name__ == '__main__':
    print("🚀 Starting TASTY FINGERS on Railway...")
    print("=" * 60)
    
    setup_environment()
    run_migrations()
    collect_static()
    add_sample_data()
    start_server()
