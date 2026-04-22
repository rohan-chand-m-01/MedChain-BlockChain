@echo off
echo Installing Stellar SDK...

echo.
echo [1/2] Installing Stellar SDK for frontend...
cd frontend
call pnpm add @stellar/stellar-sdk

echo.
echo [2/2] Installing Stellar SDK for backend...
cd ..\backend
pip install stellar-sdk

echo.
echo ✅ Stellar SDK installation complete!
pause
