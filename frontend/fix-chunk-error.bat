@echo off
echo Fixing Next.js chunk loading error...
echo.

cd frontend

echo Step 1: Stopping any running dev servers...
taskkill /F /IM node.exe 2>nul
timeout /t 2 /nobreak >nul

echo Step 2: Cleaning Next.js cache...
if exist .next rmdir /s /q .next
if exist node_modules\.cache rmdir /s /q node_modules\.cache

echo Step 3: Starting fresh dev server...
echo.
echo Dev server starting on http://localhost:3000
echo.
npm run dev
