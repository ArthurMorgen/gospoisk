"""
Парсер площадки Росэлторг (roseltorg.ru)
Использует Selenium для работы с динамическим контентом

Оптимизированная версия для сервера:
- Headless режим
- Минимальные таймауты
- Полный список ключевых слов
"""

import logging
import time
import re
from typing import List, Dict, Optional
from datetime import datetime
from bs4 import BeautifulSoup

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False


class RoseltorgParser:
    """Парсер для площадки Росэлторг"""
    
    def __init__(self):
        self.base_url = 'https://www.roseltorg.ru'
        self.search_url = 'https://www.roseltorg.ru/procedures/search?source%5B%5D=1&place=44fz'
        self.selenium_available = SELENIUM_AVAILABLE
        logging.info(f"RoseltorgParser инициализирован (Selenium: {'✓' if SELENIUM_AVAILABLE else '✗'})")
    
    def search_tenders(self, keywords: List[str] = None) -> List[Dict]:
        """Поиск тендеров"""
        if not self.selenium_available:
            logging.error("Selenium не установлен!")
            return []
        
        all_tenders = []
        seen_ids = set()
        
        # Полный список ключевых слов
        search_keywords = [
            'журналы',
            'бланки',
            'грамоты',
            'дипломы',
            'благодарственные письма',
            'благодарности',
            'полиграфическая продукция',
            'типографическая продукция',
            'бумажная продукция'
        ]
        
        # Создаем один браузер для всех поисков
        driver = self._create_driver()
        if not driver:
            return []
        
        try:
            for search_word in search_keywords:
                try:
                    logging.info(f"🔍 Росэлторг: Поиск по '{search_word}'...")
                    tenders = self._search_with_driver(driver, search_word)
                    for t in tenders:
                        if t['tender_id'] not in seen_ids:
                            seen_ids.add(t['tender_id'])
                            all_tenders.append(t)
                except Exception as e:
                    logging.error(f"Ошибка поиска '{search_word}': {e}")
        finally:
            try:
                driver.quit()
            except:
                pass
        
        logging.info(f"✓ Всего найдено уникальных тендеров: {len(all_tenders)}")
        return all_tenders
    
    def _create_driver(self, headless: bool = True):
        """Создание драйвера Chrome"""
        try:
            chrome_options = Options()
            
            # Headless режим для сервера
            if headless:
                chrome_options.add_argument('--headless=new')
            
            # Базовые настройки
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-infobars')
            chrome_options.add_argument('--window-size=1920,1080')
            
            # Маскировка автоматизации + отключение логов
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_argument('--log-level=3')
            chrome_options.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            driver = webdriver.Chrome(options=chrome_options)
            driver.set_page_load_timeout(20)
            driver.set_script_timeout(10)
            
            # Маскировка webdriver
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                    Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                    Object.defineProperty(navigator, 'languages', {get: () => ['ru-RU', 'ru', 'en-US', 'en']});
                    window.chrome = {runtime: {}};
                '''
            })
            return driver
        except Exception as e:
            logging.error(f"Ошибка создания драйвера: {e}")
            return None
    
    def _search_with_selenium(self, keyword: str) -> List[Dict]:
        """Поиск с использованием Selenium (создает новый браузер)"""
        driver = self._create_driver()
        if not driver:
            return []
        try:
            return self._search_with_driver(driver, keyword)
        finally:
            try:
                driver.quit()
            except:
                pass
    
    def _search_with_driver(self, driver, keyword: str) -> List[Dict]:
        """Поиск через существующий драйвер"""
        try:
            import urllib.parse
            # URL с параметром поиска
            search_url = f"https://www.roseltorg.ru/procedures/search?query_field={urllib.parse.quote(keyword)}&source%5B%5D=1&place=44fz"
            logging.info(f"🔍 Росэлторг: '{keyword}'")
            driver.get(search_url)
            time.sleep(2)  # Минимальное ожидание
            
            # Закрываем куки баннер
            try:
                cookie_btns = driver.find_elements(By.XPATH, 
                    "//button[contains(text(),'Принять') or contains(text(),'OK')]")
                if cookie_btns:
                    cookie_btns[0].click()
            except:
                pass
            
            # Прокрутка для загрузки всего контента
            try:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(0.3)
            except:
                pass
            
            # Парсим HTML
            tenders = self._parse_search_results(driver.page_source)
            return tenders
            
        except Exception as e:
            logging.error(f"✗ Ошибка поиска '{keyword}': {e}")
            return []
    
    def _parse_search_results(self, html: str) -> List[Dict]:
        """Парсинг HTML результатов поиска"""
        soup = BeautifulSoup(html, 'html.parser')
        tenders = []
        
        # Ищем ссылки на процедуры
        procedure_links = soup.find_all('a', href=lambda h: h and '/procedure/' in h)
        
        # Собираем по ID, выбирая лучшее название
        id_to_data = {}
        
        for link in procedure_links:
            try:
                href = link.get('href', '')
                if not href or '/procedure/' not in href:
                    continue
                
                match = re.search(r'/procedure/(\d+)', href)
                if not match:
                    continue
                    
                tender_id = match.group(1)
                title = link.get_text(strip=True)
                
                # Обновляем если новое название лучше
                if tender_id in id_to_data:
                    old_title = id_to_data[tender_id]['title']
                    if title and len(title) > len(old_title) and not title.isdigit():
                        id_to_data[tender_id]['title'] = title
                else:
                    id_to_data[tender_id] = {'href': href, 'title': title or ''}
            except:
                continue
        
        for tender_id, data in id_to_data.items():
            title = data['title']
            href = data['href']
            
            # Пропускаем пустые/короткие/цифровые названия
            if not title or len(title) < 10 or title.isdigit():
                continue
            
            url = f"{self.base_url}{href}" if href.startswith('/') else href
            
            tenders.append({
                'tender_id': f"roseltorg_{tender_id}",
                'platform': 'roseltorg',
                'title': title,
                'price': 0.0,
                'customer': '',
                'deadline': '',
                'status': 'Активна',
                'url': url,
                'tender_type': '44-ФЗ',
                'parsed_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
        
        logging.info(f"   → найдено {len(tenders)} тендеров")
        return tenders
