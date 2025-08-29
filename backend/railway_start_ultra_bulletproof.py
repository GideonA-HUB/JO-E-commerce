#!/usr/bin/env python
"""
Ultra Bulletproof Railway startup script for TASTY FINGERS
Uses direct commands to avoid ALL configuration issues
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
    
    # Set CSRF trusted origins
    os.environ['CSRF_TRUSTED_ORIGINS'] = 'https://tasty-fingers.up.railway.app,http://localhost:3000,http://127.0.0.1:8000'
    
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
    """Start the Gunicorn server with ultra bulletproof configuration"""
    print("🌐 Starting ultra bulletproof Gunicorn server...")
    print("✅ Ultra bulletproof configuration:")
    print("   - Direct command execution")
    print("   - No config files")
    print("   - Minimal parameters only")
    print("   - Railway optimized")
    print("📍 Access your application at: https://tasty-fingers.up.railway.app")
    print("🔧 Admin panel at: https://tasty-fingers.up.railway.app/admin")
    print("📊 API endpoints at: https://tasty-fingers.up.railway.app/api/")
    
    # Ultra bulletproof Gunicorn command - direct execution, no config files
    cmd = "gunicorn backend.wsgi:application --bind 0.0.0.0:$PORT --workers 1 --timeout 120"
    print(f"Running: {cmd}")
    
    # Execute the command directly
    exit_code = os.system(cmd)
    
    if exit_code != 0:
        print(f"❌ Gunicorn failed with exit code: {exit_code}")
        sys.exit(1)

if __name__ == '__main__':
    print("🚀 Starting TASTY FINGERS on Railway (Ultra Bulletproof Mode)...")
    print("=" * 60)
    
    setup_environment()
    run_commands()
    start_server()
