@echo off
echo ========================================
echo CLEAN AND COMPILE SMART CONTRACTS
echo ========================================
echo.
echo This will:
echo 1. Clean Hardhat cache
echo 2. Compile all contracts
echo.

REM Clean cache and artifacts
echo [1/2] Cleaning cache and artifacts...
if exist cache rmdir /s /q cache
if exist artifacts rmdir /s /q artifacts
echo    ✓ Cache cleaned
echo.

REM Compile contracts
echo [2/2] Compiling contracts...
call npx hardhat compile

if %errorlevel% equ 0 (
    echo.
    echo ✅ Compilation successful!
    echo.
    echo You can now deploy:
    echo   npx hardhat run scripts/deploy.ts --network localhost
) else (
    echo.
    echo ❌ Compilation failed!
    echo Check the errors above.
)

echo.
pause
