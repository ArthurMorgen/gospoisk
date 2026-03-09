"""
ТЕСТОВАЯ конфигурация с тестовым ботом
Запуск: python bot_test.py
"""

# Импортируем основную конфигурацию
from config import PARSING_CONFIG, PLATFORMS, FILTER_CONFIG

# Переопределяем только токен бота
NOTIFICATION_CONFIG = {
    'email': {
        'enabled': False,
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'sender_email': '',
        'sender_password': '',
        'recipient_emails': []
    },
    'telegram': {
        'enabled': True,
        'bot_token': '8368209626:AAHJhlvpGlMDMABpu7QMhd2sbw10iE3mQWg',  # ТЕСТОВЫЙ БОТ
        'chat_ids': []
    }
}
