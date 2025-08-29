@echo off
echo 🚀 Starting TASTY FINGERS with Fixed Configuration...
echo.

REM Set environment variables to prevent redirect issues
set DEBUG=True
set SECURE_SSL_REDIRECT=False
set CORS_ALLOW_ALL_ORIGINS=True

echo 📋 Configuration:
echo DEBUG=%DEBUG%
echo SECURE_SSL_REDIRECT=%SECURE_SSL_REDIRECT%
echo CORS_ALLOW_ALL_ORIGINS=%CORS_ALLOW_ALL_ORIGINS%
echo.

echo 🗄️ Running migrations...
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
echo ✅ Server should now run without 301 redirects!
echo 📍 Access: http://localhost:3000
echo 🔧 Admin: http://localhost:3000/admin
echo 📊 API: http://localhost:3000/api/
echo.
echo Press Ctrl+C to stop
echo.

python manage.py runserver 0.0.0.0:3000
