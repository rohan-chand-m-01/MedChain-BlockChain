@echo off
echo ========================================
echo Testing Urgency Fix
echo ========================================
echo.
echo This will verify that urgency values are now valid
echo.

cd backend

echo Checking current backend process...
curl http://localhost:8000/health 2>nul
if errorlevel 1 (
    echo.
    echo ❌ Backend is not running!
    echo Please start it with: cd backend ^&^& uvicorn main:app --reload
    pause
    exit /b 1
)

echo.
echo ✅ Backend is running
echo.
echo Now upload a file through the UI at:
echo http://localhost:3000/patient
echo.
echo Watch for these logs in the backend terminal:
echo   - INFO: [ANALYZE] ✅ Database record saved successfully
echo   - INFO: ✅ Stellar transaction successful
echo.
echo And in the browser console:
echo   - [Upload] ✅ Stellar proof stored successfully!
echo   - [Upload] Transaction hash: ...
echo.
echo Then check your Stellar account:
echo https://stellar.expert/explorer/testnet/account/GCN6KJDKH4DRF2B7NXN3TNZNYDVPGOFOWLNB2AYE3LURQ6C5SFUS50NV
echo.
echo You should see Total trades ^> 0
echo.
pause
