#!/usr/bin/env python3

import logging
import sys
import os

# Настройка логирования
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from config import FILTER_CONFIG
    from parsers.base_parser import BaseParser
    
    print("Модули успешно импортированы")
    
    # Создаем тестовый парсер
    class TestParser(BaseParser):
        def __init__(self):
            super().__init__({'name': 'Test', 'base_url': 'http://test.com'})
    
    # Тестовые тендеры
    test_tenders = [
        {
            'tender_id': 'test_001',
            'title': 'Поставка грамот и дипломов',
            'description': 'Изготовление благодарственных грамот',
            'price': '50000',
            'status': 'Подача заявок',
            'deadline': '2025-09-20',
            'platform': 'test'
        }
    ]
    
    print(f"Тестовых тендеров: {len(test_tenders)}")
    print(f"Ключевые слова из конфига: {FILTER_CONFIG.get('keywords', [])[:5]}...")
    
    parser = TestParser()
    print("Парсер создан")
    
    # Тестируем фильтрацию
    print("\nЗапуск фильтрации...")
    filtered = parser.filter_tenders(test_tenders, FILTER_CONFIG)
    print(f"Результат фильтрации: {len(filtered)} тендеров")
    
except Exception as e:
    print(f"Ошибка: {e}")
    import traceback
    traceback.print_exc()
