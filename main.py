"""
Основной модуль парсера государственных закупок
"""

import logging
import schedule
import time
from datetime import datetime
from typing import List, Dict
from config import PLATFORMS, FILTER_CONFIG, PARSING_CONFIG, LOGGING_CONFIG
from database import TenderDatabase
from notifications import NotificationManager
from parsers import EISParser, SuppliersPortalParser

class TenderMonitor:
    def __init__(self):
        # Настройка логирования
        logging.basicConfig(
            level=getattr(logging, LOGGING_CONFIG['level']),
            format=LOGGING_CONFIG['format'],
            handlers=[
                logging.FileHandler(LOGGING_CONFIG['file'], encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        self.db = TenderDatabase()
        self.notification_manager = NotificationManager()
        
        # Инициализация парсеров
        self.parsers = {}
        if PLATFORMS['eis']['enabled']:
            self.parsers['eis'] = EISParser(PLATFORMS['eis'])
        if PLATFORMS['suppliers_portal']['enabled']:
            self.parsers['suppliers_portal'] = SuppliersPortalParser(PLATFORMS['suppliers_portal'])
        
        logging.info("Парсер тендеров инициализирован")
    
    def run_parsing_cycle(self):
        """Выполнение одного цикла парсинга"""
        logging.info("Начало цикла парсинга тендеров")
        
        new_tenders_count = 0
        
        for platform_name, parser in self.parsers.items():
            try:
                logging.info(f"Парсинг площадки: {platform_name}")
                
                # Получаем тендеры с площадки
                tenders = parser.search_tenders(
                    keywords=FILTER_CONFIG.get('keywords'),
                    filters=FILTER_CONFIG
                )
                
                logging.info(f"Получено {len(tenders)} сырых тендеров с площадки {platform_name}")
                
                # Фильтруем тендеры
                filtered_tenders = parser.filter_tenders(tenders, FILTER_CONFIG)
                logging.info(f"После фильтрации осталось {len(filtered_tenders)} тендеров")
                
                # Обрабатываем каждый тендер
                processed_count = 0
                for tender in filtered_tenders:
                    if not self.db.tender_exists(tender['tender_id'], tender['platform']):
                        # Добавляем новый тендер в базу
                        if self.db.add_tender(tender):
                            new_tenders_count += 1
                            
                            # Отправляем уведомление о новом тендере
                            if self.notification_manager.send_tender_notification(tender, 'new'):
                                self.db.add_notification_log(tender['tender_id'], 'telegram_new')
                                self.db.mark_tender_notified(tender['tender_id'])
                        processed_count += 1
                    else:
                        logging.debug(f"Тендер {tender['tender_id']} уже существует в базе")
                
                logging.info(f"Обработано {processed_count} тендеров с площадки {platform_name}")
                
            except Exception as e:
                logging.error(f"Ошибка парсинга площадки {platform_name}: {e}")
        
        logging.info(f"Цикл парсинга завершен. Найдено новых тендеров: {new_tenders_count}")
        
        # Отправляем статистику
        if new_tenders_count > 0:
            stats = self.db.get_statistics()
            status_message = f"""
Отчет о парсинге тендеров ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})

🆕 Новых тендеров найдено: {new_tenders_count}
📊 Всего тендеров в базе: {stats.get('total_tenders', 0)}
🔄 Необработанных тендеров: {stats.get('new_tenders', 0)}

По площадкам:
{self._format_platform_stats(stats.get('by_platform', {}))}
            """.strip()
            
            self.notification_manager.send_status_notification(status_message)
    
    def check_upcoming_deadlines(self):
        """Проверка приближающихся дедлайнов"""
        logging.info("Проверка приближающихся дедлайнов")
        
        try:
            warning_days = PARSING_CONFIG.get('deadline_warning_days', [5, 6])
            upcoming_tenders = self.db.get_tenders_with_upcoming_deadlines(warning_days)
            
            deadline_notifications_count = 0
            
            for tender in upcoming_tenders:
                # Отправляем уведомление о дедлайне
                if self.notification_manager.send_tender_notification(tender, 'deadline'):
                    self.db.add_notification_log(tender['id'], 'telegram_deadline')
                    self.db.mark_tender_deadline_notified(tender['id'])
                    deadline_notifications_count += 1
            
            if deadline_notifications_count > 0:
                logging.info(f"Отправлено {deadline_notifications_count} уведомлений о дедлайнах")
                
        except Exception as e:
            logging.error(f"Ошибка проверки дедлайнов: {e}")
    
    def _format_platform_stats(self, platform_stats: Dict) -> str:
        """Форматирование статистики по площадкам"""
        if not platform_stats:
            return "Нет данных"
        
        lines = []
        for platform, count in platform_stats.items():
            lines.append(f"• {platform}: {count}")
        
        return "\n".join(lines)
    
    def start_monitoring(self):
        """Запуск мониторинга тендеров"""
        logging.info("Запуск мониторинга тендеров")
        
        # Планируем выполнение парсинга новых тендеров
        interval_minutes = PARSING_CONFIG['check_interval'] // 60
        schedule.every(interval_minutes).minutes.do(self.run_parsing_cycle)
        
        # Планируем проверку дедлайнов каждый час
        deadline_interval_minutes = PARSING_CONFIG['check_deadlines_interval'] // 60
        schedule.every(deadline_interval_minutes).minutes.do(self.check_upcoming_deadlines)
        
        # Выполняем первый цикл сразу
        self.run_parsing_cycle()
        self.check_upcoming_deadlines()
        
        # Основной цикл мониторинга
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Проверяем каждую минуту
                
            except KeyboardInterrupt:
                logging.info("Мониторинг остановлен пользователем")
                break
            except Exception as e:
                logging.error(f"Ошибка в основном цикле мониторинга: {e}")
                time.sleep(60)
    
    def test_system(self):
        """Тестирование системы"""
        logging.info("Запуск тестирования системы")
        
        # Тест базы данных
        try:
            stats = self.db.get_statistics()
            logging.info(f"База данных работает. Статистика: {stats}")
        except Exception as e:
            logging.error(f"Ошибка базы данных: {e}")
            return False
        
        # Тест парсеров
        for platform_name, parser in self.parsers.items():
            try:
                logging.info(f"Тестирование парсера {platform_name}")
                tenders = parser.search_tenders(keywords=['тест'], filters={})
                logging.info(f"Парсер {platform_name} работает. Найдено тендеров: {len(tenders)}")
            except Exception as e:
                logging.error(f"Ошибка парсера {platform_name}: {e}")
        
        # Тест уведомлений
        try:
            test_results = self.notification_manager.test_notifications()
            logging.info(f"Результаты тестирования уведомлений: {test_results}")
        except Exception as e:
            logging.error(f"Ошибка тестирования уведомлений: {e}")
        
        logging.info("Тестирование системы завершено")
        return True

def main():
    """Главная функция"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Парсер государственных закупок')
    parser.add_argument('--test', action='store_true', help='Запуск в тестовом режиме')
    parser.add_argument('--once', action='store_true', help='Выполнить один цикл парсинга')
    
    args = parser.parse_args()
    
    monitor = TenderMonitor()
    
    if args.test:
        monitor.test_system()
    elif args.once:
        monitor.run_parsing_cycle()
    else:
        monitor.start_monitoring()

if __name__ == "__main__":
    main()
