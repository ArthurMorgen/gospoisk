"""
Парсер для Портала поставщиков - Котировочные сессии
Работает через JSON API, БЕЗ авторизации и Selenium!
"""

import requests
from typing import List, Dict, Optional
import logging
import json
from datetime import datetime
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
            logging.info(f"🔍 Поиск котировочных сессий на {self.base_url} через GET API")
            
            # Подготовка JSON для GET запроса
            query_dto = self.search_params.copy()
            
            if keywords:
                # Объединяем ключевые слова в строку поиска
                search_string = ' '.join(keywords[:5])
                query_dto['filter']['nameLike']['value'] = search_string
                logging.debug(f"Поиск по ключевым словам: {search_string}")
            
            # Выполняем GET запрос к API
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            
            logging.debug(f"API URL: {self.search_url}")
            logging.debug(f"Query DTO: {json.dumps(query_dto, ensure_ascii=False)[:200]}...")
            
            # GET запрос с queryDto в параметрах
            response = requests.get(
                self.search_url,
                params={'queryDto': json.dumps(query_dto, ensure_ascii=False)},
                headers=headers,
                timeout=30,
                verify=False
            )
            
            logging.info(f"✓ Ответ API: {response.status_code}")
            
            if response.status_code == 200:
                # Парсим JSON ответ
                data = response.json()
                
                # Сохраняем JSON для анализа
                with open('debug_zakupki_mos_api.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                logging.info("✓ JSON ответ сохранен в debug_zakupki_mos_api.json")
                
                # Извлекаем котировочные сессии из ответа old.zakupki.mos.ru
                items = data.get('items', [])
                total_count = data.get('total', 0)
                
                if not items:
                    logging.warning("⚠️ API вернул пустой список")
                    logging.debug(f"Структура ответа: {list(data.keys())}")
                    logging.debug(f"Total в ответе: {total_count}")
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
        """Парсинг элемента котировочной сессии из old.zakupki.mos.ru API"""
        try:
            # ID котировки - берем auctionId или needId или tenderId
            auction_id = item.get('auctionId')
            need_id = item.get('needId')
            tender_id = item.get('tenderId')
            
            # Используем первый непустой ID
            clean_id = auction_id or need_id or tender_id
            if not clean_id:
                logging.debug("Котировка без ID, пропускаем")
                return None
            
            # Название
            title = item.get('name', '')
            
            if not title:
                logging.debug("Котировка без названия, пропускаем")
                return None
            
            # URL котировки - используем externalUrl из API
            # Это ссылка на ОРИГИНАЛЬНЫЙ портал региона (Москва, МО и т.д.)
            external_url = item.get('externalUrl', '')
            if external_url:
                quotation_url = external_url
                logging.debug(f"✓ Используем externalUrl: {external_url}")
            else:
                # Если нет externalUrl - пробуем построить сами
                quotation_url = f"https://zakupki.mos.ru/auction/{clean_id}"
                logging.debug(f"⚠️ Нет externalUrl, строим сами: {quotation_url}")
            
            # Цена - берем startPrice или auctionCurrentPrice
            start_price = item.get('startPrice')
            current_price = item.get('auctionCurrentPrice')
            price_value = float(current_price or start_price or 0.0)
            
            # Заказчик - берем из массива customers
            customers = item.get('customers', [])
            customer_name = ''
            if customers and isinstance(customers, list) and len(customers) > 0:
                first_customer = customers[0]
                if first_customer and isinstance(first_customer, dict):
                    customer_name = first_customer.get('name', '').strip()
            
            # Если нет заказчика, берем из purchaseCreator
            if not customer_name:
                creator = item.get('purchaseCreator', {})
                if creator and isinstance(creator, dict):
                    customer_name = creator.get('name', '').strip()
            
            # Дата окончания подачи заявок
            end_date = item.get('endDate', '')
            
            # ФИЛЬТРУЕМ: дата окончания >= СЕГОДНЯ
            if end_date:
                try:
                    end_datetime = datetime.strptime(end_date, "%d.%m.%Y %H:%M:%S")
                    now = datetime.now()
                    
                    # Сравниваем только ДАТЫ (без времени)
                    # Если дедлайн сегодня или раньше - пропускаем
                    if end_datetime.date() <= now.date():
                        logging.debug(f"⏭️  Пропускаем - дедлайн прошел или сегодня: {end_date}")
                        return None
                    
                    logging.debug(f"✓ Активна - дедлайн {end_date}")
                except ValueError:
                    logging.debug(f"⚠️  Не смогли распарсить дату: {end_date}")
            
            # Статус
            status = item.get('stateName', '')
            
            logging.info(f"✓ ПОРТАЛ: Котировка {clean_id}: {title[:50]}...")
            logging.debug(f"ПОРТАЛ: URL: {quotation_url}, Цена: {price_value}, Заказчик: {customer_name[:50]}")
            
            return {
                'tender_id': str(clean_id),
                'title': title,
                'url': quotation_url,
                'price': price_value,  # Число для фильтрации
                'currency': 'RUB',
                'customer': customer_name,
                'deadline': end_date,
                'status': status,
                'description': title,
                'platform': 'suppliers_portal'
            }
            
        except Exception as e:
            logging.error(f"Ошибка парсинга котировки: {e}")
            import traceback
            logging.debug(traceback.format_exc())
            return None
    
    def parse_tender_details(self, tender_url: str) -> Dict:
        """Парсинг детальной информации о тендере"""
        # Для котировочных сессий детали уже получены через API
        return {}
    
    def get_tender_id(self, tender_data: Dict) -> str:
        """Получение уникального ID тендера для Портала поставщиков"""
        return f"suppliers_{tender_data.get('tender_id', '')}"
