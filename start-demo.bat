@echo off
echo ========================================
echo Starting MediChain Demo with LocalTunnel
echo ========================================
echo.

REM Start backend in new window
echo [1/3] Starting Backend Server...
start "MediChain Backend" cmd /k "cd backend && uvicorn main:app --host 0.0.0.0 --port 8000"
timeout /t 5 /nobreak > nul

REM Start frontend in new window
echo [2/3] Starting Frontend Server...
start "MediChain Frontend" cmd /k "cd frontend && npm run dev"
timeout /t 5 /nobreak > nul

REM Start LocalTunnel for backend (for WhatsApp webhooks)
echo [3/3] Starting LocalTunnel for Backend...
start "LocalTunnel Backend" cmd /k "lt --port 8000"

echo.
echo ========================================
echo Demo servers started!
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo.
echo LocalTunnel: Check the LocalTunnel window for public URL
echo Use the public URL for WhatsApp webhook configuration
echo.
echo ========================================
echo.
echo Press any key to stop all servers...
pause > nul

REM Kill all services
echo.
echo Stopping servers...
taskkill /FI "WindowTitle eq MediChain Backend*" /F >nul 2>&1
taskkill /FI "WindowTitle eq MediChain Frontend*" /F >nul 2>&1
taskkill /FI "WindowTitle eq LocalTunnel Backend*" /F >nul 2>&1
echo Servers stopped.
echo ========================================
pause
