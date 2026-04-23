@echo off
echo ========================================
echo GET STELLAR PUBLIC ADDRESS
echo ========================================
echo.
echo Getting your Stellar testnet address...
echo.

cd backend
py -c "from stellar_sdk import Keypair; kp = Keypair.from_secret('SC45VCHFUBJAN566JUX3LRQI4OHGTOSE5GOS476WZZ7E7XNALPM5NO6O'); print(''); print('Your Stellar Public Address:'); print(kp.public_key); print(''); print('View on Stellar Expert:'); print(f'https://stellar.expert/explorer/testnet/account/{kp.public_key}'); print('')"

echo.
pause
