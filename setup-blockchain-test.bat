@echo off
echo ========================================
echo BLOCKCHAIN SETUP AND TEST
echo ========================================
echo.
echo This script will set up everything needed for blockchain testing.
echo.
echo Steps:
echo 1. Clean Hardhat cache
echo 2. Compile contracts
echo 3. Check if Hardhat node is running
echo 4. Deploy contract
echo 5. Update .env file
echo 6. Run test
echo.
pause

REM Step 1: Clean and compile
echo.
echo ========================================
echo STEP 1: Clean and Compile
echo ========================================
cd blockchain

echo Cleaning cache...
if exist cache rmdir /s /q cache
if exist artifacts rmdir /s /q artifacts
echo    ✓ Cache cleaned

echo.
echo Compiling contracts...
call npx hardhat compile

if %errorlevel% neq 0 (
    echo.
    echo ❌ Compilation failed!
    echo Please fix the errors above and try again.
    cd ..
    pause
    exit /b 1
)

echo    ✓ Contracts compiled successfully
cd ..

REM Step 2: Check Hardhat node
echo.
echo ========================================
echo STEP 2: Check Hardhat Node
echo ========================================
curl -s -X POST -H "Content-Type: application/json" --data "{\"jsonrpc\":\"2.0\",\"method\":\"eth_blockNumber\",\"params\":[],\"id\":1}" http://127.0.0.1:8545 > nul 2>&1

if %errorlevel% neq 0 (
    echo.
    echo ❌ Hardhat node is not running!
    echo.
    echo Please start it in another terminal:
    echo   cd blockchain
    echo   npx hardhat node
    echo.
    echo Then run this script again.
    pause
    exit /b 1
)

echo    ✓ Hardhat node is running

REM Step 3: Deploy contract
echo.
echo ========================================
echo STEP 3: Deploy Contract
echo ========================================
cd blockchain
call npx hardhat run scripts/deploy.ts --network localhost

if %errorlevel% neq 0 (
    echo.
    echo ❌ Deployment failed!
    cd ..
    pause
    exit /b 1
)

cd ..

REM Step 4: Prompt for .env update
echo.
echo ========================================
echo STEP 4: Update .env File
echo ========================================
echo.
echo IMPORTANT: Copy the CONTRACT_ADDRESS from above
echo and add these lines to backend/.env:
echo.
echo CONTRACT_ADDRESS=0x5FbDB2315678afecb367f032d93F642f64180aa3
echo GAS_WALLET_PRIVATE_KEY=0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80
echo.
echo (Use the actual CONTRACT_ADDRESS from deployment output above)
echo (The private key is the first one from Hardhat node)
echo.
echo Press any key after you've updated backend/.env...
pause > nul

REM Step 5: Run test
echo.
echo ========================================
echo STEP 5: Run Test
echo ========================================
cd backend
python test_blockchain_local.py

echo.
echo ========================================
echo SETUP COMPLETE
echo ========================================
pause
