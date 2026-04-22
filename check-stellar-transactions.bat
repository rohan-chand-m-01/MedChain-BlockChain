@echo off
echo ========================================
echo CHECKING STELLAR TESTNET TRANSACTIONS
echo ========================================
echo.
echo Gas Wallet Account:
echo GCN6KJDKH4DRF2B7NXN3TNZNYDVPGOFOWLNB2AYE3LURQ6C5SPJS5ONV
echo.
echo Opening Stellar Expert in browser...
start https://stellar.expert/explorer/testnet/account/GCN6KJDKH4DRF2B7NXN3TNZNYDVPGOFOWLNB2AYE3LURQ6C5SPJS5ONV
echo.
echo You should see transactions for each uploaded file.
echo Each transaction stores:
echo   - IPFS hash (ipfs_XXXXXXXX)
echo   - Risk score and level (risk_XXXXXXXX)
echo.
pause
