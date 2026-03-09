#!/usr/bin/env python3
"""
Локальный тест фильтров тендеров без сетевых запросов
"""

import logging
import sys
import os

# Настройка логирования для теста
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s: %(message)s',
    handlers=[logging.StreamHandler()]
)

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Импортируем только необходимые модули
from config import FILTER_CONFIG

# Копируем функцию фильтрации напрямую для тестирования
def filter_tenders_test(tenders, filters):
    """Тестовая версия функции фильтрации с DEBUG логированием"""
    if not filters:
        return tenders
        
    filtered = []
    logging.info(f"ОТЛАДКА ФИЛЬТРОВ: Начинаем фильтрацию {len(tenders)} тендеров")
    logging.debug(f"Начинаем фильтрацию {len(tenders)} тендеров")
    
    for i, tender in enumerate(tenders):
        logging.debug(f"Фильтруем тендер {i+1}: {tender.get('title', 'Без названия')[:50]}...")
        
        # Фильтр по ключевым словам
        if filters.get('keywords'):
            title_lower = tender.get('title', '').lower()
            description_lower = tender.get('description', '').lower()
            
            keyword_found = False
            for keyword in filters['keywords']:
                if keyword.lower() in title_lower or keyword.lower() in description_lower:
                    keyword_found = True
                    logging.debug(f"Найдено ключевое слово '{keyword}' в тендере")
                    break
            
            if not keyword_found:
                logging.debug(f"Тендер отклонен: не найдены ключевые слова в '{title_lower[:50]}...'")
                continue
            else:
                logging.debug(f"Тендер прошел фильтр ключевых слов")
        
        # Фильтр по исключающим словам
        if filters.get('exclude_keywords'):
            title_lower = tender.get('title', '').lower()
            description_lower = tender.get('description', '').lower()
            
            exclude_found = False
            for exclude_word in filters['exclude_keywords']:
                if exclude_word.lower() in title_lower or exclude_word.lower() in description_lower:
                    exclude_found = True
                    logging.debug(f"Найдено исключающее слово '{exclude_word}' в тендере")
                    break
            
            if exclude_found:
                logging.debug(f"Тендер отклонен: найдено исключающее слово")
                continue
            else:
                logging.debug(f"Тендер прошел фильтр исключающих слов")
        
        # Фильтр по статусу
        if filters.get('exclude_statuses'):
            tender_status = tender.get('status', '')
            if tender_status in filters['exclude_statuses']:
                logging.debug(f"Тендер отклонен: статус '{tender_status}' в списке исключений")
                continue
            else:
                logging.debug(f"Тендер прошел фильтр статусов")
        
        # Если дошли до сюда - тендер прошел все фильтры
        logging.debug(f"Тендер '{tender.get('title', '')[:30]}...' ПРИНЯТ")
        filtered.append(tender)
    
    logging.info(f"Результат фильтрации: принято {len(filtered)} из {len(tenders)} тендеров")
    return filtered

def main():
    print("=== Тест локальной фильтрации тендеров ===")
    
    # Создаем тестовые тендеры
    test_tenders = [
        {
            'tender_id': 'test_001',
            'title': 'Поставка грамот и дипломов почетных',
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
        },
        {
            'tender_id': 'test_004',
            'title': 'Поставка канцелярских товаров',
            'description': 'Закупка ручек, карандашей и других принадлежностей',
            'price': '15000',
            'status': 'Подача заявок',
            'deadline': '2025-09-30',
            'platform': 'test'
        }
    ]
    
    print(f"Количество тестовых тендеров: {len(test_tenders)}")
    print("Тендеры:")
    for tender in test_tenders:
        print(f"  - {tender['tender_id']}: {tender['title']} (статус: {tender['status']})")
    
    print(f"\nКлючевые слова из конфига: {len(FILTER_CONFIG.get('keywords', []))} шт.")
    print(f"Первые 5: {FILTER_CONFIG.get('keywords', [])[:5]}")
    
    print(f"Исключающие слова: {FILTER_CONFIG.get('exclude_keywords', [])}")
    print(f"Исключаемые статусы: {FILTER_CONFIG.get('exclude_statuses', [])}")
    
    print("\n" + "="*50)
    print("ЗАПУСК ФИЛЬТРАЦИИ С DEBUG ЛОГИРОВАНИЕМ:")
    print("="*50)
    
    # Применяем фильтры
    filtered_tenders = filter_tenders_test(test_tenders, FILTER_CONFIG)
    
    print("="*50)
    print(f"ИТОГ: {len(filtered_tenders)} тендеров прошли фильтрацию из {len(test_tenders)}")
    
    if filtered_tenders:
        print("Принятые тендеры:")
        for tender in filtered_tenders:
            print(f"  + {tender['tender_id']}: {tender['title']}")
    else:
        print("Все тендеры были отфильтрованы!")

if __name__ == '__main__':
    main()
