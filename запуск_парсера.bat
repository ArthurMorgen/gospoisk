@echo off
title Tender Parser - Start
echo.
echo ========================================
echo   GOVERNMENT TENDER PARSER
echo ========================================
echo.
echo Checking VPN connection...
ping -n 1 zakupki.gov.ru >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: zakupki.gov.ru is not accessible
    echo Maybe VPN is enabled - please disable it!
    echo.
    pause
    exit /b 1
)
echo Connection to zakupki.gov.ru - OK

echo.
echo Changing to project directory...
cd /d "%~dp0"

echo Activating virtual environment...
if not exist ".venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Make sure .venv folder exists
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat

echo.
echo ========================================
echo   STARTING TENDER PARSER
echo ========================================
echo.
echo Parser is running...
echo Notifications will be sent to Telegram
echo Logs are saved to parser.log
echo.
echo WARNING: Do not close this window!
echo Press Ctrl+C to stop
echo.

python main.py

echo.
echo ========================================
echo Parser finished working
echo ========================================
pause
