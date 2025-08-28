@echo off
echo ========================================
echo   TASTY FINGERS REVIEW TEST SUITE
echo ========================================
echo.

echo Checking if Django server is running...
curl -s http://127.0.0.1:8000/api/products/ >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Django server is not running!
    echo Please start the server first:
    echo   cd backend ^&^& python manage.py runserver
    echo.
    pause
    exit /b 1
)

echo ✅ Django server is running
echo.

echo ========================================
echo   RUNNING BACKEND API TESTS
echo ========================================
echo.

python test_review_functionality.py

echo.
echo ========================================
echo   RUNNING FRONTEND UI TESTS
echo ========================================
echo.

echo Note: Frontend tests require Chrome and ChromeDriver to be installed.
echo If you don't have them, you can skip this part.
echo.
set /p run_frontend="Do you want to run frontend tests? (y/n): "

if /i "%run_frontend%"=="y" (
    python test_frontend_reviews.py
) else (
    echo Skipping frontend tests.
)

echo.
echo ========================================
echo   TEST SUITE COMPLETE
echo ========================================
echo.
echo Check the output above for test results.
echo.
pause
