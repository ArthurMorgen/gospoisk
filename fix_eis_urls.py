"""
Поиск рабочих URL для ЕИС
"""

import requests
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning
disable_warnings(InsecureRequestWarning)

def test_eis_urls():
    print("🔍 ПОИСК РАБОЧИХ URL ЕИС")
    print("=" * 40)
    
    # Возможные URL для тестирования
    urls_to_test = [
        "https://zakupki.gov.ru/",
        "https://zakupki.gov.ru/epz/order/search/results.html",
        "https://zakupki.gov.ru/epz/order/quicksearch/search.html", 
        "https://zakupki.gov.ru/epz/order/extendedsearch/results.html",
        "https://zakupki.gov.ru/rss/",
        "https://zakupki.gov.ru/rss/purchase.xml",
        "https://zakupki.gov.ru/rss/notification.xml",
        "https://zakupki.gov.ru/rss/contract.xml",
        "https://zakupki.gov.ru/223/purchase/public/purchase/info/common-info.html",
    ]
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })
    
    working_urls = []
    
    for url in urls_to_test:
        try:
            print(f"\n🔍 Тестируем: {url}")
            response = session.get(url, timeout=15, verify=False, allow_redirects=True)
            
            if response.status_code == 200:
                print(f"✅ РАБОТАЕТ! ({len(response.text)} байт)")
                working_urls.append(url)
                
                # Проверяем содержимое
                content_type = response.headers.get('content-type', '')
                if 'xml' in content_type:
                    print(f"   📄 XML фид")
                elif 'html' in content_type:
                    print(f"   🌐 HTML страница")
                    
            elif response.status_code == 302 or response.status_code == 301:
                print(f"➡️ Редирект: {response.headers.get('Location', 'неизвестно')}")
            else:
                print(f"❌ HTTP {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"⏱️ Таймаут")
        except Exception as e:
            print(f"❌ Ошибка: {e}")
    
    print(f"\n" + "=" * 40)
    print(f"✅ РАБОЧИЕ URL ({len(working_urls)}):")
    for url in working_urls:
        print(f"  - {url}")
        
    if not working_urls:
        print("❌ НИ ОДИН URL НЕ РАБОТАЕТ!")
        print("💡 Возможно нужна авторизация или сайт изменился")
    
    return working_urls

if __name__ == "__main__":
    working_urls = test_eis_urls()
