#!/usr/bin/env python3
"""
Тест импорта модулей парсеров
"""

try:
    print("Тестирование импортов...")
    
    print("1. Импорт базового парсера...")
    from parsers.base_parser import BaseParser
    print("✓ BaseParser импортирован успешно")
    
    print("2. Импорт парсера ЕИС...")
    from parsers.eis_parser import EISParser
    print("✓ EISParser импортирован успешно")
    
    print("3. Импорт парсера портала поставщиков...")
    from parsers.suppliers_portal_parser import SuppliersPortalParser
    print("✓ SuppliersPortalParser импортирован успешно")
    
    print("4. Импорт через __init__.py...")
    from parsers import EISParser, SuppliersPortalParser
    print("✓ Импорт через __init__.py успешен")
    
    print("\nВсе импорты прошли успешно!")
    
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"❌ Неожиданная ошибка: {e}")
    import traceback
    traceback.print_exc()
