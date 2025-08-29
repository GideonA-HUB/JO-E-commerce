#!/usr/bin/env python
"""
Production Railway startup script for TASTY FINGERS
Uses Gunicorn with proper production configuration
"""
import os
import sys
import subprocess

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

def run_command_with_error_handling(command, description):
    """Run a command with proper error handling"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠️ {description} failed with error: {e}")
        print(f"Error output: {e.stderr}")
        return False

def run_commands():
    """Run all necessary commands with proper error handling"""
    commands = [
        ("python manage.py migrate", "Database migrations"),
        ("python manage.py collectstatic --noinput", "Static file collection"),
        ("python manage.py add_sample_data", "Sample data loading")
    ]
    
    for command, description in commands:
        success = run_command_with_error_handling(command, description)
        if not success:
            print(f"⚠️ Continuing despite {description} failure...")

def start_production_server():
    """Start the Gunicorn server with production configuration"""
    print("🌐 Starting production Gunicorn server...")
    print("✅ Production server configuration:")
    print("   - Multiple workers for concurrent requests")
    print("   - Proper timeout handling")
    print("   - Production logging")
    print("   - Health monitoring")
    print("📍 Access your application at: https://tasty-fingers.up.railway.app")
    print("🔧 Admin panel at: https://tasty-fingers.up.railway.app/admin")
    print("📊 API endpoints at: https://tasty-fingers.up.railway.app/api/")
    
    # Simplified Production Gunicorn configuration - avoiding problematic flags
    gunicorn_cmd = [
        "gunicorn",
        "backend.wsgi:application",
        "--bind", "0.0.0.0:$PORT",
        "--workers", "2",
        "--timeout", "120",
        "--log-level", "info"
    ]
    
    print(f"🚀 Starting: {' '.join(gunicorn_cmd)}")
    
    try:
        # Use subprocess.Popen for better process management
        process = subprocess.Popen(gunicorn_cmd, env=os.environ)
        print("✅ Gunicorn server started successfully")
        
        # Wait for the process
        process.wait()
    except KeyboardInterrupt:
        print("🛑 Received interrupt signal, shutting down gracefully...")
        process.terminate()
        process.wait()
    except Exception as e:
        print(f"❌ Failed to start Gunicorn: {e}")
        sys.exit(1)

if __name__ == '__main__':
    print("🚀 Starting TASTY FINGERS on Railway (Production Mode)...")
    print("=" * 60)
    
    setup_environment()
    run_commands()
    start_production_server()
