"""
Тестирование API портала поставщиков
"""

import requests
import json

# Возможные API endpoints
endpoints = [
    'https://zakupki.mos.ru/newapi/api/Core/Marketplace/quotationsessions',
    'https://zakupki.mos.ru/api/Cssp/Purchase/Query',
    'https://zakupki.mos.ru/api/Core/Marketplace/quotationsessions',
    'https://zakupki.mos.ru/api/marketplace/quotationsessions',
    'https://zakupki.mos.ru/newapi/api/Cssp/Purchase/Query',
    'https://zakupki.mos.ru/search/api/v1/quotationsessions',
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json',
}

print("Тестирование API endpoints для портала поставщиков...\n")

for i, url in enumerate(endpoints, 1):
    print(f"{i}. Проверяю: {url}")
    
    try:
        # Пробуем GET запрос
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        print(f"   GET: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✅ РАБОТАЕТ! Status: {response.status_code}")
            try:
                data = response.json()
                print(f"   📊 Формат ответа: {type(data)}")
                if isinstance(data, dict):
                    print(f"   🔑 Ключи: {list(data.keys())[:5]}")
                print(f"   💾 Ответ сохранен в test_api_response_{i}.json")
                with open(f'test_api_response_{i}.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            except:
                print(f"   ⚠️  Не JSON: {response.text[:100]}")
        elif response.status_code == 404:
            print(f"   ❌ 404 Not Found")
        else:
            print(f"   ⚠️  Status: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
    
    print()

print("\n✅ Тестирование завершено!")
print("Проверьте файлы test_api_response_*.json для успешных запросов")
