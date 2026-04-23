@echo off
echo ========================================
echo Restarting Backend with Urgency Fix
echo ========================================
echo.
echo This will restart the backend to load the fixed code
echo.
echo Press Ctrl+C in the backend terminal window to stop it
echo Then run this command:
echo.
echo   cd backend
echo   uvicorn main:app --reload
echo.
echo After restart, upload a file and check:
echo 1. Browser console for Stellar transaction logs
echo 2. Backend terminal for success messages
echo 3. Stellar Expert for your transactions
echo.
echo Your account:
echo https://stellar.expert/explorer/testnet/account/GCN6KJDKH4DRF2B7NXN3TNZNYDVPGOFOWLNB2AYE3LURQ6C5SFUS50NV
echo.
pause
