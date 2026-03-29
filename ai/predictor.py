"""
Предиктор % снижения цены тендера.
Загружает обученную модель и делает прогнозы.
"""

import os
import json
import pickle
import logging
import numpy as np
from typing import Optional

logger = logging.getLogger(__name__)

AI_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(AI_DIR, 'model.pkl')
META_PATH = os.path.join(AI_DIR, 'model_meta.json')


class PriceDropPredictor:
    def __init__(self):
        self.model = None
        self.meta = None
        self._load()
    
    def _load(self):
        try:
            with open(MODEL_PATH, 'rb') as f:
                self.model = pickle.load(f)
            with open(META_PATH, 'r', encoding='utf-8') as f:
                self.meta = json.load(f)
            logger.info("Модель прогноза загружена")
        except Exception as e:
            logger.warning(f"Не удалось загрузить модель: {e}")
    
    def predict(self, title: str, price: float, proc_type: str = '44-FZ') -> Optional[dict]:
        """
        Прогноз % снижения цены.
        
        Args:
            title: название тендера
            price: начальная (максимальная) цена
            proc_type: тип процедуры ('44-FZ' или '223-FZ')
        
        Returns:
            {'drop_pct': float, 'category': str, 'confidence': str}
        """
        if not self.model or not self.meta or price <= 0:
            return None
        
        # Определяем категорию по названию
        category = self._detect_category(title)
        
        cat_idx = self.meta['cat_to_idx'].get(category, 0)
        proc_idx = self.meta['proc_to_idx'].get(proc_type, 0)
        
        features = np.array([[
            cat_idx,
            np.log1p(price),
            price,
            proc_idx,
            1 if price > 10_000_000 else 0,
            1 if price < 100_000 else 0,
        ]])
        
        try:
            drop_pct = float(self.model.predict(features)[0])
            drop_pct = max(1.0, min(45.0, drop_pct))  # Ограничиваем разумным диапазоном
            
            # Уровень уверенности
            avg = self.meta.get('category_averages', {}).get(category)
            if avg and abs(drop_pct - avg) < 3:
                confidence = 'high'
            elif avg and abs(drop_pct - avg) < 6:
                confidence = 'medium'
            else:
                confidence = 'low'
            
            return {
                'drop_pct': round(drop_pct, 1),
                'category': category,
                'confidence': confidence,
            }
        except Exception as e:
            logger.warning(f"Ошибка прогноза: {e}")
            return self._fallback(category)
    
    def _detect_category(self, title: str) -> str:
        """Определить категорию закупки по названию"""
        title_lower = title.lower()
        
        keyword_map = {
            'канцелярские товары': ['канцеляр', 'ручк', 'бумаг', 'тетрад', 'папк'],
            'мебель': ['мебел', 'стол', 'стул', 'шкаф', 'кресл'],
            'компьютеры': ['компьютер', 'ноутбук', 'монитор', 'сервер', 'системный блок'],
            'продукты питания': ['продукт', 'питани', 'молок', 'мяс', 'хлеб', 'овощ'],
            'медицинские изделия': ['медицин', 'шприц', 'бинт', 'перчатк', 'маск'],
            'лекарства': ['лекарств', 'препарат', 'таблет', 'вакцин', 'фармацев'],
            'строительные работы': ['строител', 'возведен', 'фундамент', 'монтаж здан'],
            'ремонт': ['ремонт', 'реконструк', 'восстановлен', 'капитальн'],
            'уборка помещений': ['уборк', 'клининг', 'содержани', 'обслуживани помещ'],
            'охрана': ['охран', 'безопасност', 'пожарн', 'видеонаблюден'],
            'транспортные услуги': ['транспорт', 'перевоз', 'автобус', 'автомобил'],
            'печать': ['печат', 'типограф', 'полиграф', 'баннер', 'плакат'],
            'одежда': ['одежд', 'форм', 'обувь', 'костюм', 'куртк'],
            'оборудование': ['оборудован', 'прибор', 'станок', 'агрегат', 'установк'],
            'программное обеспечение': ['программ', 'лицензи', 'софт', 'информацион'],
            'связь': ['связ', 'телефон', 'интернет', 'телекоммуникац'],
            'электроэнергия': ['электроэнерг', 'электричеств', 'энергоснабжен'],
            'топливо': ['топлив', 'бензин', 'дизел', 'газ', 'гсм'],
            'обучение': ['обучен', 'курс', 'тренинг', 'повышен квалификац'],
            'консалтинг': ['консалтинг', 'консультац', 'аудит', 'экспертиз'],
            'грамоты': ['грамот', 'награжден', 'благодарствен'],
            'дипломы': ['диплом', 'аттестат', 'свидетельств', 'сертификат'],
            'бланки': ['бланк', 'строгой отчетност'],
            'полиграфия': ['полиграф', 'буклет', 'брошюр', 'листовк', 'каталог'],
        }
        
        for category, keywords in keyword_map.items():
            for kw in keywords:
                if kw in title_lower:
                    return category
        
        return 'оборудование'  # Дефолтная категория
    
    def _fallback(self, category: str) -> Optional[dict]:
        """Fallback — средние по категории"""
        if not self.meta:
            return None
        avg = self.meta.get('category_averages', {}).get(category, 10.0)
        return {
            'drop_pct': round(avg, 1),
            'category': category,
            'confidence': 'low',
        }


# Синглтон
_predictor = None

def get_predictor() -> PriceDropPredictor:
    global _predictor
    if _predictor is None:
        _predictor = PriceDropPredictor()
    return _predictor
