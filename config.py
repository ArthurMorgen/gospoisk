"""
Конфигурационный файл для парсера государственных закупок
"""

# Настройки парсинга
PARSING_CONFIG = {
    'check_interval': 3600,  # Интервал проверки в секундах (1 час)
    'request_delay': 1,     # Задержка между запросами в секундах (уменьшено для быстрой работы бота)
    'timeout': 30,          # Таймаут запроса в секундах
    'max_retries': 3,       # Максимальное количество повторных попыток
    'deadline_warning_days': [5, 6],  # За сколько дней предупреждать о сроках
    'check_deadlines_interval': 3600,  # Проверка дедлайнов каждый час (3600 сек)
}

# URL площадок
PLATFORMS = {
    'eis': {
        'enabled': True,
        'name': 'Единая информационная система',
        'base_url': 'https://zakupki.gov.ru',
        'search_url': 'https://zakupki.gov.ru/epz/order/extendedsearch/results.html'
    },
    'suppliers_portal': {
        'enabled': True,
        'name': 'МосРег (агрегатор всех регионов РФ)',
        'base_url': 'https://old.zakupki.mos.ru',
        'search_url': 'https://old.zakupki.mos.ru/api/Cssp/Purchase/Query',
        'search_params': {
            'filter': {
                'nameLike': {'value': 'keywords', 'contains': True}
            },
            'order': [{'field': 'endDate', 'desc': True}],
            'withCount': True,
            'take': 100,
            'skip': 0
        }
    },
    'rts_tender': {
        'enabled': True,  # ✅ РАБОТАЕТ! (Selenium для обхода Anti-DDoS)
        'name': 'РТС-Тендер (электронная торговая площадка 44-ФЗ/223-ФЗ)',
        'base_url': 'https://www.rts-tender.ru',
        'search_url': 'https://www.rts-tender.ru/poisk/poisk-44-fz/',
        'timeout': 30,
        'use_selenium': True,  # Использовать Selenium для обхода Anti-DDoS
        'html_file': 'debug_rts_tender.html'  # Запасной HTML (если Selenium не работает)
    },
    'suppliers_portal_new': {
        'enabled': True,
        'name': 'Портал поставщиков (Единый реестр закупок)',
        'base_url': 'https://zakupki.mos.ru',
        'search_url_quotations': 'https://zakupki.mos.ru/purchase/list?page=1&perPage=50&sortField=relevance&sortDesc=true&state=%7B%22currentTab%22%3A8%7D',
        'search_url_needs': 'https://zakupki.mos.ru/purchase/list?page=1&perPage=50&sortField=relevance&sortDesc=true&state=%7B%22currentTab%22%3A9%7D',
        'timeout': 60,
        'use_selenium': True
    },
    'roseltorg': {
        'enabled': True,
        'name': 'Росэлторг (44-ФЗ)',
        'base_url': 'https://www.roseltorg.ru',
        'search_url': 'https://www.roseltorg.ru/procedures/search?source%5B%5D=1&place=44fz',
        'timeout': 60,
        'use_selenium': True
    }
}

# Настройки фильтрации
FILTER_CONFIG = {
    'keywords': [
        # ПОЛНЫЙ список нужных ключевых слов (ПРИОРИТЕТ: грамоты первыми!)
        'грамота', 'грамоты', 'грамот', 'грамоте', 'грамотой', 'грамотам', 'грамотами', 'грамотах',
        'журнал', 'журналы', 'журналов', 'журналу', 'журналом', 'журналам', 'журналами', 'журналах',
        'бланк', 'бланки', 'бланков', 'бланку', 'бланком', 'бланкам', 'бланками', 'бланках',
        'диплом', 'дипломы', 'дипломов', 'диплому', 'дипломом', 'дипломам', 'дипломами', 'дипломах',
        'благодарственные письма', 'благодарственное письмо', 'благодарственных писем',
        'благодарность', 'благодарности', 'благодарностей', 'благодарностям', 'благодарностях', 'благодарностями',
        'полиграфическая продукция', 'полиграфической продукции', 'полиграфическую продукцию',
        'типографская продукция', 'типографской продукции', 'типографскую продукцию',
        'типографическая продукция', 'типографической продукции', 'типографическую продукцию',
        'бумажная продукция', 'бумажной продукции', 'бумажную продукцию',
    ],  # Ключевые слова для поиска
    'exclude_keywords': ['ремонт дорог', 'строительство', 'медицинские услуги', 'продукты питания'],  # Исключающие ключевые слова
    'min_price': 0,         # Минимальная цена
    'max_price': None,      # Максимальная цена
    'regions': [],          # Регионы
    'categories': [],       # Категории закупок
    'exclude_finished': True,  # Исключать завершенные тендеры
    'only_active': True,    # Только активные тендеры (с открытой подачей заявок)
    'exclude_statuses': ['Завершен', 'Отменен', 'Не состоялся', 'Закрыт']  # Исключаемые статусы
}

# Настройки уведомлений
NOTIFICATION_CONFIG = {
    'email': {
        'enabled': False,  # Отключены email уведомления
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'username': '',
        'password': '',
        'recipients': []
    },
    'telegram': {
        'enabled': True,   # Включены только Telegram уведомления
        'bot_token': '8257830122:AAG4MPYgELY3x2z9OlNM10YKCPmT_iRcqiw',
        'chat_ids': ['1382173062']
    }
}

# Настройки базы данных
DATABASE_CONFIG = {
    'db_path': 'tenders.db',
    'backup_interval': 86400  # Резервное копирование каждые 24 часа
}

# Настройки логирования
LOGGING_CONFIG = {
    'level': 'DEBUG',
    'file': 'parser.log',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
}
