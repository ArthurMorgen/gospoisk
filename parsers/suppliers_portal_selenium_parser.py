"""
Парсер Портала поставщиков (zakupki.mos.ru) через API
Парсит котировочные сессии по ключевым словам

Оптимизированная версия:
- Прямой API запрос (без Selenium)
- Полный список ключевых слов
- Быстрая работа
"""

import logging
import requests
import json
import urllib.parse
from typing import List, Dict, Optional
from datetime import datetime


class SuppliersPortalSeleniumParser:
    """Парсер Портала поставщиков через API"""
    
    def __init__(self, config):
        self.base_url = 'https://zakupki.mos.ru'
        self.api_url = 'https://old.zakupki.mos.ru/api/Cssp/Purchase/Query'
        self.timeout = config.get('timeout', 30)
        logging.info("SuppliersPortalSeleniumParser инициализирован (API: ✓)")
    
    def search_tenders(self, keywords: List[str] = None, max_results: int = 50) -> List[Dict]:
        """Поиск тендеров на Портале поставщиков через API"""
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
        
        for keyword in search_keywords:
            logging.info(f"🔍 Портал поставщиков: '{keyword}'...")
            tenders = self._search_api(keyword)
            
            for t in tenders:
                if t['tender_id'] not in seen_ids:
                    seen_ids.add(t['tender_id'])
                    all_tenders.append(t)
            
            logging.info(f"   → найдено {len(tenders)} тендеров")
        
        logging.info(f"✓ Всего найдено уникальных тендеров: {len(all_tenders)}")
        return all_tenders[:max_results]
    
    def _search_api(self, keyword: str) -> List[Dict]:
        """Поиск через API"""
        try:
            # Правильный формат queryDto для zakupki.mos.ru API
            # stateIdIn: 19000002 = Активные котировки
            query_dto = {
                "filter": {
                    "nameLike": {"value": keyword, "contains": True},
                    "auctionSpecificFilter": {
                        "stateIdIn": [19000002]
                    }
                },
                "order": [{"field": "PublishDate", "desc": True}],
                "withCount": True,
                "take": 20,
                "skip": 0
            }
            
            # Кодируем JSON в URL параметр
            query_json = json.dumps(query_dto, ensure_ascii=False)
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                'Origin': 'https://zakupki.mos.ru',
                'Referer': 'https://zakupki.mos.ru/'
            }
            
            response = requests.get(
                self.api_url,
                params={'queryDto': query_json},
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                logging.error(f"API ошибка: {response.status_code}")
                return []
            
            data = response.json()
            items = data.get('items', []) or data.get('content', []) or []
            
            tenders = []
            for item in items:
                tender = self._parse_item(item)
                if tender:
                    tenders.append(tender)
            
            return tenders
            
        except Exception as e:
            logging.error(f"Ошибка API: {e}")
            return []
    
    def _parse_item(self, item: dict) -> Optional[Dict]:
        """Парсинг одного элемента из API"""
        try:
            # ID - определяем тип закупки
            # auctionId = котировочная сессия (/auction/)
            # needId = закупка по потребностям (/need/)
            auction_id = item.get('auctionId')
            need_id = item.get('needId')
            
            # Выбираем ID и тип URL (auctionId приоритетнее!)
            if auction_id:
                item_id = auction_id
                url_type = 'auction'
                tender_type = 'Котировочная сессия'
            elif need_id:
                item_id = need_id
                url_type = 'need'
                tender_type = 'Закупка по потребностям'
            else:
                return None
            
            # Название
            title = item.get('name', '')
            if not title:
                return None
            
            # Проверяем дату окончания - отбрасываем старые
            deadline = item.get('endDate', '')
            if deadline:
                try:
                    from datetime import datetime as dt
                    end_date = dt.strptime(deadline, '%d.%m.%Y %H:%M:%S')
                    if end_date < dt.now():
                        return None  # Старая закупка
                except:
                    pass
            
            # URL - правильный формат
            url = f"{self.base_url}/{url_type}/{item_id}"
            
            # Цена
            price = float(item.get('auctionCurrentPrice') or item.get('startPrice') or 0)
            
            # Заказчик
            customers = item.get('customers', [])
            customer = customers[0].get('name', '') if customers else ''
            
            # Статус
            status = item.get('stateName', 'Активна')
            
            return {
                'tender_id': str(item_id),
                'platform': 'suppliers_portal_new',
                'title': title,
                'price': price,
                'customer': customer,
                'deadline': deadline,
                'status': status,
                'url': url,
                'tender_type': tender_type,
                'region': 'Москва',
                'parsed_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            return None
