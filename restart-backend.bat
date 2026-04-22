@echo off
echo Restarting backend...
taskkill /F /IM python.exe 2>nul
timeout /t 2 /nobreak >nul
cd backend
start cmd /k "py main.py"
echo Backend restarted!
