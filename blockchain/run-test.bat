@echo off
echo ========================================
echo RUNNING BLOCKCHAIN TEST
echo ========================================
echo.
echo Testing document hash storage...
echo.

cd ..
cd backend
py test_blockchain_local.py

pause
