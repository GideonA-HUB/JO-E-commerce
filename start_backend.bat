@echo off
echo ========================================
echo    CHOPHOUSE Backend Startup
echo ========================================
echo.

echo [1/6] Navigating to project directory...
cd /d "C:\Users\SPEED\OneDrive\Desktop\JOJO"

echo [2/6] Activating virtual environment...
call venv\Scripts\activate

echo [3/6] Installing Python dependencies...
cd backend
pip install -r requirements.txt

echo [4/6] Running database migrations...
python manage.py makemigrations
python manage.py migrate

echo [5/6] Loading sample data...
python manage.py load_sample_products
python manage.py load_sample_catering_services

echo [6/6] Starting Django server...
echo.
echo ========================================
echo    Backend running at http://127.0.0.1:8000/
echo    API available at http://127.0.0.1:8000/api/
echo    Press Ctrl+C to stop the server
echo ========================================
echo.
python manage.py runserver

pause 