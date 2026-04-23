@echo off
echo ========================================
echo Local Blockchain Test
echo ========================================
echo.

REM Check if Hardhat node is running
echo Checking if Hardhat node is running...
curl -s -X POST -H "Content-Type: application/json" --data "{\"jsonrpc\":\"2.0\",\"method\":\"eth_blockNumber\",\"params\":[],\"id\":1}" http://127.0.0.1:8545 > nul 2>&1

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Hardhat node is not running!
    echo.
    echo Please start it first:
    echo   1. Open a new terminal
    echo   2. cd blockchain
    echo   3. npx hardhat node
    echo.
    pause
    exit /b 1
)

echo Hardhat node is running!
echo.

REM Run the test
echo Running blockchain test...
echo.
cd backend
python test_blockchain_local.py

echo.
pause
