@echo off
echo ========================================
echo PREPARING PROJECT FOR GITHUB
echo ========================================
echo.
echo This will:
echo 1. Clean up temporary files
echo 2. Remove old git history
echo 3. Create fresh git repository
echo 4. Prepare for GitHub push
echo.
echo WARNING: This will delete all git history!
echo Press Ctrl+C to cancel, or
pause

echo.
echo ========================================
echo STEP 1: CLEANING TEMPORARY FILES
echo ========================================

echo Removing Python cache...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
for /d /r . %%d in (.pytest_cache) do @if exist "%%d" rd /s /q "%%d"

echo Removing Node modules (will need reinstall)...
rd /s /q frontend\node_modules 2>nul
rd /s /q blockchain\node_modules 2>nul

echo Removing build artifacts...
rd /s /q frontend\.next 2>nul
rd /s /q blockchain\artifacts 2>nul
rd /s /q blockchain\cache 2>nul

echo Removing temporary documentation...
del /q AGENTS.md 2>nul
del /q BLOCKCHAIN_*.md 2>nul
del /q COMPLETE_*.md 2>nul
del /q DEMO_*.md 2>nul
del /q DOCTOR_*.md 2>nul
del /q FIX*.md 2>nul
del /q GEMINI_*.md 2>nul
del /q IMPLEMENTATION_*.md 2>nul
del /q LOCAL_*.md 2>nul
del /q MEDGEMMA_*.md 2>nul
del /q MIGRATION_*.md 2>nul
del /q MULTI_*.md 2>nul
del /q PATIENT_*.md 2>nul
del /q PRIVY_*.md 2>nul
del /q PROFILE_*.md 2>nul
del /q QUICK_*.md 2>nul
del /q RECOVERY_*.md 2>nul
del /q RISK_*.md 2>nul
del /q RUN_*.md 2>nul
del /q SEPOLIA_*.md 2>nul
del /q SETUP_*.md 2>nul
del /q STELLAR_*.md 2>nul
del /q TEST_*.md 2>nul
del /q TIMEBOUND_*.md 2>nul
del /q VIEW_*.md 2>nul
del /q WHATSAPP_*.md 2>nul
del /q WORKING_*.tsx 2>nul

echo Removing test files...
del /q test_*.py 2>nul
del /q write_*.py 2>nul
del /q check-*.bat 2>nul
del /q restart-backend-simple.bat 2>nul
del /q cleanup-docs.bat 2>nul
del /q fresh-git-start.bat 2>nul

echo.
echo ========================================
echo STEP 2: REMOVING OLD GIT HISTORY
echo ========================================

rd /s /q .git 2>nul
rd /s /q blockchain\.git 2>nul
echo ✅ Old git history removed

echo.
echo ========================================
echo STEP 3: CREATING FRESH GIT REPOSITORY
echo ========================================

git init
echo ✅ Fresh git repository initialized

echo.
echo Creating comprehensive .gitignore...
(
echo # Python
echo __pycache__/
echo *.py[cod]
echo *$py.class
echo *.so
echo .Python
echo env/
echo venv/
echo ENV/
echo .pytest_cache/
echo .coverage
echo htmlcov/
echo *.pkl
echo.
echo # Node
echo node_modules/
echo .next/
echo out/
echo build/
echo dist/
echo *.log
echo npm-debug.log*
echo yarn-debug.log*
echo yarn-error.log*
echo package-lock.json
echo.
echo # Environment variables - IMPORTANT!
echo .env
echo .env.local
echo .env.*.local
echo backend/.env
echo frontend/.env
echo.
echo # IDE
echo .vscode/
echo .idea/
echo *.swp
echo *.swo
echo *~
echo.
echo # OS
echo .DS_Store
echo Thumbs.db
echo desktop.ini
echo.
echo # Blockchain
echo blockchain/artifacts/
echo blockchain/cache/
echo blockchain/typechain-types/
echo.
echo # Data files
echo backend/data/*.csv
echo.
echo # Temporary files
echo *.tmp
echo *.bak
echo *.backup
echo.
echo # Batch scripts for cleanup
echo cleanup-*.bat
echo fresh-git-*.bat
echo prepare-for-github.bat
) > .gitignore
echo ✅ .gitignore created

echo.
echo Adding all files...
git add .
echo ✅ Files staged

echo.
echo Creating initial commit...
git commit -m "Initial commit: MediChain - AI-Powered Medical Records Platform

Features:
- AI medical analysis with Google Gemini 2.5 Flash
- Stellar blockchain verification
- End-to-end encryption with Privy
- IPFS decentralized storage
- Multi-role system (Patient/Doctor)
- Real-time AI medical assistant
- Risk score calculation with ML models
- Time-bound access control
- WhatsApp notifications

Tech Stack:
- Frontend: Next.js 15, React 19, TypeScript, Tailwind CSS
- Backend: FastAPI, Python, PostgreSQL
- Blockchain: Stellar Testnet
- AI: Google Gemini, Custom ML models"

echo ✅ Initial commit created

echo.
echo ========================================
echo ✅ PROJECT READY FOR GITHUB!
echo ========================================
echo.
echo Next steps:
echo.
echo 1. Create a new repository on GitHub (https://github.com/new)
echo    - Name: medichain or medicare
echo    - Description: AI-Powered Medical Records Platform with Blockchain
echo    - Make it Public or Private
echo    - DO NOT initialize with README (we already have one)
echo.
echo 2. Copy your repository URL (looks like: https://github.com/username/repo.git)
echo.
echo 3. Run these commands:
echo    git remote add origin YOUR_GITHUB_URL
echo    git branch -M main
echo    git push -u origin main
echo.
echo 4. IMPORTANT: Before pushing, make sure your .env files are NOT committed!
echo    Check with: git status
echo.
echo 5. After pushing, reinstall dependencies:
echo    cd frontend ^&^& npm install
echo.
pause
