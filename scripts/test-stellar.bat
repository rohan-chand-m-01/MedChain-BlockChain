@echo off
echo ========================================
echo Testing Stellar Integration
echo ========================================

echo.
echo Enter your Gas Wallet Public Key:
set /p GAS_WALLET_KEY=

echo.
echo [Test 1] Checking Stellar connection...
curl http://localhost:8000/api/stellar/account/%GAS_WALLET_KEY%

echo.
echo.
echo [Test 2] Checking backend health...
curl http://localhost:8000/health

echo.
echo.
echo ========================================
echo Tests Complete!
echo ========================================
echo.
echo If you see account balance, Stellar is working! ✅
echo.
echo Next steps:
echo 1. Upload a medical report in the frontend
echo 2. Check Stellar Expert for the transaction
echo 3. Grant doctor access
echo 4. Verify access works
echo.
pause
