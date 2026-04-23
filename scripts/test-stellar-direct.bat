@echo off
echo ========================================
echo Testing Stellar Endpoint Directly
echo ========================================
echo.
echo This will call the backend Stellar endpoint directly
echo to see if it's working.
echo.

curl -X POST http://localhost:8000/api/stellar/store-proof ^
  -H "Content-Type: application/json" ^
  -d "{\"ipfs_hash\":\"QmTestHash123456789\",\"risk_score\":75,\"risk_level\":\"high\"}"

echo.
echo.
echo ========================================
echo Check the output above for:
echo 1. Success message with tx_hash
echo 2. Or error message
echo ========================================
pause
