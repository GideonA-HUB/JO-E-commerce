@echo off
echo Starting CHOPHOUSE servers...
echo.

echo Starting Backend Server (Django)...
start "Backend Server" cmd /k "cd backend && call ..\venv\Scripts\activate.bat && python manage.py runserver 0.0.0.0:8000 --noreload"

echo Starting Frontend Server...
start "Frontend Server" cmd /k "npx live-server --port=3000"

echo.
echo Servers are starting...
echo Backend: http://127.0.0.1:8000/
echo Frontend: http://127.0.0.1:3000/
echo Admin: http://127.0.0.1:8000/admin/
echo.
pause 