echo off

echo -----------------------------------
echo Ramo Estudantil IEEE CEFET-RJ
echo Computer Society Chapter - Wolfbyte
echo IA+BOT - PROJECT VSSS (2025)
echo -----------------------------------
echo Starting MQTT Client (Simulating Robot)
echo -----------------------------------

cd ..
vsss_venv\Scripts\activate && cmd/k python comms\mqtt_client.py
pause