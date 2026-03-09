"""
Модуль для работы с базой данных тендеров
"""

import sqlite3
import logging
from datetime import datetime
from typing import List, Dict, Optional
from config import DATABASE_CONFIG

class TenderDatabase:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or DATABASE_CONFIG['db_path']
        self.init_database()
    
    def init_database(self):
        """Инициализация базы данных"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Таблица тендеров
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS tenders (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        tender_id TEXT UNIQUE NOT NULL,
                        platform TEXT NOT NULL,
                        title TEXT NOT NULL,
                        description TEXT,
                        price REAL,
                        currency TEXT,
                        deadline DATETIME,
                        url TEXT NOT NULL,
                        status TEXT DEFAULT 'new',
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Таблица категорий
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS categories (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE NOT NULL,
                        keywords TEXT
                    )
                ''')
                
                # Таблица отклоненных тендеров (Кал)
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS ignored_tenders (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        tender_id TEXT UNIQUE NOT NULL,
                        platform TEXT NOT NULL,
                        title TEXT NOT NULL,
                        ignored_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Таблица избранных тендеров (Играть)
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS favorite_tenders (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        tender_id TEXT UNIQUE NOT NULL,
                        platform TEXT NOT NULL,
                        title TEXT NOT NULL,
                        price REAL,
                        deadline DATETIME,
                        url TEXT NOT NULL,
                        added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        notes TEXT
                    )
                ''')
                
                # Таблица связи тендеров и категорий
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS tender_categories (
                        tender_id INTEGER,
                        category_id INTEGER,
                        FOREIGN KEY (tender_id) REFERENCES tenders (id),
                        FOREIGN KEY (category_id) REFERENCES categories (id),
                        PRIMARY KEY (tender_id, category_id)
                    )
                ''')
                
                # Таблица уведомлений
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS notifications (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        tender_id INTEGER,
                        notification_type TEXT NOT NULL,
                        sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        status TEXT DEFAULT 'sent',
                        FOREIGN KEY (tender_id) REFERENCES tenders (id)
                    )
                ''')
                
                conn.commit()
                logging.info("База данных успешно инициализирована")
                
        except Exception as e:
            logging.error(f"Ошибка инициализации базы данных: {e}")
            raise
    
    def add_tender(self, tender_data: Dict) -> bool:
        """Добавление нового тендера"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR IGNORE INTO tenders 
                    (tender_id, platform, title, description, price, currency, deadline, url)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    tender_data.get('tender_id'),
                    tender_data.get('platform'),
                    tender_data.get('title'),
                    tender_data.get('description'),
                    tender_data.get('price'),
                    tender_data.get('currency'),
                    tender_data.get('deadline'),
                    tender_data.get('url')
                ))
                
                if cursor.rowcount > 0:
                    logging.info(f"Добавлен новый тендер: {tender_data.get('title')}")
                    return True
                
        except Exception as e:
            logging.error(f"Ошибка добавления тендера: {e}")
        
        return False
    
    def tender_exists(self, tender_id: str, platform: str) -> bool:
        """Проверка существования тендера"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'SELECT 1 FROM tenders WHERE tender_id = ? AND platform = ?',
                    (tender_id, platform)
                )
                return cursor.fetchone() is not None
        except Exception as e:
            logging.error(f"Ошибка проверки существования тендера: {e}")
            return False
    
    def get_new_tenders(self, limit: int = 50) -> List[Dict]:
        """Получение новых тендеров"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM tenders 
                    WHERE status = 'new' 
                    ORDER BY created_at DESC 
                    LIMIT ?
                ''', (limit,))
                
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
                
        except Exception as e:
            logging.error(f"Ошибка получения новых тендеров: {e}")
            return []
    
    def mark_tender_notified(self, tender_id: int):
        """Отметка тендера как уведомленного"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'UPDATE tenders SET status = ? WHERE id = ?',
                    ('notified', tender_id)
                )
                conn.commit()
        except Exception as e:
            logging.error(f"Ошибка обновления статуса тендера: {e}")
    
    def add_notification_log(self, tender_id: int, notification_type: str):
        """Добавление записи об уведомлении"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO notifications (tender_id, notification_type)
                    VALUES (?, ?)
                ''', (tender_id, notification_type))
                conn.commit()
        except Exception as e:
            logging.error(f"Ошибка записи уведомления: {e}")
    
    def get_tenders_with_upcoming_deadlines(self, days_ahead: List[int]) -> List[Dict]:
        """Получение тендеров с приближающимися дедлайнами"""
        try:
            from datetime import datetime, timedelta
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                upcoming_tenders = []
                
                for days in days_ahead:
                    target_date = datetime.now() + timedelta(days=days)
                    date_start = target_date.replace(hour=0, minute=0, second=0)
                    date_end = target_date.replace(hour=23, minute=59, second=59)
                    
                    cursor.execute('''
                        SELECT * FROM tenders 
                        WHERE deadline >= ? AND deadline <= ?
                        AND status != 'deadline_notified'
                    ''', (date_start.isoformat(), date_end.isoformat()))
                    
                    columns = [description[0] for description in cursor.description]
                    tenders = [dict(zip(columns, row)) for row in cursor.fetchall()]
                    
                    for tender in tenders:
                        tender['days_remaining'] = days
                        upcoming_tenders.append(tender)
                
                return upcoming_tenders
                
        except Exception as e:
            logging.error(f"Ошибка получения тендеров с дедлайнами: {e}")
            return []
    
    def mark_tender_deadline_notified(self, tender_id: int):
        """Отметка тендера как уведомленного о дедлайне"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'UPDATE tenders SET status = ? WHERE id = ?',
                    ('deadline_notified', tender_id)
                )
                conn.commit()
        except Exception as e:
            logging.error(f"Ошибка обновления статуса дедлайна тендера: {e}")

    def get_statistics(self) -> Dict:
        """Получение статистики по тендерам"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Общее количество тендеров
                cursor.execute('SELECT COUNT(*) FROM tenders')
                total_tenders = cursor.fetchone()[0]
                
                # Новые тендеры
                cursor.execute('SELECT COUNT(*) FROM tenders WHERE status = "new"')
                new_tenders = cursor.fetchone()[0]
                
                # Тендеры по платформам
                cursor.execute('''
                    SELECT platform, COUNT(*) 
                    FROM tenders 
                    GROUP BY platform
                ''')
                by_platform = dict(cursor.fetchall())
                
                return {
                    'total_tenders': total_tenders,
                    'new_tenders': new_tenders,
                    'by_platform': by_platform
                }
                
        except Exception as e:
            logging.error(f"Ошибка получения статистики: {e}")
            return {}
    
    # ========== МЕТОДЫ ДЛЯ ОЦЕНКИ ТЕНДЕРОВ ==========
    
    def ignore_tender(self, tender_data: Dict) -> bool:
        """Добавить тендер в список отклоненных (Кал)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR IGNORE INTO ignored_tenders 
                    (tender_id, platform, title)
                    VALUES (?, ?, ?)
                ''', (
                    tender_data.get('tender_id'),
                    tender_data.get('platform'),
                    tender_data.get('title')
                ))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logging.error(f"Ошибка добавления в отклоненные: {e}")
            return False
    
    def add_to_favorites(self, tender_data: Dict) -> bool:
        """Добавить тендер в избранное (Играть)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO favorite_tenders 
                    (tender_id, platform, title, price, deadline, url)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    tender_data.get('tender_id'),
                    tender_data.get('platform'),
                    tender_data.get('title'),
                    tender_data.get('price'),
                    tender_data.get('deadline'),
                    tender_data.get('url')
                ))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logging.error(f"Ошибка добавления в избранное: {e}")
            return False
    
    def remove_from_favorites(self, tender_id: str) -> bool:
        """Удалить тендер из избранного"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM favorite_tenders WHERE tender_id = ?', (tender_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logging.error(f"Ошибка удаления из избранного: {e}")
            return False
    
    def is_ignored(self, tender_id: str) -> bool:
        """Проверка: тендер в списке отклоненных?"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT 1 FROM ignored_tenders WHERE tender_id = ?', (tender_id,))
                return cursor.fetchone() is not None
        except:
            return False
    
    def is_favorite(self, tender_id: str) -> bool:
        """Проверка: тендер в избранном?"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT 1 FROM favorite_tenders WHERE tender_id = ?', (tender_id,))
                return cursor.fetchone() is not None
        except:
            return False
    
    def get_favorites(self) -> List[Dict]:
        """Получить все избранные тендеры"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT tender_id, platform, title, price, deadline, url, added_at
                    FROM favorite_tenders
                    ORDER BY added_at DESC
                ''')
                
                favorites = []
                for row in cursor.fetchall():
                    favorites.append({
                        'tender_id': row[0],
                        'platform': row[1],
                        'title': row[2],
                        'price': row[3],
                        'deadline': row[4],
                        'url': row[5],
                        'added_at': row[6]
                    })
                return favorites
        except Exception as e:
            logging.error(f"Ошибка получения избранного: {e}")
            return []
    
    def clear_all_data(self):
        """Очистить ВСЮ базу данных (тендеры, отклоненные, избранное)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            try:
                # Очищаем все таблицы
                cursor.execute('DELETE FROM tenders')
                cursor.execute('DELETE FROM ignored_tenders')
                cursor.execute('DELETE FROM favorite_tenders')
                cursor.execute('DELETE FROM notifications')
                conn.commit()
                logging.info("✅ База данных полностью очищена")
                return True
            except Exception as e:
                logging.error(f"❌ Ошибка очистки БД: {e}")
                conn.rollback()
                return False
