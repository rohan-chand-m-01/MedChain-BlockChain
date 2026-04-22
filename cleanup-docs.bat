@echo off
echo ========================================
echo CLEANING UP TEMPORARY DOCUMENTATION
echo ========================================
echo.
echo This will delete temporary .md files created during development.
echo Press Ctrl+C to cancel, or
pause

echo.
echo Deleting temporary documentation files...

del /q AGENTS.md 2>nul
del /q ARCHITECTURE_DIAGRAM.md 2>nul
del /q BLOCKCHAIN_FIXES_COMPLETE.md 2>nul
del /q BLOCKCHAIN_PITCH.md 2>nul
del /q BLOCKCHAIN_SUCCESS.md 2>nul
del /q BLOCKCHAIN_TEST_GUIDE.md 2>nul
del /q COMPLETE_FEATURE_LIST_WITH_BLOCKCHAIN.md 2>nul
del /q DEMO_RECOVERY_FEATURE.md 2>nul
del /q DOCTOR_PATIENT_VIEW_COMPLETE.md 2>nul
del /q DOCTOR_PATIENT_VIEW_SPEC.md 2>nul
del /q FIX_APPLIED.md 2>nul
del /q FIXES_COMPLETE.md 2>nul
del /q GEMINI_2.5_UPGRADE_COMPLETE.md 2>nul
del /q GEMINI_MODEL_UPDATE_COMPLETE.md 2>nul
del /q GEMINI_PRIMARY_SETUP.md 2>nul
del /q GEMINI_RISK_SCORE_FIX.md 2>nul
del /q IMPLEMENTATION_COMPLETE.md 2>nul
del /q LOCAL_BLOCKCHAIN_TEST.md 2>nul
del /q MEDGEMMA_GRADIO_INTEGRATION.md 2>nul
del /q MIGRATION_SUMMARY.md 2>nul
del /q MULTI_ACCOUNT_SETUP.md 2>nul
del /q PATIENT_PROFILE_FEATURE_COMPLETE.md 2>nul
del /q PRIVY_ENCRYPTION_GUIDE.md 2>nul
del /q PRIVY_SETUP_COMPLETE.md 2>nul
del /q PROFILE_FEATURE_IMPLEMENTATION.md 2>nul
del /q QUICK_REFERENCE.md 2>nul
del /q RECOVERY_BUTTON_LOCATION.md 2>nul
del /q RECOVERY_FEATURE_SUMMARY.md 2>nul
del /q RECOVERY_UI_REDESIGN.md 2>nul
del /q RISK_SCORE_20_ISSUE_EXPLAINED.md 2>nul
del /q RISK_SCORE_FIX_COMPLETE.md 2>nul
del /q RUN_TEST_NOW.md 2>nul
del /q SEPOLIA_SETUP_GUIDE.md 2>nul
del /q SETUP_MEDGEMMA.md 2>nul
del /q STELLAR_FIX_COMPLETE.md 2>nul
del /q STELLAR_FIX_SUMMARY.md 2>nul
del /q STELLAR_HASH_FIX.md 2>nul
del /q STELLAR_IMPLEMENTATION_COMPLETE.md 2>nul
del /q STELLAR_INTEGRATION_FLOW.md 2>nul
del /q STELLAR_MIGRATION_GUIDE.md 2>nul
del /q STELLAR_QUICK_START.md 2>nul
del /q STELLAR_STORAGE_FIX.md 2>nul
del /q STELLAR_TESTNET_READY.md 2>nul
del /q TEST_STELLAR_NOW.md 2>nul
del /q TIMEBOUND_ACCESS_FEATURE.md 2>nul
del /q TIMEBOUND_ACCESS_UI_UPDATE.md 2>nul
del /q VIEW_STELLAR_TESTNET.md 2>nul
del /q WHATSAPP_NOTIFICATION_COMPLETE.md 2>nul
del /q WORKING_RECOVERY_CODE.tsx 2>nul

echo.
echo Deleting test files...
del /q test_*.py 2>nul
del /q write_stellar_client.py 2>nul
del /q check-backend-logs.bat 2>nul
del /q restart-backend-simple.bat 2>nul

echo.
echo ✅ Cleanup complete!
echo.
pause
