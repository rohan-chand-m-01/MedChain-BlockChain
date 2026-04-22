@echo off
echo Checking if backend is running...
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Backend is running on port 8000
) else (
    echo ❌ Backend is NOT running
    echo.
    echo To start backend:
    echo   cd backend
    echo   py -m uvicorn main:app --reload --port 8000
)
pause
