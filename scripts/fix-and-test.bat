@echo off
echo ========================================
echo FIXING AND TESTING UPLOAD FLOW
echo ========================================
echo.

echo Step 1: Clearing browser cache...
echo Please do this manually:
echo   1. Open browser DevTools (F12)
echo   2. Right-click the refresh button
echo   3. Select "Empty Cache and Hard Reload"
echo.
pause

echo.
echo Step 2: Check if frontend picked up changes...
echo The upload flow should now include Stellar storage.
echo.
echo Step 3: Upload a test file
echo   1. Go to http://localhost:3000/patient
echo   2. Upload a medical file
echo   3. Watch the backend terminal for:
echo      - Risk score calculation
echo      - Stellar transaction hash
echo.
echo Step 4: Check browser console (F12) for:
echo   - [Upload] Stellar proof stored: HASH
echo   - Or any Stellar errors
echo.
echo Step 5: Check Stellar Explorer:
start https://stellar.expert/explorer/testnet/account/GCN6KJDKH4DRF2B7NXN3TNZNYDVPGOFOWLNB2AYE3LURQ6C5SPJS5ONV
echo.
echo ========================================
echo DEBUGGING TIPS
echo ========================================
echo.
echo If risk_score still shows 20%%:
echo   - Check backend logs for actual calculated risk_score
echo   - Check browser console: records[0].risk_score
echo.
echo If Stellar still not working:
echo   - Check browser console for Stellar errors
echo   - Check backend logs for Stellar transaction attempts
echo.
pause
