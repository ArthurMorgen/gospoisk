"""
Базовый класс для парсеров государственных площадок
"""

import requests
import time
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from config import PARSING_CONFIG

class BaseParser(ABC):
    def __init__(self, platform_config: Dict):
        self.platform_config = platform_config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def make_request(self, url: str, params: Dict = None, retries: int = None) -> Optional[requests.Response]:
        """Выполнение HTTP запроса с повторными попытками"""
        if retries is None:
            retries = PARSING_CONFIG['max_retries']
            
        for attempt in range(retries + 1):
            try:
                # Увеличиваем таймаут и добавляем verify=False для проблемных сайтов
                response = self.session.get(
                    url, 
                    params=params, 
                    timeout=60,  # Увеличиваем таймаут
                    verify=False,  # Отключаем проверку SSL для проблемных сайтов
                    allow_redirects=True
                )
                
                # Проверяем статус код более мягко
                if response.status_code == 200:
                    # Задержка между запросами
                    time.sleep(PARSING_CONFIG['request_delay'])
                    return response
                else:
                    logging.warning(f"HTTP {response.status_code} для {url}")
                    
            except requests.exceptions.Timeout:
                logging.warning(f"Таймаут для {url} (попытка {attempt + 1})")
            except requests.exceptions.ConnectionError:
                logging.warning(f"Ошибка соединения с {url} (попытка {attempt + 1})")
            except Exception as e:
                logging.warning(f"Ошибка запроса к {url}: {e} (попытка {attempt + 1})")
            
            if attempt < retries:
                time.sleep(5)  # Увеличиваем паузу между попытками
            else:
                logging.error(f"Все попытки исчерпаны для {url}")
                    
        return None
    
    def parse_html(self, html_content: str) -> BeautifulSoup:
        """Парсинг HTML контента"""
        return BeautifulSoup(html_content, 'lxml')
    
    @abstractmethod
    def search_tenders(self, keywords: List[str] = None, filters: Dict = None) -> List[Dict]:
        """Поиск тендеров на площадке"""
        pass
    
    @abstractmethod
    def parse_tender_details(self, tender_url: str) -> Dict:
        """Парсинг детальной информации о тендере"""
        pass
    
    @abstractmethod
    def get_tender_id(self, tender_data: Dict) -> str:
        """Получение уникального ID тендера"""
        pass
    
    def format_tender_data(self, raw_data: Dict) -> Dict:
        """Форматирование данных тендера в стандартный вид"""
        return {
            'tender_id': self.get_tender_id(raw_data),
            'platform': self.platform_config['name'],
            'title': raw_data.get('title', '').strip(),
            'description': raw_data.get('description', '').strip(),
            'price': self.parse_price(raw_data.get('price')),
            'currency': raw_data.get('currency', 'RUB'),
            'deadline': self.parse_date(raw_data.get('deadline')),
            'url': raw_data.get('url', ''),
            'region': raw_data.get('region', ''),
            'customer': raw_data.get('customer', ''),
            'category': raw_data.get('category', '')
        }
    
    def parse_price(self, price_str: str) -> Optional[float]:
        """Парсинг цены из строки"""
        if not price_str:
            return None
            
        try:
            # Удаляем все символы кроме цифр, точек и запятых
            price_clean = ''.join(c for c in str(price_str) if c.isdigit() or c in '.,')
            if not price_clean:
                return None
                
            # Заменяем запятую на точку
            price_clean = price_clean.replace(',', '.')
            return float(price_clean)
            
        except (ValueError, TypeError):
            logging.warning(f"Не удалось распарсить цену: {price_str}")
            return None
    
    def parse_date(self, date_str: str) -> Optional[str]:
        """Парсинг даты из строки в формат ISO"""
        if not date_str:
            return None
            
        try:
            from datetime import datetime
            import re
            
            date_clean = str(date_str).strip()
            
            # Различные форматы дат на российских площадках
            date_patterns = [
                # ДД.ММ.ГГГГ ЧЧ:ММ
                (r'(\d{1,2})\.(\d{1,2})\.(\d{4})\s+(\d{1,2}):(\d{2})', '%d.%m.%Y %H:%M'),
                # ДД.ММ.ГГГГ
                (r'(\d{1,2})\.(\d{1,2})\.(\d{4})', '%d.%m.%Y'),
                # ГГГГ-ММ-ДД ЧЧ:ММ:СС
                (r'(\d{4})-(\d{1,2})-(\d{1,2})\s+(\d{1,2}):(\d{2}):(\d{2})', '%Y-%m-%d %H:%M:%S'),
                # ГГГГ-ММ-ДД
                (r'(\d{4})-(\d{1,2})-(\d{1,2})', '%Y-%m-%d'),
                # ДД/ММ/ГГГГ
                (r'(\d{1,2})/(\d{1,2})/(\d{4})', '%d/%m/%Y'),
            ]
            
            for pattern, date_format in date_patterns:
                match = re.search(pattern, date_clean)
                if match:
                    try:
                        if 'H' in date_format or 'M' in date_format:
                            # С временем
                            parsed_date = datetime.strptime(match.group(0), date_format)
                        else:
                            # Только дата, устанавливаем время 23:59
                            parsed_date = datetime.strptime(match.group(0), date_format)
                            parsed_date = parsed_date.replace(hour=23, minute=59)
                        
                        return parsed_date.isoformat()
                    except ValueError:
                        continue
            
            # Если не удалось распарсить, возвращаем оригинальную строку
            logging.warning(f"Не удалось распарсить дату: {date_str}")
            return date_clean
            
        except Exception as e:
            logging.warning(f"Ошибка парсинга даты {date_str}: {e}")
            return str(date_str).strip()
    
    def filter_tenders(self, tenders: List[Dict], filters: Dict) -> List[Dict]:
        """Фильтрация тендеров по критериям"""
        if not filters:
            return tenders
            
        filtered = []
        # Принудительное INFO сообщение для отладки
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
                        break
                
                if exclude_found:
                    continue
            
            # Фильтр по статусу (исключаем завершенные)
            if filters.get('exclude_finished') or filters.get('only_active'):
                status = tender.get('status', '').lower()
                exclude_statuses = filters.get('exclude_statuses', [])
                
                for exclude_status in exclude_statuses:
                    if exclude_status.lower() in status:
                        continue
                
                # Проверяем на ключевые слова завершенности
                finished_keywords = ['завершен', 'отменен', 'не состоялся', 'закрыт', 'истек', 'окончен']
                if any(keyword in status for keyword in finished_keywords):
                    continue
            
            # Фильтр по дате окончания (исключаем просроченные)
            if filters.get('only_active'):
                deadline = tender.get('deadline', '')
                if deadline and self._is_deadline_passed(deadline):
                    continue
            
            # Фильтр по цене
            price = tender.get('price')
            if price is not None:
                min_price = filters.get('min_price', 0)
                max_price = filters.get('max_price')
                
                if price < min_price:
                    continue
                    
                if max_price is not None and price > max_price:
                    continue
            
            filtered.append(tender)
        
        return filtered
    
    def _is_deadline_passed(self, deadline_str: str) -> bool:
        """Проверка, истек ли срок подачи заявок"""
        try:
            from datetime import datetime
            import re
            
            # Простая проверка на основе текста
            deadline_lower = deadline_str.lower()
            if any(word in deadline_lower for word in ['истек', 'прошел', 'завершен']):
                return True
            
            # Здесь можно добавить более сложную логику парсинга дат
            # в зависимости от формата каждой площадки
            
            return False
        except:
            return False
