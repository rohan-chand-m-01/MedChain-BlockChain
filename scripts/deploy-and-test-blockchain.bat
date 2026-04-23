@echo off
echo ========================================
echo BLOCKCHAIN DEPLOYMENT AND TEST
echo ========================================
echo.
echo This script will:
echo 1. Check if Hardhat node is running
echo 2. Deploy the smart contract
echo 3. Run the test
echo.
pause

REM Check if Hardhat node is running
echo.
echo [1/3] Checking if Hardhat node is running...
curl -s -X POST -H "Content-Type: application/json" --data "{\"jsonrpc\":\"2.0\",\"method\":\"eth_blockNumber\",\"params\":[],\"id\":1}" http://127.0.0.1:8545 > nul 2>&1

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Hardhat node is not running!
    echo.
    echo Please start it first in another terminal:
    echo   cd blockchain
    echo   npx hardhat node
    echo.
    pause
    exit /b 1
)

echo    ✓ Hardhat node is running
echo.

REM Deploy contract
echo [2/3] Deploying smart contract...
cd blockchain
call npx hardhat run scripts/deploy.ts --network localhost
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Deployment failed!
    pause
    exit /b 1
)
cd ..

echo.
echo    ✓ Contract deployed
echo.
echo IMPORTANT: Copy the CONTRACT_ADDRESS from above and add to backend/.env
echo.
pause

REM Run test
echo [3/3] Running blockchain test...
echo.
cd backend
python test_blockchain_local.py

echo.
echo ========================================
echo TEST COMPLETE
echo ========================================
pause
