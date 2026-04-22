@echo off
echo Stopping any running Next.js processes...
taskkill /F /IM node.exe /FI "WINDOWTITLE eq npm*" 2>nul

echo.
echo Starting Next.js dev server...
npm run dev
