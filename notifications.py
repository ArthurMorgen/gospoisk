"""
Модуль для отправки уведомлений о новых тендерах
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict
from config import NOTIFICATION_CONFIG

try:
    import requests
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    logging.warning("Requests библиотека не установлена. Уведомления в Telegram недоступны.")

class NotificationManager:
    def __init__(self):
        self.email_config = NOTIFICATION_CONFIG['email']
        self.telegram_config = NOTIFICATION_CONFIG['telegram']
        
        # Telegram API URL
        if TELEGRAM_AVAILABLE and self.telegram_config['enabled']:
            self.telegram_api_url = f"https://api.telegram.org/bot{self.telegram_config['bot_token']}/sendMessage"
        else:
            self.telegram_api_url = None
    
    def send_tender_notification(self, tender: Dict, notification_type: str = 'new') -> bool:
        """Отправка уведомления о тендере"""
        success = True
        
        # Формируем сообщение в зависимости от типа
        if notification_type == 'deadline':
            message = self._format_deadline_message(tender)
        else:
            message = self._format_tender_message(tender)
        
        # Отправляем по email
        if self.email_config['enabled']:
            if not self._send_email_notification(message, tender):
                success = False
        
        # Отправляем в Telegram
        if self.telegram_config['enabled'] and self.telegram_api_url:
            if not self._send_telegram_notification(message):
                success = False
        
        return success
    
    def _format_tender_message(self, tender: Dict) -> str:
        """Форматирование сообщения о тендере"""
        message = f"""
🔔 НОВЫЙ ТЕНДЕР

📋 Название: {tender.get('title', 'Не указано')}
🏢 Площадка: {tender.get('platform', 'Не указано')}
💰 Цена: {tender.get('price', 'Не указана')} {tender.get('currency', '')}
🏛️ Заказчик: {tender.get('customer', 'Не указан')}
📅 Срок подачи: {tender.get('deadline', 'Не указан')}
🔗 Ссылка: {tender.get('url', '')}

📝 Описание: {tender.get('description', 'Не указано')[:200]}...
        """.strip()
        
        return message
    
    def _format_deadline_message(self, tender: Dict) -> str:
        """Форматирование сообщения о приближающемся дедлайне"""
        days_remaining = tender.get('days_remaining', 0)
        
        message = f"""
⏰ СРОК ПОДАЧИ ЗАЯВОК ИСТЕКАЕТ!

📅 Осталось дней: {days_remaining}
📋 Название: {tender.get('title', 'Не указано')}
🏢 Площадка: {tender.get('platform', 'Не указано')}
💰 Цена: {tender.get('price', 'Не указана')} {tender.get('currency', '')}
🏛️ Заказчик: {tender.get('customer', 'Не указан')}
📅 Срок подачи: {tender.get('deadline', 'Не указан')}
🔗 Ссылка: {tender.get('url', '')}

⚡ УСПЕЙТЕ ПОДАТЬ ЗАЯВКУ!
        """.strip()
        
        return message
    
    def _send_email_notification(self, message: str, tender: Dict) -> bool:
        """Отправка уведомления по email"""
        try:
            # Создаем сообщение
            msg = MIMEMultipart()
            msg['From'] = self.email_config['username']
            msg['Subject'] = f"Новый тендер: {tender.get('title', '')[:50]}..."
            
            # Добавляем текст сообщения
            msg.attach(MIMEText(message, 'plain', 'utf-8'))
            
            # Подключаемся к SMTP серверу
            with smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port']) as server:
                server.starttls()
                server.login(self.email_config['username'], self.email_config['password'])
                
                # Отправляем всем получателям
                for recipient in self.email_config['recipients']:
                    msg['To'] = recipient
                    server.send_message(msg)
                    del msg['To']
            
            logging.info(f"Email уведомление отправлено для тендера: {tender.get('title', '')}")
            return True
            
        except Exception as e:
            logging.error(f"Ошибка отправки email уведомления: {e}")
            return False
    
    def _send_telegram_notification(self, message: str) -> bool:
        """Отправка уведомления в Telegram через HTTP API"""
        if not self.telegram_api_url:
            return False
            
        try:
            # Отправляем сообщение всем чатам
            for chat_id in self.telegram_config['chat_ids']:
                data = {
                    'chat_id': chat_id,
                    'text': message,
                    'parse_mode': 'HTML',
                    'disable_web_page_preview': False
                }
                
                response = requests.post(self.telegram_api_url, json=data, timeout=10)
                response.raise_for_status()
            
            logging.info("Telegram уведомление отправлено")
            return True
            
        except Exception as e:
            logging.error(f"Ошибка отправки Telegram уведомления: {e}")
            return False
    
    def send_status_notification(self, status_message: str) -> bool:
        """Отправка статусного уведомления"""
        success = True
        
        # Отправляем по email
        if self.email_config['enabled']:
            try:
                msg = MIMEMultipart()
                msg['From'] = self.email_config['username']
                msg['Subject'] = "Статус парсера тендеров"
                msg.attach(MIMEText(status_message, 'plain', 'utf-8'))
                
                with smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port']) as server:
                    server.starttls()
                    server.login(self.email_config['username'], self.email_config['password'])
                    
                    for recipient in self.email_config['recipients']:
                        msg['To'] = recipient
                        server.send_message(msg)
                        del msg['To']
                        
            except Exception as e:
                logging.error(f"Ошибка отправки статусного email: {e}")
                success = False
        
        # Отправляем в Telegram
        if self.telegram_config['enabled'] and self.telegram_api_url:
            try:
                for chat_id in self.telegram_config['chat_ids']:
                    data = {
                        'chat_id': chat_id,
                        'text': f"📊 {status_message}"
                    }
                    response = requests.post(self.telegram_api_url, json=data, timeout=10)
                    response.raise_for_status()
            except Exception as e:
                logging.error(f"Ошибка отправки статусного Telegram сообщения: {e}")
                success = False
        
        return success
    
    def test_notifications(self) -> Dict[str, bool]:
        """Тестирование настроек уведомлений"""
        results = {}
        
        test_message = "🧪 Тестовое сообщение от парсера тендеров"
        
        # Тест email
        if self.email_config['enabled']:
            results['email'] = self._send_test_email(test_message)
        
        # Тест Telegram
        if self.telegram_config['enabled'] and self.telegram_api_url:
            results['telegram'] = self._send_test_telegram(test_message)
        
        return results
    
    def _send_test_email(self, message: str) -> bool:
        """Отправка тестового email"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_config['username']
            msg['Subject'] = "Тест уведомлений парсера тендеров"
            msg.attach(MIMEText(message, 'plain', 'utf-8'))
            
            with smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port']) as server:
                server.starttls()
                server.login(self.email_config['username'], self.email_config['password'])
                
                for recipient in self.email_config['recipients']:
                    msg['To'] = recipient
                    server.send_message(msg)
                    del msg['To']
            
            return True
            
        except Exception as e:
            logging.error(f"Ошибка тестового email: {e}")
            return False
    
    def _send_test_telegram(self, message: str) -> bool:
        """Отправка тестового сообщения в Telegram"""
        try:
            for chat_id in self.telegram_config['chat_ids']:
                data = {
                    'chat_id': chat_id,
                    'text': message
                }
                response = requests.post(self.telegram_api_url, json=data, timeout=10)
                response.raise_for_status()
            return True
            
        except Exception as e:
            logging.error(f"Ошибка тестового Telegram сообщения: {e}")
            return False
