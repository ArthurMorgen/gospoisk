"""
Тест исправления URL в парсере ЕИС
"""

import logging
from bs4 import BeautifulSoup

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Читаем сохраненный HTML
with open('debug_eis.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

# Находим все блоки тендеров
tender_rows = soup.select('div.search-registry-entry-block')

print(f"\n{'='*70}")
print(f"ТЕСТ ИЗВЛЕЧЕНИЯ ПРАВИЛЬНЫХ ССЫЛОК НА ТЕНДЕРЫ")
print(f"{'='*70}\n")
print(f"Найдено блоков тендеров: {len(tender_rows)}\n")

for i, row in enumerate(tender_rows[:5], 1):  # Проверяем первые 5
    print(f"\n--- Тендер #{i} ---")
    
    # Название
    purchase_object = row.find('div', string='Объект закупки')
    if purchase_object:
        title_elem = purchase_object.find_next('div', class_='registry-entry__body-value')
        if title_elem:
            title = title_elem.get_text(strip=True)
            print(f"Название: {title[:60]}...")
    
    # Все ссылки в блоке
    all_links = row.find_all('a', href=True)
    print(f"\nВсего ссылок в блоке: {len(all_links)}")
    
    # Ищем правильную ссылку
    correct_link = None
    for link in all_links:
        href = link.get('href', '')
        if '/view/common-info.html' in href and 'regNumber=' in href:
            correct_link = href
            print(f"\n✅ ПРАВИЛЬНАЯ ссылка найдена:")
            print(f"   {href}")
            break
    
    if not correct_link:
        print("\n❌ Правильная ссылка НЕ найдена!")
        print("Все найденные ссылки:")
        for link in all_links[:3]:  # Первые 3 ссылки
            href = link.get('href', '')
            print(f"   - {href}")

print(f"\n{'='*70}")
print("ТЕСТ ЗАВЕРШЕН")
print(f"{'='*70}\n")
