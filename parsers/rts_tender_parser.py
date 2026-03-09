"""
Парсер для РТС-Тендер (www.rts-tender.ru)
Электронная торговая площадка для закупок по 44-ФЗ и 223-ФЗ

Использует Selenium для обхода Anti-DDoS защиты
"""

import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Optional
import time
import json
import os

# Selenium для обхода Anti-DDoS
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    logging.warning("⚠️ Selenium не установлен. Используется fallback на сохраненный HTML")

class RTSTenderParser:
    """Парсер для площадки РТС-Тендер"""
    
    def __init__(self, config: dict):
        """
        Инициализация парсера
        
        Args:
            config: Конфигурация парсера из config.py
        """
        self.config = config
        self.base_url = config.get('base_url', 'https://www.rts-tender.ru')
        self.search_url = config.get('search_url', 'https://www.rts-tender.ru/poisk/poisk-44-fz/')
        self.timeout = config.get('timeout', 30)
        self.use_selenium = config.get('use_selenium', True) and SELENIUM_AVAILABLE
        
        logging.info(f"RTSTenderParser инициализирован (Selenium: {'✓' if self.use_selenium else '✗'})")
    
    def search_tenders(self, keywords: List[str], max_results: int = 50) -> List[Dict]:
        """
        Поиск тендеров по ключевым словам
        
        Args:
            keywords: Список ключевых слов для поиска
            max_results: Максимальное количество результатов
            
        Returns:
            Список найденных тендеров
        """
        logging.info(f"🔍 РТС-Тендер: Поиск тендеров по ключевым словам...")
        
        tenders = []
        html_content = None
        
        # Пока одно слово для отладки
        all_keywords = 'грамота'
        
        logging.info(f"📋 Поиск по слову: {all_keywords}")
        search_url = f"{self.search_url}?searchString={all_keywords}"
        
        html_content = None
        
        # 1️⃣ Попытка через Selenium (с прокруткой до конца)
        if self.use_selenium:
            html_content = self._get_html_with_selenium(search_url)
        
        # 2️⃣ Fallback на сохраненный HTML
        if not html_content:
            html_content = self._get_saved_html()
        
        # 3️⃣ Парсим HTML
        if html_content:
            tenders = self._parse_search_results(html_content)
            logging.info(f"✓ Найдено тендеров: {len(tenders)}")
        else:
            logging.error("✗ Не удалось получить HTML")
        
        return tenders[:max_results]
    
    def _get_html_with_selenium(self, url: str) -> Optional[str]:
        """
        Получение HTML через Selenium для обхода Anti-DDoS
        
        Args:
            url: URL для загрузки
            
        Returns:
            HTML контент или None
        """
        driver = None
        try:
            logging.info("🌐 Запуск Chrome для обхода Anti-DDoS...")
            
            # Настройка Chrome
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # Для работы на сервере без GUI
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--remote-debugging-port=9222')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_argument('--start-maximized')
            chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # User-Agent
            chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # Запуск браузера
            driver = webdriver.Chrome(options=chrome_options)
            
            # Маскировка автоматизации
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                    Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                    Object.defineProperty(navigator, 'languages', {get: () => ['ru-RU', 'ru', 'en-US', 'en']});
                    window.chrome = {runtime: {}};
                '''
            })
            
            # Загружаем страницу поиска
            base_search_url = self.search_url.split('?')[0]  # Убираем параметры
            logging.info(f"📄 Загрузка страницы: {base_search_url}")
            driver.get(base_search_url)
            
            # Ждем загрузки страницы + Anti-DDoS проверку (5-7 секунд)
            logging.info("⏳ Ожидание Anti-DDoS проверки...")
            time.sleep(7)
            
            # Ищем поле поиска и вводим текст
            try:
                # Извлекаем поисковый запрос из URL
                search_query = url.split('searchString=')[-1] if 'searchString=' in url else ''
                if search_query:
                    logging.info(f"🔍 Ввод поискового запроса: {search_query}")
                    
                    # Находим поле поиска - ищем ВСЕ input поля
                    search_input = None
                    
                    # Сначала пробуем известные селекторы
                    selectors = [
                        'input[name="searchString"]',
                        'input[id="searchString"]',
                        'input[type="search"]',
                        'input.search-input',
                        'input#searchString',
                        '#search-input',
                        'input[placeholder*="Поиск"]',
                        'input[placeholder*="поиск"]'
                    ]
                    
                    for selector in selectors:
                        try:
                            search_input = driver.find_element(By.CSS_SELECTOR, selector)
                            logging.info(f"✓ Найдено поле поиска: {selector}")
                            break
                        except:
                            continue
                    
                    # Если не нашли - ищем ВСЕ видимые input[type="text"]
                    if not search_input:
                        try:
                            all_inputs = driver.find_elements(By.CSS_SELECTOR, 'input[type="text"]')
                            # Берем первый видимый input
                            for inp in all_inputs:
                                if inp.is_displayed():
                                    search_input = inp
                                    logging.info(f"✓ Найдено текстовое поле (первое видимое)")
                                    break
                        except:
                            pass
                    
                    if search_input:
                        # Очищаем поле
                        search_input.clear()
                        
                        # Вводим каждое слово отдельно через Enter (теги)
                        words = search_query.split()
                        from selenium.webdriver.common.keys import Keys
                        
                        for word in words:
                            search_input.send_keys(word)
                            search_input.send_keys(Keys.RETURN)
                            time.sleep(0.3)  # Небольшая пауза между тегами
                        
                        logging.info(f"✓ Введено {len(words)} тегов в поле поиска")
                        
                        # Ищем кнопку поиска через XPath (по тексту)
                        button_found = False
                        
                        # Пробуем найти по тексту через XPath
                        xpath_selectors = [
                            "//button[contains(text(), 'Найти')]",
                            "//button[contains(text(), 'найти')]",
                            "//button[contains(text(), 'Поиск')]",
                            "//button[contains(text(), 'поиск')]",
                            "//input[@type='submit']",
                            "//button[@type='submit']",
                            "//a[contains(@class, 'search')]",
                            "//button[contains(@class, 'search')]"
                        ]
                        
                        for xpath in xpath_selectors:
                            try:
                                search_button = driver.find_element(By.XPATH, xpath)
                                if search_button.is_displayed():
                                    # Пробуем обычный клик
                                    try:
                                        search_button.click()
                                        logging.info(f"✓ Нажата кнопка поиска (обычный клик): {xpath}")
                                        button_found = True
                                    except:
                                        # Если не работает - JavaScript клик
                                        driver.execute_script("arguments[0].click();", search_button)
                                        logging.info(f"✓ Нажата кнопка поиска (JS клик): {xpath}")
                                        button_found = True
                                    
                                    time.sleep(5)
                                    break
                            except:
                                continue
                        
                        if not button_found:
                            # Теги уже введены с Enter, просто ждем
                            logging.info("⚠️ Кнопка не найдена, теги введены")
                            time.sleep(5)
                    else:
                        logging.warning("⚠️ Не найдено поле поиска, используем URL параметры")
            except Exception as e:
                logging.warning(f"⚠️ Не удалось ввести поисковый запрос: {e}")
            
            # Ждем загрузки карточек тендеров (до 45 секунд)
            try:
                WebDriverWait(driver, 45).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'card-item'))
                )
                logging.info("✓ Первые карточки загружены")
                
                # МНОГОКРАТНЫЙ скролл до самого конца - загружаем ВСЕ карточки
                prev_count = 0
                max_scrolls = 20  # Максимум 20 прокруток (защита от бесконечного цикла)
                
                for scroll_num in range(max_scrolls):
                    # Считаем текущее количество карточек
                    current_cards = driver.find_elements(By.CLASS_NAME, 'card-item')
                    current_count = len(current_cards)
                    
                    logging.info(f"  Прокрутка {scroll_num + 1}: {current_count} карточек")
                    
                    # Если новых карточек не появилось - достигли конца
                    if current_count == prev_count and scroll_num > 0:
                        logging.info(f"✓ Все карточки загружены: {current_count}")
                        break
                    
                    prev_count = current_count
                    
                    # Скроллим вниз
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)  # Ждем подгрузки новых карточек
                
            except Exception as e:
                logging.warning(f"⚠️ Ошибка загрузки карточек: {e}")
            
            # Получаем HTML
            html_content = driver.page_source
            
            # Сохраняем для отладки
            with open('debug_rts_tender.html', 'w', encoding='utf-8') as f:
                f.write(html_content)
            logging.info("✓ HTML сохранен в debug_rts_tender.html")
            
            # Проверяем что это не Anti-DDoS
            if 'Anti-DDoS' in html_content:
                logging.error("✗ Selenium тоже получил Anti-DDoS защиту")
                return None
            
            return html_content
            
        except Exception as e:
            logging.error(f"✗ Ошибка Selenium: {e}")
            return None
            
        finally:
            if driver:
                driver.quit()
                logging.debug("Chrome закрыт")
    
    def _get_saved_html(self) -> Optional[str]:
        """
        Получение сохраненного HTML (запасной вариант)
        
        Returns:
            HTML контент или None
        """
        html_file = self.config.get('html_file', 'debug_rts_tender.html')
        
        if not os.path.exists(html_file):
            logging.warning(f"⚠️ Файл {html_file} не найден")
            return None
        
        try:
            logging.info(f"💾 Использую сохраненный HTML: {html_file}")
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Проверяем что это не Anti-DDoS
            if 'Anti-DDoS' in html_content:
                logging.error(f"✗ Файл {html_file} содержит Anti-DDoS защиту")
                return None
            
            return html_content
            
        except Exception as e:
            logging.error(f"✗ Ошибка чтения файла: {e}")
            return None
    
    def _parse_search_results(self, html: str) -> List[Dict]:
        """
        Парсинг результатов поиска
        
        Args:
            html: HTML страницы с результатами
            
        Returns:
            Список тендеров
        """
        tenders = []
        soup = BeautifulSoup(html, 'html.parser')
        
        # Селектор для карточек тендеров на RTS-Tender
        tender_cards = soup.select('div.card-item')
        
        if not tender_cards:
            logging.warning("⚠️ Не найдено карточек тендеров")
            # Проверяем есть ли сообщение о результатах
            result_message = soup.select_one('h4.cards')
            if result_message:
                logging.info(f"Сообщение на странице: {result_message.get_text(strip=True)}")
            return tenders
        
        logging.info(f"✓ Найдено {len(tender_cards)} карточек тендеров")
        
        for i, card in enumerate(tender_cards, 1):
            try:
                tender = self._parse_tender_card(card)
                if tender:
                    tenders.append(tender)
                    logging.debug(f"  [{i}/{len(tender_cards)}] ✓ {tender['title'][:50]}...")
                else:
                    logging.debug(f"  [{i}/{len(tender_cards)}] ✗ Пропущена")
            except Exception as e:
                logging.error(f"  [{i}/{len(tender_cards)}] ✗ Ошибка: {e}")
                continue
        
        return tenders
    
    def _parse_tender_card(self, card) -> Optional[Dict]:
        """
        Парсинг одной карточки тендера
        
        Args:
            card: BeautifulSoup элемент карточки
            
        Returns:
            Словарь с данными тендера или None
        """
        try:
            # Тип закупки (из plate__item)
            tender_type = ''
            plate_items = card.select('span.plate__item')
            for item in plate_items:
                text = item.get_text(strip=True).upper()
                if any(keyword in text for keyword in ['АУКЦИОН', 'КОТИРОВК', 'КОНКУРС', 'ПРЕДЛОЖЕН', 'ЗАПРОС']):
                    tender_type = item.get_text(strip=True)
                    break
            
            # Название тендера
            title_elem = card.select_one('div.card-item__title')
            if not title_elem:
                return None
            title = title_elem.get_text(strip=True)
            
            # URL на детальную страницу
            url_elem = card.select_one('a.button-red[href*="/poisk/id/"]')
            if not url_elem:
                return None
            url = url_elem.get('href', '')
            if url and not url.startswith('http'):
                url = f"{self.base_url}{url}"
            
            # ID тендера из URL
            tender_id = ''
            if '/poisk/id/' in url:
                tender_id = url.split('/poisk/id/')[-1].rstrip('/')
            
            # Цена (начальная максимальная цена контракта)
            price_value = 0.0
            price_elem = card.select_one('div.card-item__properties-desc[itemprop="price"]')
            if price_elem:
                price_text = price_elem.get('content', '') or price_elem.get_text(strip=True)
                # Убираем все кроме цифр и точки
                price_text = ''.join(c for c in price_text if c.isdigit() or c == '.')
                try:
                    price_value = float(price_text)
                except ValueError:
                    pass
            
            # Статус
            status = ''
            status_cells = card.select('div.card-item__properties-cell')
            for cell in status_cells:
                name_elem = cell.select_one('div.card-item__properties-name')
                if name_elem and 'СТАТУС' in name_elem.get_text(strip=True).upper():
                    desc_elem = cell.select_one('div.card-item__properties-desc')
                    if desc_elem:
                        status = desc_elem.get_text(strip=True)
                    break
            
            # Дедлайн (окончание подачи заявок)
            deadline = ''
            deadline_elem = card.select_one('div.card-item__info-end-date time')
            if deadline_elem:
                # Берем из атрибута datetime
                deadline_datetime = deadline_elem.get('datetime', '')
                if deadline_datetime:
                    # Формат: "08.12.2025 02:00:00 +03:00"
                    try:
                        # Парсим дату
                        from datetime import datetime
                        deadline_dt = datetime.strptime(deadline_datetime.split(' +')[0], '%d.%m.%Y %H:%M:%S')
                        deadline = deadline_dt.strftime('%d.%m.%Y %H:%M')
                    except:
                        # Если не удалось распарсить, берем текст
                        deadline = deadline_elem.get_text(strip=True)
                else:
                    deadline = deadline_elem.get_text(strip=True)
            
            # Организатор (заказчик)
            customer = ''
            customer_elem = card.select_one('div.card-item__organization-main a.text--bold')
            if customer_elem:
                customer = customer_elem.get_text(strip=True).replace('(все закупки)', '').strip()
            
            # Номер в ЕИС (если есть)
            eis_number = ''
            eis_link = card.select_one('a[href*="zakupki.gov.ru"]')
            if eis_link:
                href = eis_link.get('href', '')
                if 'regNumber=' in href:
                    eis_number = href.split('regNumber=')[-1]
            
            tender_data = {
                'title': title,
                'url': url,
                'price': price_value,
                'customer': customer,
                'deadline': deadline,
                'status': status,
                'platform': 'РТС-Тендер',
                'tender_id': tender_id,
                'eis_number': eis_number,
                'tender_type': tender_type  # Тип закупки
            }
            
            return tender_data
            
        except Exception as e:
            logging.error(f"Ошибка парсинга карточки тендера: {e}")
            return None
    
    def get_tender_details(self, tender_url: str) -> Optional[Dict]:
        """
        Получение детальной информации о тендере
        
        Args:
            tender_url: URL страницы тендера
            
        Returns:
            Словарь с детальной информацией
        """
        try:
            response = self.session.get(tender_url, timeout=self.timeout)
            
            if response.status_code == 200:
                return self._parse_tender_details(response.text)
            else:
                logging.error(f"Ошибка загрузки деталей: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            logging.error(f"Ошибка получения деталей тендера: {e}")
            return None
    
    def _parse_tender_details(self, html: str) -> Dict:
        """
        Парсинг детальной страницы тендера
        
        Args:
            html: HTML страницы тендера
            
        Returns:
            Словарь с детальной информацией
        """
        # TODO: Реализовать после анализа HTML
        return {}
