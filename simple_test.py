"""
Простой тест Telegram бота
"""

print("🔍 ДИАГНОСТИКА TELEGRAM БОТА")
print("=" * 40)

# Проверка 1: Импорт библиотек
print("\n1. Проверка библиотек...")
try:
    import requests
    print("✅ requests - OK")
except ImportError:
    print("❌ requests не установлен")

try:
    from telegram import Bot
    print("✅ python-telegram-bot - OK")
except ImportError:
    print("❌ python-telegram-bot не установлен")

# Проверка 2: Настройки
print("\n2. Проверка настроек...")
try:
    from config import NOTIFICATION_CONFIG
    bot_token = NOTIFICATION_CONFIG['telegram']['bot_token']
    chat_ids = NOTIFICATION_CONFIG['telegram']['chat_ids']
    
    print(f"✅ Токен бота: {bot_token[:10]}...{bot_token[-10:]}")
    print(f"✅ Chat ID: {chat_ids[0]}")
    
    if bot_token == 'YOUR_BOT_TOKEN_HERE':
        print("❌ Токен не настроен!")
    if chat_ids[0] == 'YOUR_CHAT_ID_HERE':
        print("❌ Chat ID не настроен!")
        
except Exception as e:
    print(f"❌ Ошибка конфига: {e}")

# Проверка 3: Отправка через HTTP API
print("\n3. Отправка тестового сообщения...")
try:
    import requests
    from config import NOTIFICATION_CONFIG
    
    bot_token = NOTIFICATION_CONFIG['telegram']['bot_token']
    chat_id = NOTIFICATION_CONFIG['telegram']['chat_ids'][0]
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    data = {
        "chat_id": chat_id,
        "text": "🧪 ТЕСТ БОТА УСПЕШЕН!\nЭто сообщение означает, что ваш парсер тендеров готов к работе!"
    }
    
    response = requests.post(url, data=data, timeout=10)
    
    if response.status_code == 200:
        print("✅ Сообщение отправлено успешно!")
    else:
        print(f"❌ Ошибка HTTP: {response.status_code}")
        print(f"Ответ: {response.text}")
    
except Exception as e:
    print(f"❌ Ошибка отправки: {e}")

print("\n" + "=" * 40)
print("Проверьте Telegram на наличие сообщений от бота")
