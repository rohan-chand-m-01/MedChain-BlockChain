@echo off
echo ========================================
echo MediChain - Local Blockchain Setup
echo ========================================
echo.
echo This will:
echo 1. Start local Hardhat blockchain
echo 2. Deploy smart contracts
echo 3. Run test to verify hash storage
echo.
echo Press Ctrl+C to stop at any time
echo.
pause

REM Start Hardhat node in a new window
echo.
echo Step 1: Starting Hardhat node...
start "Hardhat Node" cmd /k "cd blockchain && npx hardhat node"

REM Wait for node to start
echo Waiting for blockchain to start...
timeout /t 5 /nobreak > nul

REM Deploy contracts
echo.
echo Step 2: Deploying contracts...
cd blockchain
call npx hardhat run scripts/deploy.ts --network localhost
cd ..

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Contract deployment failed!
    pause
    exit /b 1
)

REM Run test
echo.
echo Step 3: Running test...
echo.
cd backend
python test_blockchain_local.py
cd ..

echo.
echo ========================================
echo Test complete!
echo.
echo The Hardhat node is still running.
echo You can now:
echo   - Upload documents through the UI
echo   - Watch transactions in the Hardhat window
echo   - Run more tests
echo.
echo To stop the blockchain, close the Hardhat Node window
echo.
pause
