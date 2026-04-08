"""
Парсер для ЕИС (zakupki.gov.ru)
"""

import re
import logging
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse, parse_qs
from datetime import datetime
from .base_parser import BaseParser

class EISParser(BaseParser):
    def __init__(self, platform_config: Dict):
        super().__init__(platform_config)
        self.base_url = platform_config['base_url']
        self.search_url = platform_config['search_url']
    
    def search_tenders(self, keywords: List[str] = None, filters: Dict = None) -> List[Dict]:
        """Поиск тендеров на ЕИС"""
        tenders = []
        
        try:
            # Используем рабочий URL расширенного поиска
            search_url = self.search_url
            
            # Базовые параметры поиска
            search_params = {
                'searchString': '',
                'morphology': 'on',
                'search-filter': 'Дате+размещения',
                'pageNumber': 1,
                'sortDirection': 'false',
                'recordsPerPage': '_50'  # Максимум результатов на странице (было 10)
            }
            
            # Делаем запросы по каждому ключевому слову пользователя
            if keywords and len(keywords) > 0:
                all_tender_rows = []
                
                for idx, search_string in enumerate(keywords, 1):
                    search_params['searchString'] = search_string
                    search_params['fz44'] = 'on'
                    search_params['fz223'] = 'on'
                    search_params['ppRf615'] = 'on'
                    
                    logging.info(f"[{idx}/{len(keywords)}] Поиск тендеров на ЕИС: {search_string}")
                    
                    # Выполняем поиск
                    response = self.make_request(search_url, params=search_params)
                    if not response:
                        logging.warning(f"Не удалось получить ответ от ЕИС для запроса: {search_string}")
                        continue
                    
                    soup = self.parse_html(response.text)
                    
                    # Ищем тендеры в этом ответе
                    possible_selectors = [
                        'div.search-registry-entry-block',
                        'div.registry-entry__form',
                        'div.search-results-item',
                        'div.tender-item',
                        '.registry-entry',
                        'tr.search-results-row'
                    ]
                    
                    tender_rows_found = []
                    for selector in possible_selectors:
                        rows = soup.select(selector)
                        if rows:
                            logging.info(f"Запрос '{search_string}': найдено {len(rows)} тендеров")
                            tender_rows_found = rows
                            break
                    
                    # Добавляем найденные тендеры к общему списку
                    if tender_rows_found:
                        all_tender_rows.extend(tender_rows_found)
                    else:
                        logging.debug(f"Запрос '{search_string}': тендеры не найдены")
                    
                    # Сохраняем последний HTML для отладки
                    with open('debug_eis.html', 'w', encoding='utf-8') as f:
                        f.write(response.text)
                
                logging.info(f"Всего найдено {len(all_tender_rows)} тендеров из {len(keywords)} запросов")
                tender_rows = all_tender_rows
            else:
                # Если нет ключевых слов - делаем один запрос
                response = self.make_request(search_url, params=search_params)
                if not response:
                    logging.warning("Не удалось получить ответ от ЕИС")
                    return tenders
                soup = self.parse_html(response.text)
                tender_rows = []
            
            if not tender_rows:
                logging.warning("Не найдено элементов тендеров ни с одним селектором")
                return tenders
            
            # Убираем дубликаты по ID
            seen_ids = set()
            for row in tender_rows:
                try:
                    tender_data = self._parse_tender_row(row)
                    if tender_data:
                        tender_id = tender_data.get('tender_id')
                        # Пропускаем если уже видели этот ID
                        if tender_id and tender_id in seen_ids:
                            logging.debug(f"Пропускаем дубликат: {tender_id}")
                            continue
                        
                        formatted_tender = self.format_tender_data(tender_data)
                        tenders.append(formatted_tender)
                        
                        if tender_id:
                            seen_ids.add(tender_id)
                        
                except Exception as e:
                    logging.warning(f"Ошибка парсинга строки тендера на ЕИС: {e}")
                    continue
            
            logging.info(f"Найдено {len(tenders)} уникальных тендеров на ЕИС")
            
        except Exception as e:
            logging.error(f"Ошибка парсинга тендера: {e}")
        
        return tenders
    
    def _search_via_rss(self, keywords: List[str] = None) -> List[Dict]:
        """Поиск тендеров через RSS (обходит блокировки VPN)"""
        tenders = []
        
        try:
            # Правильные URL для ЕИС
            rss_urls = [
                "https://zakupki.gov.ru/rss/fz44/published/purchase.xml",
                "https://zakupki.gov.ru/rss/fz223/published/purchase.xml", 
                "https://zakupki.gov.ru/rss/purchased.xml"
            ]
            
            logging.info("Попытка получить данные через RSS ЕИС...")
            
            # Пробуем разные RSS фиды
            for rss_url in rss_urls:
                logging.info(f"Проверяем RSS: {rss_url}")
                response = self.make_request(rss_url)
                
                if response and response.status_code == 200:
                    logging.info(f"Успешно подключились к RSS: {rss_url}")
                    break
            else:
                logging.warning("Ни один RSS фид ЕИС недоступен")
                return tenders
            
            # Парсим RSS как XML
            from xml.etree import ElementTree as ET
            try:
                root = ET.fromstring(response.text)
                items = root.findall('.//item')
                
                for item in items[:10]:  # Берем первые 10
                    try:
                        title = item.find('title').text if item.find('title') is not None else ""
                        raw_link = item.find('link').text if item.find('link') is not None else ""
                        description = item.find('description').text if item.find('description') is not None else ""
                        pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ""
                        
                        # Исправляем и нормализуем ссылку
                        link = self._fix_rss_link(raw_link)
                        
                        logging.info(f"✓ ЕИС RSS: Исправлена ссылка")
                        logging.debug(f"ЕИС RSS: {raw_link} -> {link}")
                        
                        # Фильтруем по ключевым словам
                        if keywords and not any(keyword.lower() in title.lower() or keyword.lower() in description.lower() 
                                              for keyword in keywords[:5]):
                            continue
                        
                        # Получаем правильный ID тендера
                        tender_id = self._extract_tender_id_from_url(link) or f"rss_{len(tenders)}"
                        
                        tender = {
                            'id': tender_id,
                            'title': title,
                            'platform': 'ЕИС',
                            'url': link,
                            'price': None,
                            'currency': 'RUB',
                            'customer': 'Не указан',
                            'deadline': None,
                            'description': description[:200] if description else "",
                            'date_published': pub_date,
                            'status': 'Активный'
                        }
                        
                        tenders.append(tender)
                        
                    except Exception as e:
                        logging.warning(f"Ошибка парсинга RSS элемента: {e}")
                        continue
                        
                logging.info(f"RSS: найдено {len(tenders)} тендеров")
                
            except ET.ParseError as e:
                logging.error(f"Ошибка парсинга RSS XML: {e}")
                
        except Exception as e:
            logging.error(f"Ошибка получения RSS: {e}")
            
        return tenders
    
    def _parse_tender_row(self, row) -> Optional[Dict]:
        """Парсинг строки с информацией о тендере"""
        try:
            # Отладка: показываем что пытаемся парсить
            logging.debug(f"Парсинг строки тендера: {str(row)[:200]}...")
            
            # Ищем НАЗВАНИЕ тендера (НЕ статус процедуры!)
            # Сначала ищем в блоке "Объект закупки" - там настоящее название
            title_elem = None
            
            # Вариант 1: Блок "Объект закупки" - основное место для названия
            purchase_object = row.find('div', string='Объект закупки')
            if purchase_object:
                # Ищем соседний элемент с описанием закупки
                title_elem = purchase_object.find_next('div', class_='registry-entry__body-value')
                if title_elem:
                    logging.debug("Найдено название в блоке 'Объект закупки'")
            
            # Вариант 2: Поиск в разных элементах
            if not title_elem:
                title_elem = (
                    row.find('a', class_='registry-entry__body-value') or
                    row.find('div', class_='registry-entry__body-value') or
                    row.find('div', class_='registry-entry__header-mid__title') or
                    row.find('a', class_='registry-entry__header-mid__title') or
                    row.find('span', class_='registry-entry__body-value') or
                    row.find('a') or
                    row.find('h3') or
                    row.find('h4')
                )
            
            if not title_elem:
                logging.debug("Не найден элемент заголовка")
                return None
            
            # Получаем текст названия тендера
            title = ' '.join(title_elem.get_text(separator=' ', strip=True).split())
            
            # Отфильтровываем статусы процедур 
            status_phrases = [
                'подача заявок', 'определение поставщика завершено',
                'работа комиссии', 'рассмотрение заявок', 'подведение итогов'
            ]
            
            # Если это статус процедуры, пробуем найти реальное название
            if any(phrase in title.lower() for phrase in status_phrases):
                logging.debug(f"Обнаружен статус процедуры: {title[:50]}... Ищем реальное название...")
                
                # Ищем реальное название тендера в других местах
                real_title_selectors = [
                    'div.registry-entry__body-value',
                    'span.registry-entry__body-value', 
                    'a.registry-entry__body-href',
                    'div.registry-entry__body-href',
                    '[class*="subject"]',
                    '[class*="purchase"]',
                    '[class*="object"]'
                ]
                
                for selector in real_title_selectors:
                    real_title_elem = row.select_one(selector)
                    if real_title_elem:
                        potential_title = ' '.join(real_title_elem.get_text(separator=' ', strip=True).split())
                        if (potential_title and len(potential_title) > 10 and 
                            not any(phrase in potential_title.lower() for phrase in status_phrases)):
                            title = potential_title
                            title_elem = real_title_elem
                            logging.info(f"✓ ЕИС: Найдено реальное название (не статус): {title[:50]}...")
                            break
            
            # Получаем ссылку на тендер - ищем ПРАВИЛЬНУЮ ссылку на просмотр
            relative_url = ""
            
            # Ищем ссылку с "/view/common-info.html" - это правильная ссылка на тендер
            all_links = row.find_all('a', href=True)
            for link in all_links:
                href = link.get('href', '')
                # Правильная ссылка содержит /view/common-info.html
                if '/view/common-info.html' in href and 'regNumber=' in href:
                    relative_url = href
                    logging.debug(f"✓ Найдена правильная ссылка на тендер: {href}")
                    break
            
            # Если не нашли правильную ссылку, берем ссылку с regNumber в заголовке
            if not relative_url:
                for link in all_links:
                    href = link.get('href', '')
                    if 'regNumber=' in href and 'printForm' not in href and 'listModal' not in href:
                        relative_url = href
                        logging.debug(f"✓ Найдена альтернативная ссылка: {href}")
                        break
            
            # Если все равно не нашли, берем первую с regNumber
            if not relative_url:
                for link in all_links:
                    href = link.get('href', '')
                    if 'regNumber=' in href:
                        relative_url = href
                        logging.warning(f"⚠ Взята резервная ссылка (может быть неправильной): {href}")
                        break
            
            # Если не нашли правильную ссылку - пропускаем тендер
            if not relative_url or 'regNumber=' not in relative_url:
                logging.warning(f"⚠️ Пропускаем тендер без правильной ссылки: {title[:50]}...")
                return None
            
            full_url = urljoin(self.base_url, relative_url)
            tender_id = self._extract_tender_id_from_url(relative_url)
            
            logging.info(f"✓ ЕИС: Найден тендер: {title[:50]}...")
            logging.info(f"✓ ЕИС: URL: {full_url}")
            logging.debug(f"ЕИС: Полная информация - Title: {title}, URL: {full_url}, ID: {tender_id}")
            
            # Извлекаем цену
            price_elem = row.find('div', class_='price-block__value')
            price_text = price_elem.get_text(strip=True) if price_elem else ''
            
            # Извлекаем заказчика
            customer_elem = row.find('div', class_='registry-entry__body-href')
            customer = ' '.join(customer_elem.get_text(separator=' ', strip=True).split()) if customer_elem else ''
            
            # Извлекаем дату окончания подачи заявок
            # Ищем блок с заголовком "Окончание подачи заявок"
            deadline = ''
            deadline_title = row.find('div', class_='data-block__title', string=lambda text: text and 'Окончание подачи заявок' in text)
            if deadline_title:
                deadline_elem = deadline_title.find_next_sibling('div', class_='data-block__value')
                if deadline_elem:
                    deadline = deadline_elem.get_text(strip=True)
            
            # ФИЛЬТРУЕМ: дата окончания >= СЕГОДНЯ
            if deadline:
                try:
                    # Парсим дату в формате "DD.MM.YYYY"
                    deadline_datetime = datetime.strptime(deadline, "%d.%m.%Y")
                    now = datetime.now()
                    
                    # Сравниваем только ДАТЫ (без времени)
                    # Если дедлайн сегодня или раньше - пропускаем
                    if deadline_datetime.date() <= now.date():
                        logging.debug(f"⏭️  Пропускаем - дедлайн прошел или сегодня: {deadline}")
                        return None
                    
                    logging.debug(f"✓ Активна - дедлайн {deadline}")
                except ValueError:
                    # Если не смогли распарсить дату - оставляем тендер
                    logging.debug(f"⚠️  Не смогли распарсить дату: {deadline}")
            
            # Извлекаем статус
            status_elem = row.find('div', class_='registry-entry__header-mid__title')
            status = status_elem.get('title', '') if status_elem else ''
            
            # Извлекаем регион из блока заказчика или адреса
            region = ''
            place_elem = row.find('div', class_='registry-entry__body-href')
            if place_elem:
                place_text = place_elem.get_text(separator=' ', strip=True)
                # Ищем типичные маркеры региона: "г. Москва", "Московская обл." и т.д.
                import re as _re
                region_match = _re.search(
                    r'(?:г\.\s*|город\s+)([\w\-]+)', place_text
                )
                if region_match:
                    region = region_match.group(1)
            
            return {
                'tender_id': tender_id,
                'title': title,
                'url': full_url,
                'price': price_text,
                'currency': 'RUB',
                'customer': customer,
                'deadline': deadline,
                'status': status,
                'region': region,
                'description': title  # Для ЕИС описание часто совпадает с заголовком
            }
        
        except Exception as e:
            logging.error(f"Ошибка парсинга строки тендера: {e}")
            return None
    
    def parse_tender_details(self, tender_url: str) -> Dict:
        """Парсинг детальной информации о тендере"""
        details = {}
        
        try:
            response = self.make_request(tender_url)
            if not response:
                return details
            
            soup = self.parse_html(response.text)
            
            # Извлекаем дополнительную информацию
            # Описание закупки
            description_elem = soup.find('div', class_='noticeTabContentTable')
            if description_elem:
                details['description'] = description_elem.get_text(strip=True)
            
            # Требования к участникам
            requirements_elem = soup.find('div', {'id': 'requirements'})
            if requirements_elem:
                details['requirements'] = requirements_elem.get_text(strip=True)
            
            # Контактная информация
            contact_elem = soup.find('div', {'id': 'contactInfo'})
            if contact_elem:
                details['contact_info'] = contact_elem.get_text(strip=True)
            
        except Exception as e:
            logging.error(f"Ошибка парсинга деталей тендера {tender_url}: {e}")
        
        return details
    
    def _fix_rss_link(self, raw_link: str) -> str:
        """Исправление и нормализация ссылок из RSS"""
        if not raw_link:
            return self.base_url
            
        # Убираем возможные лишние пробелы и символы
        link = raw_link.strip()
        
        # Если ссылка уже полная, возвращаем как есть
        if link.startswith('http'):
            # Проверяем что это ссылка на zakupki.gov.ru
            if 'zakupki.gov.ru' in link:
                return link
            else:
                # Если это другой домен, пытаемся извлечь параметры
                from urllib.parse import urlparse, parse_qs
                try:
                    parsed = urlparse(link)
                    query_params = parse_qs(parsed.query)
                    
                    # Если есть regNumber, формируем правильную ссылку
                    if 'regNumber' in query_params:
                        reg_number = query_params['regNumber'][0]
                        return f"{self.base_url}/epz/order/notice/ea44/view/common-info.html?regNumber={reg_number}"
                    
                    # Если есть другие параметры, пытаемся их использовать
                    if query_params:
                        query_string = '&'.join([f"{k}={v[0]}" for k, v in query_params.items()])
                        return f"{self.base_url}/epz/order/notice/ea44/view/common-info.html?{query_string}"
                        
                except Exception as e:
                    logging.warning(f"Ошибка парсинга ссылки {link}: {e}")
                    
        # Если ссылка относительная, добавляем базовый URL
        elif link.startswith('/'):
            return f"{self.base_url}{link}"
        
        # Если это просто параметры, формируем полную ссылку
        elif '=' in link:
            return f"{self.base_url}/epz/order/notice/ea44/view/common-info.html?{link}"
            
        # По умолчанию возвращаем базовый URL
        logging.warning(f"Не удалось обработать ссылку: {link}")
        return self.base_url
    
    def _extract_tender_id_from_url(self, url: str) -> Optional[str]:
        """Извлечение ID тендера из URL"""
        if not url:
            return None
            
        try:
            from urllib.parse import urlparse, parse_qs
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            
            # Приоритет: regNumber - это основной ID в ЕИС
            if 'regNumber' in query_params:
                reg_number = query_params['regNumber'][0]
                logging.info(f"✓ ЕИС: Извлечен regNumber: {reg_number}")
                return reg_number
            
            # Пытаемся найти другие параметры-идентификаторы
            id_params = ['noticeId', 'id', 'purchaseNumber', 'lotId']
            for param in id_params:
                if param in query_params:
                    param_value = query_params[param][0]
                    logging.info(f"✓ ЕИС: Извлечен {param}: {param_value}")
                    return param_value
            
            # Альтернативный способ - извлечение из пути
            path_parts = parsed_url.path.split('/')
            for part in path_parts:
                # Ищем числовые ID (минимум 5 цифр)
                if re.match(r'\d{5,}', part):
                    logging.debug(f"Извлечен ID из пути: {part}")
                    return part
                # Ищем смешанные ID (буквы + цифры)
                elif re.match(r'[A-Za-z0-9\-_]{8,}', part) and any(c.isdigit() for c in part):
                    logging.debug(f"Извлечен смешанный ID: {part}")
                    return part
            
            # Если ничего не нашли, создаем ID на основе хеша URL
            import hashlib
            url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
            logging.debug(f"Создан хеш-ID: {url_hash}")
            return url_hash
            
        except Exception as e:
            logging.warning(f"Ошибка извлечения ID из URL {url}: {e}")
            # В качестве фоллбэка используем последнюю часть URL
            try:
                return url.split('/')[-1] or url.split('?')[-1][:10]
            except:
                return "unknown_id"
    
    def get_tender_id(self, tender_data: Dict) -> str:
        """Получение уникального ID тендера для ЕИС"""
        return f"eis_{tender_data.get('tender_id', '')}"
