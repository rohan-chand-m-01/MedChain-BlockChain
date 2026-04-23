@echo off
echo ========================================
echo Fixing NPM and Installing Stellar SDK
echo ========================================

echo.
echo [Step 1] Cleaning npm cache...
cd frontend
call npm cache clean --force

echo.
echo [Step 2] Removing node_modules and lock files...
rmdir /s /q node_modules 2>nul
del package-lock.json 2>nul
del pnpm-lock.yaml 2>nul

echo.
echo [Step 3] Installing dependencies with pnpm...
call pnpm install

echo.
echo [Step 4] Installing Stellar SDK...
call pnpm add @stellar/stellar-sdk

echo.
echo [Step 5] Installing Stellar SDK for backend...
cd ..\backend
pip install stellar-sdk

echo.
echo ========================================
echo ✅ Installation Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Generate keypairs at https://laboratory.stellar.org
echo 2. Fund accounts at https://friendbot.stellar.org
echo 3. Update .env files with Stellar config
echo.
pause
