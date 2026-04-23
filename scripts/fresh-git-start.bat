@echo off
echo ========================================
echo CREATING FRESH GIT REPOSITORY
echo ========================================
echo.
echo WARNING: This will delete all git history!
echo Press Ctrl+C to cancel, or
pause

echo.
echo Step 1: Removing old .git directory...
rd /s /q .git 2>nul
rd /s /q blockchain\.git 2>nul

echo Step 2: Cleaning all cache files...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
for /d /r . %%d in (.pytest_cache) do @if exist "%%d" rd /s /q "%%d"
for /d /r . %%d in (node_modules) do @if exist "%%d" rd /s /q "%%d"
for /d /r . %%d in (.next) do @if exist "%%d" rd /s /q "%%d"

echo Step 3: Initializing fresh git repository...
git init

echo Step 4: Creating .gitignore...
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
echo.
echo # Environment variables
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
echo blockchain/node_modules/
echo.
echo # Models and data
echo backend/models/*.pkl
echo backend/data/*.csv
echo.
echo # Temporary files
echo *.tmp
echo *.bak
echo *.backup
) > .gitignore

echo Step 5: Adding all files...
git add .

echo Step 6: Creating initial commit...
git commit -m "Initial commit: MediChain - AI-Powered Medical Records Platform with Blockchain"

echo.
echo ========================================
echo ✅ FRESH GIT REPOSITORY CREATED!
echo ========================================
echo.
echo Next steps:
echo 1. Create a new repository on GitHub
echo 2. Run: git remote add origin YOUR_GITHUB_URL
echo 3. Run: git branch -M main
echo 4. Run: git push -u origin main
echo.
pause
