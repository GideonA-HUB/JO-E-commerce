#!/usr/bin/env python
"""
Clean Railway startup script for TASTY FINGERS
No external config files - everything inline to avoid issues
"""
import os
import sys

def setup_environment():
    """Setup Railway environment variables"""
    print("🚀 Setting up Railway environment...")
    
    # Critical environment variables for Railway
    os.environ['DEBUG'] = 'False'
    os.environ['SECURE_SSL_REDIRECT'] = 'False'
    os.environ['CORS_ALLOW_ALL_ORIGINS'] = 'False'
    
    # Ensure Railway domain is in allowed hosts
    current_hosts = os.environ.get('ALLOWED_HOSTS', '')
    if 'tasty-fingers.up.railway.app' not in current_hosts:
        if current_hosts:
            os.environ['ALLOWED_HOSTS'] = f"{current_hosts},tasty-fingers.up.railway.app"
        else:
            os.environ['ALLOWED_HOSTS'] = 'tasty-fingers.up.railway.app,localhost,127.0.0.1,0.0.0.0'
    
    # Ensure CORS includes Railway domain
    current_cors = os.environ.get('CORS_ALLOWED_ORIGINS', '')
    if 'https://tasty-fingers.up.railway.app' not in current_cors:
        if current_cors:
            os.environ['CORS_ALLOWED_ORIGINS'] = f"{current_cors},https://tasty-fingers.up.railway.app"
        else:
            os.environ['CORS_ALLOWED_ORIGINS'] = 'https://tasty-fingers.up.railway.app,http://localhost:3000'
    
    print("✅ Environment variables set")

def run_commands():
    """Run all necessary commands"""
    print("🗄️ Running database migrations...")
    result = os.system("python manage.py migrate")
    if result != 0:
        print("⚠️ Migration warning (continuing anyway)")
    
    print("📦 Collecting static files...")
    result = os.system("python manage.py collectstatic --noinput")
    if result != 0:
        print("⚠️ Static collection warning (continuing anyway)")
    
    print("🎯 Adding sample data...")
    result = os.system("python manage.py add_sample_data")
    if result != 0:
        print("⚠️ Sample data warning (continuing anyway)")

def start_server():
    """Start the Gunicorn server with clean configuration"""
    print("🌐 Starting Gunicorn server...")
    print("✅ Server should now be running without 301 redirects!")
    print("📍 Access your application at: https://tasty-fingers.up.railway.app")
    print("🔧 Admin panel at: https://tasty-fingers.up.railway.app/admin")
    print("📊 API endpoints at: https://tasty-fingers.up.railway.app/api/")
    
    # Start Gunicorn with clean, minimal configuration
    cmd = "gunicorn backend.wsgi --bind 0.0.0.0:3000 --workers 1 --timeout 120 --log-level info"
    print(f"Running: {cmd}")
    os.system(cmd)

if __name__ == '__main__':
    print("🚀 Starting TASTY FINGERS on Railway (Clean Mode)...")
    print("=" * 60)
    
    setup_environment()
    run_commands()
    start_server()
