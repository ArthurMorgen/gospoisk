"""
Тестирование парсера РТС-Тендер на загруженном HTML файле
"""

import sys
import logging
from parsers.rts_tender_parser import RTSTenderParser
from config import PLATFORMS

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

def main():
    """Тестирование парсера на готовом HTML"""
    
    print("="*70)
    print("ТЕСТ ПАРСЕРА РТС-ТЕНДЕР (ИЗ ФАЙЛА)")
    print("="*70)
    
    # Читаем HTML файл
    html_file = 'debug_rts_tender.html'
    
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        print(f"\n✓ HTML файл загружен: {html_file}")
        print(f"  Размер: {len(html_content)} символов")
    except FileNotFoundError:
        print(f"\n✗ ОШИБКА: Файл {html_file} не найден!")
        print(f"  Пожалуйста, сохраните страницу как {html_file}")
        return
    
    # Создаем парсер
    config = PLATFORMS['rts_tender']
    parser = RTSTenderParser(config)
    
    print(f"\n🔍 Парсинг HTML...")
    
    # Парсим HTML
    tenders = parser._parse_search_results(html_content)
    
    print(f"\n{'='*70}")
    print(f"РЕЗУЛЬТАТЫ:")
    print(f"{'='*70}")
    print(f"\n✅ Найдено тендеров: {len(tenders)}")
    
    if tenders:
        print(f"\n{'='*70}")
        print("ДЕТАЛИ ТЕНДЕРОВ:")
        print(f"{'='*70}\n")
        
        for i, tender in enumerate(tenders, 1):
            print(f"📋 ТЕНДЕР #{i}")
            print(f"   Название: {tender['title']}")
            print(f"   URL: {tender['url']}")
            print(f"   Цена: {tender['price']:,.2f} ₽")
            print(f"   Заказчик: {tender['customer'][:60]}..." if len(tender['customer']) > 60 else f"   Заказчик: {tender['customer']}")
            print(f"   Дедлайн: {tender['deadline']}")
            print(f"   Статус: {tender['status']}")
            print(f"   ID: {tender['tender_id']}")
            if tender.get('eis_number'):
                print(f"   Номер ЕИС: {tender['eis_number']}")
            print()
    else:
        print(f"\n⚠️ ТЕНДЕРЫ НЕ НАЙДЕНЫ")
        print(f"\nВозможные причины:")
        print(f"  1. HTML файл содержит Anti-DDoS защиту")
        print(f"  2. Неправильные селекторы")
        print(f"  3. Страница без результатов")
    
    print(f"{'='*70}")
    print("ТЕСТ ЗАВЕРШЕН")
    print(f"{'='*70}")

if __name__ == '__main__':
    main()
