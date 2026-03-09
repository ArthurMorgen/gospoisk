"""
Прямой тест отправки в Telegram
"""
import requests

# Настройки из вашего конфига
BOT_TOKEN = "8257830122:AAG4MPYgELY3x2z9OlNM10YKCPmT_iRcqiw"
CHAT_ID = "1382173062"

print("🔍 ПРЯМОЙ ТЕСТ TELEGRAM")
print("=" * 30)

# Простая отправка сообщения
try:
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    data = {
        "chat_id": CHAT_ID,
        "text": "🧪 ТЕСТ РАБОТАЕТ!\n\nЭто прямое сообщение от парсера тендеров."
    }
    
    print(f"Отправляем на: {url}")
    print(f"Chat ID: {CHAT_ID}")
    
    response = requests.post(url, data=data)
    
    print(f"Статус ответа: {response.status_code}")
    print(f"Ответ сервера: {response.text}")
    
    if response.status_code == 200:
        print("✅ УСПЕШНО! Проверьте Telegram")
    else:
        print(f"❌ ОШИБКА: {response.status_code}")
        
except Exception as e:
    print(f"❌ Исключение: {e}")

print("\nЕсли сообщение не пришло, проверьте:")
print("1. Правильность токена бота")  
print("2. Правильность chat_id")
print("3. Написали ли вы боту /start")
