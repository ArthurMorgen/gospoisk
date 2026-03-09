"""
Быстрый тест работы системы
"""

import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_system():
    print("🧪 БЫСТРЫЙ ТЕСТ СИСТЕМЫ")
    print("=" * 30)
    
    # Тест 1: Уведомления
    print("\n1. Тест уведомлений...")
    try:
        from notifications import NotificationManager
        notification_manager = NotificationManager()
        
        test_tender = {
            'title': '🧪 НАЙДЕН ТЕСТОВЫЙ ТЕНДЕР',
            'platform': 'Тестовая площадка',
            'price': 500000,
            'currency': 'RUB',
            'customer': 'Тестовый заказчик',
            'deadline': '2024-12-31',
            'url': 'https://example.com/test',
            'description': 'Поставка грамот и дипломов'
        }
        
        success = notification_manager.send_tender_notification(test_tender)
        if success:
            print("✅ Уведомления работают!")
        else:
            print("❌ Проблема с уведомлениями")
            
    except Exception as e:
        print(f"❌ Ошибка уведомлений: {e}")
    
    # Тест 2: База данных
    print("\n2. Тест базы данных...")
    try:
        from database import TenderDatabase
        db = TenderDatabase()
        stats = db.get_statistics()
        print(f"✅ База данных работает. Тендеров: {stats.get('total_tenders', 0)}")
    except Exception as e:
        print(f"❌ Ошибка базы данных: {e}")
    
    # Тест 3: Простой HTTP запрос
    print("\n3. Тест HTTP запросов...")
    try:
        import requests
        response = requests.get('https://httpbin.org/get', timeout=10)
        if response.status_code == 200:
            print("✅ HTTP запросы работают")
        else:
            print(f"⚠️ HTTP статус: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка HTTP: {e}")
    
    print("\n" + "=" * 30)
    print("Если все тесты прошли успешно, система готова к работе!")
    print("Запустите: python main.py --once")

if __name__ == "__main__":
    test_system()
