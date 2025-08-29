@echo off
echo 🚀 Starting TASTY FINGERS with fixed redirect configuration...
echo.

REM Set environment variables to prevent redirect issues
set DEBUG=True
set SECURE_SSL_REDIRECT=False
set CORS_ALLOW_ALL_ORIGINS=True

echo 📋 Environment Configuration:
echo DEBUG=%DEBUG%
echo SECURE_SSL_REDIRECT=%SECURE_SSL_REDIRECT%
echo CORS_ALLOW_ALL_ORIGINS=%CORS_ALLOW_ALL_ORIGINS%
echo.

echo 🔍 Testing current configuration...
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

echo 🌐 Starting server on port 3000...
echo.
echo ✅ Server should now be running without 301 redirects!
echo 📍 Access your application at: http://localhost:3000
echo 🔧 Admin panel at: http://localhost:3000/admin
echo 📊 API endpoints at: http://localhost:3000/api/
echo.
echo Press Ctrl+C to stop the server
echo.

python run_server_debug.py
