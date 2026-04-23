@echo off
echo ========================================
echo Checking Stellar Transaction Status
echo ========================================
echo.
echo Your Stellar Account:
echo GCN6KJDKH4DRF2B7NXN3TNZNYDVPGOFOWLNB2AYE3LURQ6C5SFUS50NV
echo.
echo Opening Stellar Expert in browser...
echo.
start https://stellar.expert/explorer/testnet/account/GCN6KJDKH4DRF2B7NXN3TNZNYDVPGOFOWLNB2AYE3LURQ6C5SFUS50NV
echo.
echo Check for:
echo 1. Total trades ^> 0 (should not be 0 anymore!)
echo 2. Recent transactions with memo "MEDICAL_RECORD:..."
echo 3. Data entries with keys like "ipfs_..." and "risk_..."
echo.
echo If you see transactions, the fix worked! ✅
echo If still 0 transactions, check browser console for errors.
echo.
pause
