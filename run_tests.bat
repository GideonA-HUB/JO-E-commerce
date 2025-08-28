@echo off
echo ========================================
echo TASTY FINGERS - Order System Tests
echo ========================================
echo.

echo [1] Testing API endpoints...
python test_order_system.py
echo.

echo [2] Testing Django shell functionality...
cd backend
python manage.py shell < ../test_paystack_shell.py
cd ..
echo.

echo ========================================
echo Tests completed! Check test_results.json
echo ========================================
pause
