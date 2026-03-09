#!/usr/bin/env python3
"""
Тест DEBUG логирования фильтров тендеров
"""

import sys
import os
import logging

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import LOGGING_CONFIG, FILTER_CONFIG
from parsers.base_parser import BaseParser

def setup_logging():
    """Настройка логирования"""
    logging.basicConfig(
        level=logging.DEBUG,  # Явно устанавливаем DEBUG
        format='%(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()  # Только в консоль для теста
        ]
    )
    
    # Дополнительная проверка
    logging.debug("DEBUG логирование активировано")

def test_filter_tenders():
    """Тестирование фильтрации тендеров с DEBUG логированием"""
    
    # Создаем тестовые тендеры
    test_tenders = [
        {
            'tender_id': 'test_001',
            'title': 'Поставка грамот и дипломов',
            'description': 'Изготовление благодарственных грамот для награждения сотрудников',
            'price': '50000',
            'status': 'Подача заявок',
            'deadline': '2025-09-20',
            'platform': 'test'
        },
        {
            'tender_id': 'test_002', 
            'title': 'Ремонт дорог в городе',
            'description': 'Капитальный ремонт дорожного покрытия',
            'price': '1000000',
            'status': 'Подача заявок',
            'deadline': '2025-09-25',
            'platform': 'test'
        },
        {
            'tender_id': 'test_003',
            'title': 'Изготовление сертификатов',
            'description': 'Печать сертификатов об окончании курсов',
            'price': '25000',
            'status': 'Завершен',
            'deadline': '2025-08-15',
            'platform': 'test'
        }
    ]
    
    # Создаем экземпляр базового парсера для тестирования
    class TestParser(BaseParser):
        def __init__(self):
            super().__init__({'name': 'Test Parser', 'base_url': 'http://test.com'})
    
    parser = TestParser()
    
    print("Тестирование фильтрации тендеров...")
    print(f"Количество тестовых тендеров: {len(test_tenders)}")
    print("\nТендеры до фильтрации:")
    for tender in test_tenders:
        print(f"- {tender['tender_id']}: {tender['title']} (статус: {tender['status']})")
    
    # Применяем фильтры
    filtered_tenders = parser.filter_tenders(test_tenders, FILTER_CONFIG)
    
    print(f"\nКоличество тендеров после фильтрации: {len(filtered_tenders)}")
    print("Тендеры после фильтрации:")
    for tender in filtered_tenders:
        print(f"- {tender['tender_id']}: {tender['title']}")

if __name__ == '__main__':
    setup_logging()
    test_filter_tenders()
