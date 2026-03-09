@echo off
chcp 65001 >nul
echo ============================================================
echo УСТАНОВКА SELENIUM ДЛЯ АВТОМАТИЧЕСКОГО ПАРСИНГА
echo ============================================================
echo.
echo 📦 Устанавливаю Selenium...
pip install selenium
echo.
echo 🚗 Устанавливаю WebDriver Manager...
pip install webdriver-manager
echo.
echo ============================================================
echo ✅ ГОТОВО!
echo ============================================================
echo.
echo 🧪 Проверка установки:
python -c "from selenium import webdriver; print('✓ Selenium установлен')"
echo.
echo 🚀 Теперь можно запускать:
echo    python bot_interactive.py
echo.
echo или
echo    python main.py
echo.
pause
