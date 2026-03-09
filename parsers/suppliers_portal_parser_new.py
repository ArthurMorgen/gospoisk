"""
Парсер для Портала поставщиков - Котировочные сессии
Работает через JSON API, БЕЗ авторизации и Selenium!
"""

import requests
from typing import List, Dict, Optional
import logging
import json
from .base_parser import BaseParser

class SuppliersPortalParser(BaseParser):
    def __init__(self, platform_config: Dict):
        super().__init__(platform_config)
        self.base_url = platform_config['base_url']
        self.search_url = platform_config['search_url']
        self.search_params = platform_config.get('search_params', {})
    
    def search_tenders(self, keywords: List[str] = None, filters: Dict = None) -> List[Dict]:
        """Поиск котировочных сессий на Портале поставщиков через JSON API (БЕЗ авторизации!)"""
        tenders = []
        
        try:
            logging.info(f"🔍 Поиск котировочных сессий на {self.base_url} через JSON API")
            
            # Подготовка параметров запроса
            params = self.search_params.copy()
            
            if keywords:
                # Объединяем ключевые слова в строку поиска
                search_string = ' '.join(keywords[:10])
                params['searchString'] = search_string
                logging.debug(f"Поиск по ключевым словам: {search_string}")
            
            # Выполняем GET запрос к API
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            
            logging.debug(f"API URL: {self.search_url}")
            logging.debug(f"Параметры: {params}")
            
            response = requests.get(
                self.search_url,
                params=params,
                headers=headers,
                timeout=30,
                verify=False  # Отключаем проверку SSL если нужно
            )
            
            logging.info(f"✓ Ответ API: {response.status_code}")
            
            if response.status_code == 200:
                # Парсим JSON ответ
                data = response.json()
                
                # Сохраняем JSON для анализа
                with open('debug_zakupki_mos_api.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                logging.info("✓ JSON ответ сохранен в debug_zakupki_mos_api.json")
                
                # Извлекаем котировочные сессии
                items = data.get('content', []) or data.get('data', []) or data.get('items', []) or data
                
                if isinstance(items, dict):
                    # Возможно items это словарь с ключом content
                    items = items.get('content', []) or items.get('items', [])
                
                if not items or not isinstance(items, list):
                    logging.warning("⚠️ API вернул пустой список или неверную структуру")
                    logging.debug(f"Структура ответа: {list(data.keys()) if isinstance(data, dict) else type(data)}")
                    return tenders
                
                logging.info(f"✅ Получено {len(items)} котировочных сессий")
                
                # Парсим каждую котировку
                for item in items:
                    try:
                        tender = self._parse_quotation_item(item)
                        if tender:
                            tenders.append(tender)
                    except Exception as e:
                        logging.error(f"Ошибка парсинга котировки: {e}")
                        continue
                
                logging.info(f"✅ Успешно распарсено {len(tenders)} котировок")
            else:
                logging.error(f"❌ Ошибка API: {response.status_code}")
                logging.debug(f"Ответ: {response.text[:500]}")
                
        except Exception as e:
            logging.error(f"❌ Ошибка поиска котировок: {e}")
            import traceback
            logging.debug(traceback.format_exc())
            
        return tenders
    
    def _parse_quotation_item(self, item: Dict) -> Optional[Dict]:
        """Парсинг элемента котировочной сессии из JSON API"""
        try:
            # ID котировки
            tender_id = str(item.get('id', ''))
            
            # Название
            title = item.get('name', '') or item.get('title', '') or item.get('subject', '') or item.get('purchaseObject', '')
            
            if not title:
                logging.debug("Котировка без названия, пропускаем")
                return None
            
            # URL котировки
            quotation_url = f"{self.base_url}/quotationsession/{tender_id}"
            
            # Цена
            price = item.get('price', '') or item.get('maxPrice', '') or item.get('startPrice', '') or item.get('sum', '')
            price_str = str(price) if price else ''
            
            # Заказчик
            customer = item.get('customer', {})
            if isinstance(customer, dict):
                customer_name = customer.get('name', '') or customer.get('title', '') or customer.get('shortName', '')
            else:
                customer_name = str(customer) if customer else ''
            
            # Дата окончания подачи заявок
            deadline = item.get('endDate', '') or item.get('deadline', '') or item.get('finishDate', '') or item.get('submissionCloseDateTime', '')
            
            # Статус
            status = item.get('status', '') or item.get('state', '') or item.get('statusName', '')
            
            logging.info(f"✓ ПОРТАЛ: Котировка {tender_id}: {title[:50]}...")
            logging.debug(f"ПОРТАЛ: URL: {quotation_url}, Цена: {price_str}, Заказчик: {customer_name}")
            
            return {
                'tender_id': tender_id,
                'title': title,
                'url': quotation_url,
                'price': price_str,
                'currency': 'RUB',
                'customer': customer_name,
                'deadline': deadline,
                'status': status,
                'description': title,
                'platform': 'suppliers_portal'
            }
            
        except Exception as e:
            logging.error(f"Ошибка парсинга котировки: {e}")
            import traceback
            logging.debug(traceback.format_exc())
            return None
    
    def get_tender_id(self, tender_data: Dict) -> str:
        """Получение уникального ID тендера для Портала поставщиков"""
        return f"suppliers_{tender_data.get('tender_id', '')}"
