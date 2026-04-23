@echo off
echo ========================================
echo Testing Privacy Features (FHE + ZK-Proofs)
echo ========================================
echo.

echo Make sure backend is running on http://localhost:8000
echo.
echo Press any key to start tests...
pause > nul

python test_privacy_features.py

echo.
echo ========================================
echo Tests complete!
echo ========================================
echo.
echo Check PRIVACY_FEATURES.md for documentation
echo.
pause
