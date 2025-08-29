@echo off
echo 🚀 Starting TASTY FINGERS in Production Mode...
echo.

REM Set production environment variables
set DEBUG=False
set SECURE_SSL_REDIRECT=False
set CORS_ALLOW_ALL_ORIGINS=False

echo 📋 Production Configuration:
echo DEBUG=%DEBUG%
echo SECURE_SSL_REDIRECT=%SECURE_SSL_REDIRECT%
echo CORS_ALLOW_ALL_ORIGINS=%CORS_ALLOW_ALL_ORIGINS%
echo.

echo 🔍 Testing configuration...
python test_redirects.py
echo.

echo 🗄️ Running database migrations...
python manage.py migrate
echo.

echo 📦 Collecting static files...
python manage.py collectstatic --noinput
echo.

echo 🎯 Adding sample data...
python manage.py add_sample_data
echo.

echo 🌐 Starting production server with Gunicorn...
echo.
echo ✅ Server configured to prevent 301 redirects!
echo 📍 Access your application at: http://localhost:3000
echo 🔧 Admin panel at: http://localhost:3000/admin
echo 📊 API endpoints at: http://localhost:3000/api/
echo.
echo Press Ctrl+C to stop the server
echo.

REM Use the new gunicorn configuration
gunicorn backend.wsgi --config gunicorn.conf.py
