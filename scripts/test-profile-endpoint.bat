@echo off
echo Testing Profile Endpoint...
echo.

REM Test with a sample wallet address
set WALLET=0x0c4d06415704b313caAE6793FFe087b44A4d9656

echo Testing GET /api/profiles/patient/%WALLET%
curl -X GET "http://localhost:8000/api/profiles/patient/%WALLET%" -H "Content-Type: application/json"
echo.
echo.

echo Testing POST /api/profiles/patient/%WALLET%
curl -X POST "http://localhost:8000/api/profiles/patient/%WALLET%" ^
  -H "Content-Type: application/json" ^
  -d "{\"full_name\":\"Test Patient\",\"email\":\"test@example.com\"}"
echo.
echo.

pause
