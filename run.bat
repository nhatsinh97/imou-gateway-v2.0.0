@echo off
:: Imou Gateway v2.0.0 Startup Script

echo Starting Imou Gateway v2.0.0...
cd /d "%~dp0"

REM Create database folder if not exists
if not exist "database" mkdir database
if not exist "images" mkdir images

REM Run the Flask app
python app.py

pause
