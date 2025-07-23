@echo off
echo Starting Django Server...
echo.
cd backend
python manage.py runserver 0.0.0.0:8000
pause 