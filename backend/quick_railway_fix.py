#!/usr/bin/env python
"""
Quick fix for Railway 301 redirect issues
Run this script to immediately fix the deployment
"""
import os
import sys

def print_header():
    print("🚀 QUICK RAILWAY FIX FOR 301 REDIRECTS")
    print("=" * 50)

def check_environment():
    """Check current environment variables"""
    print("🔍 Checking environment variables...")
    
    critical_vars = [
        'DEBUG',
        'SECURE_SSL_REDIRECT', 
        'ALLOWED_HOSTS',
        'CORS_ALLOWED_ORIGINS',
        'DATABASE_URL'
    ]
    
    for var in critical_vars:
        value = os.environ.get(var, 'NOT SET')
        print(f"  {var}: {value}")
    
    print()

def fix_environment():
    """Set critical environment variables"""
    print("🔧 Setting critical environment variables...")
    
    # Set critical variables
    os.environ['DEBUG'] = 'False'
    os.environ['SECURE_SSL_REDIRECT'] = 'False'
    os.environ['CORS_ALLOW_ALL_ORIGINS'] = 'False'
    
    # Ensure ALLOWED_HOSTS includes Railway domain
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
    
    print("✅ Environment variables fixed")

def generate_railway_commands():
    """Generate the correct Railway commands"""
    print("\n📋 RAILWAY COMMANDS TO USE:")
    print("=" * 40)
    
    print("\n🔨 BUILD COMMAND:")
    print("pip install -r requirements.txt && python manage.py collectstatic --noinput")
    
    print("\n🚀 START COMMAND (Option 1 - Recommended):")
    print("python railway_start.py")
    
    print("\n🚀 START COMMAND (Option 2 - Manual):")
    print("python test_db.py && python manage.py migrate && python manage.py collectstatic --noinput && python manage.py add_sample_data && gunicorn backend.wsgi --config railway_gunicorn.conf.py --bind 0.0.0.0:3000 --workers 1 --timeout 120 --log-level info")

def generate_env_vars():
    """Generate environment variables for Railway"""
    print("\n🔧 ENVIRONMENT VARIABLES TO SET IN RAILWAY:")
    print("=" * 50)
    
    env_vars = {
        'DEBUG': 'False',
        'SECURE_SSL_REDIRECT': 'False',
        'CORS_ALLOW_ALL_ORIGINS': 'False',
        'ALLOWED_HOSTS': 'tasty-fingers.up.railway.app,localhost,127.0.0.1,0.0.0.0',
        'CORS_ALLOWED_ORIGINS': 'https://tasty-fingers.up.railway.app,http://localhost:3000',
        'DATABASE_URL': 'postgresql://postgres:twnerPQrOqTIOXuMorQYOcZDJwoNahFQ@crossover.proxy.rlwy.net:18398/railway',
        'EMAIL_BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
        'EMAIL_HOST': 'smtp.gmail.com',
        'EMAIL_PORT': '587',
        'EMAIL_USE_TLS': 'True',
        'EMAIL_HOST_USER': 'gideonamienz24@gmail.com',
        'EMAIL_HOST_PASSWORD': 'bfdq jmxo ppuo izkt',
        'DEFAULT_FROM_EMAIL': 'gideonamienz24@gmail.com',
        'ADMIN_EMAIL': 'gideonamienz24@gmail.com',
        'SITE_NAME': 'TASTY FINGERS',
        'SITE_URL': 'https://tasty-fingers.up.railway.app',
        'CLOUDINARY_CLOUD_NAME': 'dao40lt42',
        'CLOUDINARY_API_KEY': '138773767419866',
        'CLOUDINARY_API_SECRET': 'Q-099CT3pgd-uHAt60xVDVRg-ok',
        'SECRET_KEY': 'FPSXru8or3uzUcK-MGDbaw8LkKx0uzrqa53LTQKafoQNDv4hc7sfRGnf0pny3ZSr2mI',
        'PORT': '3000'
    }
    
    for key, value in env_vars.items():
        print(f"{key}={value}")

def main():
    print_header()
    check_environment()
    fix_environment()
    generate_railway_commands()
    generate_env_vars()
    
    print("\n" + "=" * 50)
    print("✅ QUICK FIX COMPLETE!")
    print("\n📝 NEXT STEPS:")
    print("1. Update your Railway environment variables with the values above")
    print("2. Update your Railway build and start commands")
    print("3. Redeploy your application")
    print("4. Test your Railway URL - should work without 301 redirects!")
    print("\n🎯 Expected Result: Direct access to https://tasty-fingers.up.railway.app")

if __name__ == '__main__':
    main()
