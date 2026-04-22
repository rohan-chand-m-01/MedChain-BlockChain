@echo off
echo Testing LocalTunnel connection...
echo.

echo 1. Testing local backend:
curl -X POST http://localhost:8000/api/whatsapp/webhook -H "Content-Type: application/x-www-form-urlencoded" -d "From=whatsapp:+1234567890&Body=test&NumMedia=0&MessageSid=TEST123"

echo.
echo.
echo 2. Testing via LocalTunnel:
curl -X POST https://bitter-toys-relax.loca.lt/api/whatsapp/webhook -H "Content-Type: application/x-www-form-urlencoded" -H "Bypass-Tunnel-Reminder: true" -d "From=whatsapp:+1234567890&Body=test&NumMedia=0&MessageSid=TEST123"

pause
