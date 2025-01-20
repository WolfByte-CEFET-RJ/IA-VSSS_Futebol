echo off

echo -----------------------------------
echo Ramo Estudantil IEEE CEFET-RJ
echo Computer Society Chapter - Wolfbyte
echo IA+BOT - PROJECT VSSS (2025)
echo -----------------------------------
echo Creating Virtual Environment for VSSS (vsss_venv)
echo -----------------------------------

python -m venv vsss_venv

vsss_venv\Scripts\activate && pip install -r requirements.txt
pause