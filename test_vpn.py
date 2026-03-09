"""
Тест доступности сайтов с VPN и без
"""

import requests
import time

def test_site_access():
    print("🌐 ТЕСТ ДОСТУПНОСТИ САЙТОВ")
    print("=" * 40)
    
    sites_to_test = [
        "https://zakupki.gov.ru/",
        "https://zakupki.gov.ru/rss/purchase.xml", 
        "https://supplier.gov.ru/",
        "https://httpbin.org/get"  # Контрольный сайт
    ]
    
    for site in sites_to_test:
        print(f"\n🔍 Проверяю: {site}")
        
        try:
            start_time = time.time()
            response = requests.get(site, timeout=15, verify=False)
            end_time = time.time()
            
            if response.status_code == 200:
                print(f"✅ Доступен (время: {end_time - start_time:.1f}с)")
            else:
                print(f"⚠️ HTTP {response.status_code} (время: {end_time - start_time:.1f}с)")
                
        except requests.exceptions.Timeout:
            print(f"❌ Таймаут (>15с)")
        except requests.exceptions.ConnectionError:
            print(f"❌ Ошибка соединения")
        except Exception as e:
            print(f"❌ Ошибка: {e}")
    
    print("\n" + "=" * 40)
    print("💡 РЕКОМЕНДАЦИИ:")
    print("- Если zakupki.gov.ru недоступен - попробуйте отключить VPN")
    print("- Если httpbin.org недоступен - проверьте интернет-соединение")
    print("- RSS может работать лучше основного сайта")

if __name__ == "__main__":
    test_site_access()
