@echo off
echo ========================================
echo Testing Stellar Upload Flow
echo ========================================
echo.

cd backend
python ..\test-stellar-upload.py
cd ..

echo.
echo ========================================
echo Test Complete
echo ========================================
pause
