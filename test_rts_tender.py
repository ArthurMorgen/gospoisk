"""
Тестовый скрипт для парсера РТС-Тендер
Создает файл debug_rts_tender.html для анализа структуры страницы
"""

import sys
import logging
from parsers.rts_tender_parser import RTSTenderParser
from config import PLATFORMS, FILTER_CONFIG

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('test_rts_tender.log', encoding='utf-8')
    ]
)

def main():
    """Тестирование парсера РТС-Тендер"""
    
    print("="*60)
    print("ТЕСТ ПАРСЕРА РТС-ТЕНДЕР")
    print("="*60)
    
    # Конфигурация парсера
    config = PLATFORMS['rts_tender']
    keywords = FILTER_CONFIG['keywords'][:10]  # Берем первые 10 ключевых слов
    
    print(f"\n📋 Конфигурация:")
    print(f"   URL: {config['search_url']}")
    print(f"   Ключевые слова: {', '.join(keywords[:5])}...")
    
    # Создаем парсер
    print(f"\n🔧 Инициализация парсера...")
    parser = RTSTenderParser(config)
    
    # Пробуем получить страницу
    print(f"\n🌐 Попытка загрузить страницу...")
    print(f"   (Сохранится в debug_rts_tender.html)")
    
    try:
        tenders = parser.search_tenders(keywords, max_results=10)
        
        print(f"\n✅ РЕЗУЛЬТАТ:")
        print(f"   Найдено тендеров: {len(tenders)}")
        
        if tenders:
            print(f"\n📊 Первые результаты:")
            for i, tender in enumerate(tenders[:3], 1):
                print(f"\n   {i}. {tender.get('title', 'Без названия')}")
                print(f"      URL: {tender.get('url', 'Нет URL')}")
                print(f"      Цена: {tender.get('price', 0)}")
        else:
            print(f"\n⚠️ ТЕНДЕРЫ НЕ НАЙДЕНЫ")
            print(f"\n📝 СЛЕДУЮЩИЕ ШАГИ:")
            print(f"   1. Откройте debug_rts_tender.html в браузере")
            print(f"   2. Если страница пустая или показывает защиту:")
            print(f"      - Откройте {config['search_url']} в браузере")
            print(f"      - Нажмите Ctrl+S и сохраните как HTML")
            print(f"      - Переименуйте файл в debug_rts_tender.html")
            print(f"   3. Найдите в HTML элементы карточек тендеров")
            print(f"   4. Обновите селекторы в rts_tender_parser.py")
            
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        logging.error(f"Ошибка теста: {e}", exc_info=True)
    
    print(f"\n" + "="*60)
    print("ТЕСТ ЗАВЕРШЕН")
    print("="*60)

if __name__ == '__main__':
    main()
