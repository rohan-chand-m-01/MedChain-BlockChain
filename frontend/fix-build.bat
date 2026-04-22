@echo off
echo Cleaning Next.js cache and rebuilding...

REM Stop any running dev servers
taskkill /F /IM node.exe 2>nul

REM Clean build artifacts
if exist .next rmdir /s /q .next
if exist node_modules\.cache rmdir /s /q node_modules\.cache

echo Cache cleaned. Starting fresh dev server...
pnpm run dev
