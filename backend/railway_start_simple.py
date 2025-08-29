#!/usr/bin/env python
"""
Simple Railway startup script for TASTY FINGERS
Uses main settings with environment overrides
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
    os.environ['ALLOWED_HOSTS'] = 'tasty-fingers.up.railway.app,localhost,127.0.0.1,0.0.0.0'
    os.environ['CORS_ALLOWED_ORIGINS'] = 'https://tasty-fingers.up.railway.app,http://localhost:3000'
    
    print("✅ Environment variables set")

def run_commands():
    """Run all necessary commands"""
    print("🗄️ Running database migrations...")
    os.system("python manage.py migrate")
    
    print("📦 Collecting static files...")
    os.system("python manage.py collectstatic --noinput")
    
    print("🎯 Adding sample data...")
    os.system("python manage.py add_sample_data")

def start_server():
    """Start the Gunicorn server"""
    print("🌐 Starting Gunicorn server...")
    print("✅ Server should now be running without 301 redirects!")
    print("📍 Access your application at: https://tasty-fingers.up.railway.app")
    print("🔧 Admin panel at: https://tasty-fingers.up.railway.app/admin")
    print("📊 API endpoints at: https://tasty-fingers.up.railway.app/api/")
    
    # Start Gunicorn with simple configuration
    os.system("gunicorn backend.wsgi --bind 0.0.0.0:3000 --workers 1 --timeout 120 --log-level info")

if __name__ == '__main__':
    print("🚀 Starting TASTY FINGERS on Railway (Simple Mode)...")
    print("=" * 60)
    
    setup_environment()
    run_commands()
    start_server()
