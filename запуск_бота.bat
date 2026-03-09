@echo off
chcp 65001 >nul
color 0A
title ИНТЕРАКТИВНЫЙ TELEGRAM БОТ

echo.
echo ========================================
echo   TELEGRAM БОТ С КНОПКАМИ
echo ========================================
echo.

cd /d "%~dp0"

echo Активация виртуального окружения...
call .venv\Scripts\activate.bat

echo.
echo ========================================
echo   БОТ ЗАПУСКАЕТСЯ...
echo ========================================
echo.
echo Откройте Telegram и напишите боту /start
echo.
echo Чтобы остановить бота, нажмите Ctrl+C
echo.

python bot_interactive.py

pause
