@echo off
chcp 65001 >nul 2>&1
color 0A
title Telegram Bot - Parser

cls
echo.
echo ========================================
echo   TELEGRAM BOT - PARSER
echo ========================================
echo.
echo Starting bot...
echo.
echo Open Telegram and send /start
echo.
echo Press Ctrl+C to stop
echo.
echo ========================================
echo.

cd /d "%~dp0"
call .venv\Scripts\activate.bat
python bot_interactive.py

pause
