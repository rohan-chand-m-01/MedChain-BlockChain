@echo off
echo Restarting backend...
cd backend
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *uvicorn*" 2>nul
timeout /t 2 /nobreak >nul
start "MediChain Backend" cmd /k "py -m uvicorn main:app --reload --port 8000"
echo Backend restarted on port 8000
cd ..
