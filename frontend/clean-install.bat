@echo off
echo ========================================
echo MediChain - Clean npm Install Script
echo ========================================
echo.

echo Step 1: Killing all Node processes...
taskkill /F /IM node.exe 2>nul
if %errorlevel% equ 0 (
    echo Node processes killed successfully
) else (
    echo No Node processes running
)
echo.

echo Step 2: Deleting node_modules (this may take a minute)...
if exist node_modules (
    rmdir /s /q node_modules
    echo node_modules deleted
) else (
    echo node_modules not found
)
echo.

echo Step 3: Deleting package-lock.json...
if exist package-lock.json (
    del /f /q package-lock.json
    echo package-lock.json deleted
) else (
    echo package-lock.json not found
)
echo.

echo Step 4: Clearing npm cache...
call npm cache clean --force
echo npm cache cleared
echo.

echo Step 5: Installing packages with legacy peer deps...
echo This will take 2-5 minutes...
echo.
call npm install --legacy-peer-deps
echo.

if %errorlevel% equ 0 (
    echo ========================================
    echo SUCCESS! All packages installed
    echo ========================================
    echo.
    echo You can now run: npm run dev
) else (
    echo ========================================
    echo FAILED! Check errors above
    echo ========================================
    echo.
    echo Try running as Administrator or use:
    echo pnpm install
)
echo.
pause
