"""
Интерактивный Telegram бот с кнопками для парсинга по запросу
"""

import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from parsers import EISParser, SuppliersPortalParser
from parsers.rts_tender_parser import RTSTenderParser
from parsers.suppliers_portal_selenium_parser import SuppliersPortalSeleniumParser
from parsers.roseltorg_parser import RoseltorgParser
from database import TenderDatabase
from config import PLATFORMS, FILTER_CONFIG, NOTIFICATION_CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация
db = TenderDatabase()
eis_parser = EISParser(PLATFORMS['eis'])
suppliers_parser = SuppliersPortalParser(PLATFORMS['suppliers_portal'])
rts_parser = RTSTenderParser(PLATFORMS['rts_tender'])
suppliers_portal_new_parser = SuppliersPortalSeleniumParser(PLATFORMS['suppliers_portal_new'])
roseltorg_parser = RoseltorgParser()

BOT_TOKEN = NOTIFICATION_CONFIG['telegram']['bot_token']
# CHAT_ID не нужен для интерактивного бота - он берется из update.message.chat_id


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start - главное меню"""
    keyboard = [
        [
            InlineKeyboardButton("📋 ЕИС", callback_data='parse_eis'),
        ],
        [
            InlineKeyboardButton("🏛️ МосРег", callback_data='parse_suppliers'),
        ],
        [
            InlineKeyboardButton("🏢 Портал поставщиков", callback_data='parse_portal_new'),
        ],
        [
            InlineKeyboardButton("🔷 РТС-Тендер", callback_data='parse_rts'),
        ],
        [
            InlineKeyboardButton("🟢 Росэлторг", callback_data='parse_roseltorg'),
        ],
        [
            InlineKeyboardButton("🎯 Оценка тендеров", callback_data='review_mode'),
        ],
        [
            InlineKeyboardButton("⭐ Избранное", callback_data='show_favorites'),
        ],
        [
            InlineKeyboardButton("📊 Статистика", callback_data='stats'),
        ],
        [
            InlineKeyboardButton("🗑️ Очистка БД", callback_data='clear_db'),
        ],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = """
🤖 <b>Парсер Госзакупок</b>

Выберите площадку для получения актуальных тендеров:

<b>📋 ЕИС</b> - zakupki.gov.ru ✅
<b>🏛️ МосРег</b> - Все регионы РФ ✅
<b>🔷 РТС-Тендер</b> - Электронная площадка 44-ФЗ ✅
<b>🟢 Росэлторг</b> - roseltorg.ru 44-ФЗ ✅
    """
    
    await update.message.reply_text(
        text,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на кнопки"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'parse_eis':
        await parse_eis_interactive(query)
    
    elif query.data == 'parse_suppliers':
        await parse_suppliers_interactive(query)
    
    elif query.data == 'parse_portal_new':
        await parse_portal_new_interactive(query)
    
    elif query.data.startswith('portal_page_'):
        page = int(query.data.split('_')[-1])
        await parse_portal_new_interactive(query, page=page)
    
    elif query.data == 'stats':
        await show_statistics(query)
    
    elif query.data == 'back_to_menu':
        await show_main_menu(query)
    
    elif query.data.startswith('eis_page_'):
        page = int(query.data.split('_')[-1])
        await parse_eis_interactive(query, page=page)
    
    elif query.data.startswith('suppliers_page_'):
        page = int(query.data.split('_')[-1])
        await parse_suppliers_interactive(query, page=page)
    
    elif query.data == 'parse_rts':
        await parse_rts_interactive(query)
    
    elif query.data.startswith('rts_page_'):
        page = int(query.data.split('_')[-1])
        await parse_rts_interactive(query, page=page)
    
    elif query.data == 'parse_roseltorg':
        await parse_roseltorg_interactive(query)
    
    elif query.data.startswith('roseltorg_page_'):
        page = int(query.data.split('_')[-1])
        await parse_roseltorg_interactive(query, page=page)
    
    elif query.data == 'review_mode':
        await review_mode_menu(query)
    
    elif query.data == 'review_start_eis':
        await start_review(query, 'eis')
    
    elif query.data == 'review_start_suppliers':
        await start_review(query, 'suppliers')
    
    elif query.data == 'review_start_rts':
        await start_review(query, 'rts')
    
    elif query.data == 'review_start_portal_new':
        await start_review(query, 'portal_new')
    
    elif query.data.startswith('review_'):
        # review_ignore_ID или review_favorite_ID или review_skip_ID
        action_parts = query.data.split('_')
        action = action_parts[1]  # ignore/favorite/skip
        tender_idx = int(action_parts[2])
        await handle_review_action(query, action, tender_idx)
    
    elif query.data == 'show_favorites':
        await show_favorites(query)
    
    elif query.data.startswith('fav_delete_'):
        tender_id = query.data.replace('fav_delete_', '')
        await delete_favorite(query, tender_id)
    
    elif query.data == 'clear_db':
        await confirm_clear_db(query)
    
    elif query.data == 'clear_db_confirm':
        await clear_database(query)
    
    elif query.data == 'clear_db_cancel':
        await show_main_menu(query)


async def parse_eis_interactive(query, page=0):
    """Парсинг ЕИС по кнопке с листанием"""
    await query.edit_message_text("⏳ Парсю ЕИС... Подождите немного...")
    
    try:
        # Парсим тендеры
        tenders = eis_parser.search_tenders(
            keywords=FILTER_CONFIG.get('keywords'),
            filters=FILTER_CONFIG
        )
        
        filtered_tenders = eis_parser.filter_tenders(tenders, FILTER_CONFIG)
        
        if not filtered_tenders:
            keyboard = [[InlineKeyboardButton("🏠 Главное меню", callback_data='back_to_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "❌ Новых тендеров не найдено",
                reply_markup=reply_markup
            )
            return
        
        # Pagination
        items_per_page = 5
        start_idx = page * items_per_page
        end_idx = start_idx + items_per_page
        page_tenders = filtered_tenders[start_idx:end_idx]
        total_pages = (len(filtered_tenders) + items_per_page - 1) // items_per_page
        
        # Формируем сообщение
        message = f"✅ <b>ЕИС: {len(filtered_tenders)} тендеров (стр. {page + 1}/{total_pages})</b>\n\n"
        
        for i, tender in enumerate(page_tenders, start_idx + 1):
            message += f"{i}. <b>{tender['title'][:70]}...</b>\n"
            price = tender.get('price', 'Не указана')
            message += f"💰 {price}\n"
            message += f"🔗 <a href='{tender['url']}'>Открыть</a>\n\n"
        
        # Кнопки навигации
        keyboard = []
        nav_buttons = []
        
        if page > 0:
            nav_buttons.append(InlineKeyboardButton("◀️ Назад", callback_data=f'eis_page_{page-1}'))
        if end_idx < len(filtered_tenders):
            nav_buttons.append(InlineKeyboardButton("Вперед ▶️", callback_data=f'eis_page_{page+1}'))
        
        if nav_buttons:
            keyboard.append(nav_buttons)
        
        keyboard.append([InlineKeyboardButton("🏠 Главное меню", callback_data='back_to_menu')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode='HTML',
            disable_web_page_preview=True
        )
        
    except Exception as e:
        logger.error(f"Ошибка парсинга ЕИС: {e}")
        await query.edit_message_text(f"❌ Ошибка: {str(e)}")


async def parse_suppliers_interactive(query, page=0):
    """Парсинг портала поставщиков (котировочные сессии) по кнопке с листанием"""
    await query.edit_message_text("⏳ Парсю котировочные сессии... Подождите...")
    
    try:
        # Парсим котировочные сессии
        tenders = suppliers_parser.search_tenders(
            keywords=FILTER_CONFIG.get('keywords'),
            filters=FILTER_CONFIG
        )
        
        filtered_tenders = suppliers_parser.filter_tenders(tenders, FILTER_CONFIG)
        
        if not filtered_tenders:
            keyboard = [[InlineKeyboardButton("🏠 Главное меню", callback_data='back_to_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "❌ Активных котировок не найдено",
                reply_markup=reply_markup
            )
            return
        
        # Pagination
        items_per_page = 5
        start_idx = page * items_per_page
        end_idx = start_idx + items_per_page
        page_tenders = filtered_tenders[start_idx:end_idx]
        total_pages = (len(filtered_tenders) + items_per_page - 1) // items_per_page
        
        # Формируем сообщение
        message = f"✅ <b>Портал: {len(filtered_tenders)} активных котировок (стр. {page + 1}/{total_pages})</b>\n\n"
        
        for i, tender in enumerate(page_tenders, start_idx + 1):
            message += f"{i}. <b>{tender['title'][:70]}...</b>\n"
            price = tender.get('price', 0)
            if price > 0:
                message += f"💰 {price:,.0f} ₽\n"
            else:
                message += f"💰 Не указана\n"
            message += f"🔗 <a href='{tender['url']}'>Открыть</a>\n\n"
        
        # Кнопки навигации
        keyboard = []
        nav_buttons = []
        
        if page > 0:
            nav_buttons.append(InlineKeyboardButton("◀️ Назад", callback_data=f'suppliers_page_{page-1}'))
        if end_idx < len(filtered_tenders):
            nav_buttons.append(InlineKeyboardButton("Вперед ▶️", callback_data=f'suppliers_page_{page+1}'))
        
        if nav_buttons:
            keyboard.append(nav_buttons)
        
        keyboard.append([InlineKeyboardButton("🏠 Главное меню", callback_data='back_to_menu')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode='HTML',
            disable_web_page_preview=True
        )
        
    except Exception as e:
        logger.error(f"Ошибка парсинга портала поставщиков: {e}")
        await query.edit_message_text(f"❌ Ошибка: {str(e)}")


async def show_statistics(query):
    """Показать статистику"""
    try:
        stats = db.get_statistics()
        
        message = f"""
📊 <b>Статистика парсера</b>

📦 Всего тендеров: {stats.get('total_tenders', 0)}
🆕 Новых (необработанных): {stats.get('new_tenders', 0)}
✅ Обработанных: {stats.get('processed_tenders', 0)}

<b>По площадкам:</b>
{_format_platform_stats(stats.get('by_platform', {}))}
        """
        
        keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data='back_to_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
        
    except Exception as e:
        await query.edit_message_text(f"❌ Ошибка получения статистики: {str(e)}")


async def parse_rts_interactive(query, page=0):
    """Парсинг РТС-Тендер по кнопке с листанием"""
    await query.edit_message_text("⏳ Парсю РТС-Тендер... Подождите...")
    
    try:
        # Парсим тендеры
        tenders = rts_parser.search_tenders(
            keywords=FILTER_CONFIG.get('keywords'),
            max_results=50
        )
        
        # Фильтруем тендеры (по ключевым словам, дедлайну и дубликатам)
        from datetime import datetime
        
        filtered_tenders = []
        seen_ids = set()
        current_date = datetime.now()
        keywords = FILTER_CONFIG.get('keywords', [])
        
        for tender in tenders:
            # Пропускаем дубликаты
            tender_id = tender.get('tender_id', '')
            if tender_id and tender_id in seen_ids:
                continue
            if tender_id:
                seen_ids.add(tender_id)
            
            # Проверяем дедлайн
            deadline_str = tender.get('deadline', '')
            if deadline_str:
                try:
                    deadline_dt = datetime.strptime(deadline_str.split(' ')[0], '%d.%m.%Y')
                    if deadline_dt <= current_date:
                        continue  # Просроченный тендер
                except:
                    pass  # Если не удалось распарсить - оставляем
            
            # Фильтруем по ключевым словам
            title_lower = tender.get('title', '').lower()
            if not any(keyword.lower() in title_lower for keyword in keywords):
                continue  # Нет ни одного ключевого слова в названии
            
            filtered_tenders.append(tender)
        
        if not filtered_tenders:
            keyboard = [[InlineKeyboardButton("🏠 Главное меню", callback_data='back_to_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "❌ Новых тендеров не найдено\n\n💡 Если используется сохраненный HTML, обновите его:"
                "\n1. Откройте https://www.rts-tender.ru/poisk/poisk-44-fz/"
                "\n2. Нажмите Ctrl+S и сохраните как debug_rts_tender.html",
                reply_markup=reply_markup
            )
            return
        
        # Pagination
        items_per_page = 5
        start_idx = page * items_per_page
        end_idx = start_idx + items_per_page
        page_tenders = filtered_tenders[start_idx:end_idx]
        total_pages = (len(filtered_tenders) + items_per_page - 1) // items_per_page
        
        # Формируем сообщение
        message = f"✅ <b>РТС-Тендер: {len(filtered_tenders)} тендеров (стр. {page + 1}/{total_pages})</b>\n\n"
        
        for i, tender in enumerate(page_tenders, start_idx + 1):
            message += f"{i}. <b>{tender['title'][:70]}...</b>\n"
            # Тип закупки
            tender_type = tender.get('tender_type', '')
            if tender_type:
                message += f"📋 {tender_type}\n"
            # Цена
            price = tender.get('price', 0)
            if price > 0:
                message += f"💰 {price:,.0f} ₽\n"
            else:
                message += f"💰 Не указана\n"
            # Дедлайн
            deadline = tender.get('deadline', '')
            if deadline:
                message += f"⏰ До {deadline}\n"
            message += f"🔗 <a href='{tender['url']}'>Открыть</a>\n\n"
        
        # Кнопки навигации
        keyboard = []
        nav_buttons = []
        
        if page > 0:
            nav_buttons.append(InlineKeyboardButton("◀️ Назад", callback_data=f'rts_page_{page-1}'))
        if end_idx < len(filtered_tenders):
            nav_buttons.append(InlineKeyboardButton("Вперед ▶️", callback_data=f'rts_page_{page+1}'))
        
        if nav_buttons:
            keyboard.append(nav_buttons)
        
        keyboard.append([InlineKeyboardButton("🏠 Главное меню", callback_data='back_to_menu')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode='HTML',
            disable_web_page_preview=True
        )
        
    except Exception as e:
        logger.error(f"Ошибка парсинга РТС-Тендер: {e}")
        await query.edit_message_text(f"❌ Ошибка: {str(e)}")


async def parse_portal_new_interactive(query, page=0):
    """Парсинг Портала поставщиков по кнопке с пагинацией"""
    await query.edit_message_text("⏳ Парсю Портал поставщиков... Подождите немного...")
    
    try:
        # Парсим тендеры
        tenders = suppliers_portal_new_parser.search_tenders(
            keywords=FILTER_CONFIG.get('keywords'),
            max_results=100
        )
        
        if not tenders:
            keyboard = [[InlineKeyboardButton("🏠 Главное меню", callback_data='back_to_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "❌ Новых тендеров не найдено",
                reply_markup=reply_markup
            )
            return
        
        # Сохраняем в БД
        for tender in tenders:
            db.add_tender(tender)
        
        # Пагинация
        items_per_page = 5
        start_idx = page * items_per_page
        end_idx = start_idx + items_per_page
        page_tenders = tenders[start_idx:end_idx]
        total_pages = (len(tenders) + items_per_page - 1) // items_per_page
        
        # Формируем сообщение
        message = f"🏢 <b>Портал поставщиков: {len(tenders)} тендеров (стр. {page + 1}/{total_pages})</b>\n\n"
        
        for i, tender in enumerate(page_tenders, start_idx + 1):
            message += f"{i}. <b>{tender['title'][:70]}...</b>\n"
            
            if tender.get('tender_type'):
                message += f"📋 {tender['tender_type']}\n"
            
            price = tender.get('price', 0)
            if price > 0:
                message += f"💰 {price:,.0f} ₽\n"
            
            customer = tender.get('customer', '')
            if customer:
                message += f"🏛️ {customer[:40]}\n"
            
            deadline = tender.get('deadline', '')
            if deadline:
                message += f"⏰ {deadline}\n"
            
            message += f"🔗 <a href='{tender['url']}'>Открыть</a>\n\n"
        
        # Кнопки навигации
        keyboard = []
        nav_buttons = []
        
        if page > 0:
            nav_buttons.append(InlineKeyboardButton("◀️ Назад", callback_data=f'portal_page_{page-1}'))
        if end_idx < len(tenders):
            nav_buttons.append(InlineKeyboardButton("Вперед ▶️", callback_data=f'portal_page_{page+1}'))
        
        if nav_buttons:
            keyboard.append(nav_buttons)
        
        keyboard.append([InlineKeyboardButton("🏠 Главное меню", callback_data='back_to_menu')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML', disable_web_page_preview=True)
        
    except Exception as e:
        logger.error(f"Ошибка при парсинге Портала поставщиков: {e}", exc_info=True)
        await query.edit_message_text(f"❌ Ошибка: {str(e)}")


async def parse_roseltorg_interactive(query, page=0):
    """Парсинг Росэлторг по кнопке с листанием"""
    await query.edit_message_text("⏳ Парсю Росэлторг... Подождите...")
    
    try:
        tenders = roseltorg_parser.search_tenders()
        
        if not tenders:
            keyboard = [[InlineKeyboardButton("🏠 Главное меню", callback_data='back_to_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "❌ Новых тендеров не найдено",
                reply_markup=reply_markup
            )
            return
        
        # Сохраняем в БД
        for tender in tenders:
            db.add_tender(tender)
        
        # Pagination
        items_per_page = 5
        start_idx = page * items_per_page
        end_idx = start_idx + items_per_page
        page_tenders = tenders[start_idx:end_idx]
        total_pages = (len(tenders) + items_per_page - 1) // items_per_page
        
        message = f"🟢 <b>Росэлторг: {len(tenders)} тендеров (стр. {page + 1}/{total_pages})</b>\n\n"
        
        for i, tender in enumerate(page_tenders, start_idx + 1):
            message += f"{i}. <b>{tender['title'][:70]}...</b>\n"
            if tender.get('tender_type'):
                message += f"📋 {tender['tender_type']}\n"
            message += f"🔗 <a href='{tender['url']}'>Открыть</a>\n\n"
        
        keyboard = []
        nav_buttons = []
        
        if page > 0:
            nav_buttons.append(InlineKeyboardButton("◀️ Назад", callback_data=f'roseltorg_page_{page-1}'))
        if end_idx < len(tenders):
            nav_buttons.append(InlineKeyboardButton("Вперед ▶️", callback_data=f'roseltorg_page_{page+1}'))
        
        if nav_buttons:
            keyboard.append(nav_buttons)
        
        keyboard.append([InlineKeyboardButton("🏠 Главное меню", callback_data='back_to_menu')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode='HTML',
            disable_web_page_preview=True
        )
        
    except Exception as e:
        logger.error(f"Ошибка парсинга Росэлторг: {e}")
        await query.edit_message_text(f"❌ Ошибка: {str(e)}")


async def show_main_menu(query):
    """Показать главное меню"""
    keyboard = [
        [
            InlineKeyboardButton("📋 ЕИС", callback_data='parse_eis'),
        ],
        [
            InlineKeyboardButton("🏛️ МосРег", callback_data='parse_suppliers'),
        ],
        [
            InlineKeyboardButton("🏢 Портал поставщиков", callback_data='parse_portal_new'),
        ],
        [
            InlineKeyboardButton("🔷 РТС-Тендер", callback_data='parse_rts'),
        ],
        [
            InlineKeyboardButton("🟢 Росэлторг", callback_data='parse_roseltorg'),
        ],
        [
            InlineKeyboardButton("🎯 Оценка тендеров", callback_data='review_mode'),
        ],
        [
            InlineKeyboardButton("⭐ Избранное", callback_data='show_favorites'),
        ],
        [
            InlineKeyboardButton("📊 Статистика", callback_data='stats'),
        ],
        [
            InlineKeyboardButton("🗑️ Очистка БД", callback_data='clear_db'),
        ],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = """
🤖 <b>Парсер Госзакупок</b>

Выберите площадку для получения актуальных тендеров:

<b>📋 ЕИС</b> - zakupki.gov.ru ✅
<b>🏛️ МосРег</b> - Все регионы РФ ✅
<b>🔷 РТС-Тендер</b> - Электронная площадка 44-ФЗ ✅
<b>🟢 Росэлторг</b> - roseltorg.ru 44-ФЗ ✅
    """
    
    await query.edit_message_text(
        text,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )


def _format_platform_stats(platform_stats):
    """Форматирование статистики по площадкам"""
    if not platform_stats:
        return "Нет данных"
    
    lines = []
    for platform, count in platform_stats.items():
        lines.append(f"• {platform}: {count}")
    
    return "\n".join(lines)


# ========== РЕЖИМ ОЦЕНКИ ТЕНДЕРОВ ==========

# Временное хранилище тендеров для оценки (chat_id -> список тендеров)
review_tenders = {}
review_indices = {}


async def review_mode_menu(query):
    """Меню выбора площадки для оценки"""
    keyboard = [
        [InlineKeyboardButton("📋 ЕИС", callback_data='review_start_eis')],
        [InlineKeyboardButton("🏛️ МосРег", callback_data='review_start_suppliers')],
        [InlineKeyboardButton("🏢 Портал поставщиков", callback_data='review_start_portal_new')],
        [InlineKeyboardButton("🔷 РТС-Тендер", callback_data='review_start_rts')],
        [InlineKeyboardButton("◀️ Назад", callback_data='back_to_menu')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = """
🎯 <b>Режим оценки тендеров</b>

Выберите площадку для оценки тендеров по одному:

<b>Управление:</b>
❌ <b>Кал</b> - больше не показывать
✅ <b>Играть</b> - добавить в избранное
⏭️ <b>Пропустить</b> - оценить позже
    """
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')


async def start_review(query, platform='rts'):
    """Начать оценку тендеров выбранной площадки"""
    chat_id = query.message.chat_id
    await query.edit_message_text("⏳ Загружаю тендеры...")
    
    try:
        # Получаем тендеры с выбранной площадки
        if platform == 'eis':
            all_tenders = eis_parser.search_tenders(
                keywords=FILTER_CONFIG.get('keywords')
            )
        elif platform == 'suppliers':
            all_tenders = suppliers_parser.search_tenders(
                keywords=FILTER_CONFIG.get('keywords')
            )
        elif platform == 'portal_new':
            all_tenders = suppliers_portal_new_parser.search_tenders(
                keywords=FILTER_CONFIG.get('keywords'),
                max_results=100
            )
        else:  # rts
            all_tenders = rts_parser.search_tenders(
                keywords=FILTER_CONFIG.get('keywords'),
                max_results=100
            )
        
        if not all_tenders:
            await query.edit_message_text(
                "❌ Тендеры не найдены\n\n◀️ /start - В главное меню"
            )
            return
        
        # Фильтруем: убираем уже отклоненные и уже в избранном
        new_tenders = []
        for tender in all_tenders:
            tender_id = tender.get('tender_id', '')
            if not db.is_ignored(tender_id) and not db.is_favorite(tender_id):
                new_tenders.append(tender)
        
        # Сортировка: грамоты первыми!
        def tender_priority(tender):
            """Определяет приоритет тендера (меньше = выше приоритет)"""
            title_lower = tender.get('title', '').lower()
            if 'грамот' in title_lower:
                return 0  # Высший приоритет
            elif 'благодар' in title_lower or 'диплом' in title_lower:
                return 1  # Средний приоритет
            else:
                return 2  # Обычный приоритет
        
        new_tenders.sort(key=tender_priority)
        
        if not new_tenders:
            await query.edit_message_text(
                "✅ Все тендеры уже оценены!\n\n◀️ /start - В главное меню"
            )
            return
        
        # Сохраняем список тендеров для этого чата
        review_tenders[chat_id] = new_tenders
        review_indices[chat_id] = 0
        
        # Показываем первый тендер
        await show_review_tender(query, chat_id)
        
    except Exception as e:
        logger.error(f"Ошибка запуска оценки: {e}")
        await query.edit_message_text(f"❌ Ошибка: {str(e)}\n\n◀️ /start")


async def show_review_tender(query, chat_id):
    """Показать текущий тендер для оценки"""
    tenders = review_tenders.get(chat_id, [])
    idx = review_indices.get(chat_id, 0)
    
    if idx >= len(tenders):
        # Все тендеры оценены
        del review_tenders[chat_id]
        del review_indices[chat_id]
        await query.edit_message_text(
            "🎉 <b>Все тендеры оценены!</b>\n\n◀️ /start - В главное меню",
            parse_mode='HTML'
        )
        return
    
    tender = tenders[idx]
    
    # Формируем сообщение
    message = f"🎯 <b>Тендер {idx + 1}/{len(tenders)}</b>\n\n"
    message += f"<b>{tender['title']}</b>\n\n"
    
    tender_type = tender.get('tender_type', '')
    if tender_type:
        message += f"📋 {tender_type}\n"
    
    price = tender.get('price', 0)
    if price > 0:
        message += f"💰 {price:,.0f} ₽\n"
    
    deadline = tender.get('deadline', '')
    if deadline:
        message += f"⏰ До {deadline}\n"
    
    message += f"🔗 <a href='{tender['url']}'>Открыть тендер</a>"
    
    # Кнопки оценки
    keyboard = [
        [
            InlineKeyboardButton("❌ Кал", callback_data=f'review_ignore_{idx}'),
            InlineKeyboardButton("✅ Играть", callback_data=f'review_favorite_{idx}'),
        ],
        [
            InlineKeyboardButton("⏭️ Пропустить", callback_data=f'review_skip_{idx}'),
        ],
        [
            InlineKeyboardButton("◀️ Выйти", callback_data='back_to_menu'),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')


async def handle_review_action(query, action, tender_idx):
    """Обработка оценки тендера"""
    chat_id = query.message.chat_id
    tenders = review_tenders.get(chat_id, [])
    
    if tender_idx >= len(tenders):
        await query.answer("❌ Ошибка: тендер не найден")
        return
    
    tender = tenders[tender_idx]
    
    if action == 'ignore':
        # Добавляем в отклоненные
        db.ignore_tender(tender)
        await query.answer("❌ Тендер отклонен")
        review_indices[chat_id] = tender_idx + 1
        await show_review_tender(query, chat_id)
    
    elif action == 'favorite':
        # Добавляем в избранное
        db.add_to_favorites(tender)
        await query.answer("✅ Добавлено в избранное!")
        review_indices[chat_id] = tender_idx + 1
        await show_review_tender(query, chat_id)
    
    elif action == 'skip':
        # Просто переходим к следующему
        await query.answer("⏭️ Пропущено")
        review_indices[chat_id] = tender_idx + 1
        await show_review_tender(query, chat_id)


async def show_favorites(query):
    """Показать список избранных тендеров"""
    favorites = db.get_favorites()
    
    if not favorites:
        keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data='back_to_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "⭐ <b>Избранное пусто</b>\n\nНачните оценивать тендеры!",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
        return
    
    # Формируем сообщение и кнопки удаления
    message = f"⭐ <b>Избранное: {len(favorites)} тендеров</b>\n\n"
    keyboard = []
    
    for i, tender in enumerate(favorites[:10], 1):  # Показываем первые 10
        message += f"{i}. <b>{tender['title'][:60]}...</b>\n"
        
        price = tender.get('price', 0)
        if price > 0:
            message += f"💰 {price:,.0f} ₽\n"
        
        deadline = tender.get('deadline', '')
        if deadline:
            message += f"⏰ {deadline}\n"
        
        message += f"🔗 <a href='{tender['url']}'>Открыть</a>\n\n"
        
        # Добавляем кнопку удаления для каждого тендера
        keyboard.append([InlineKeyboardButton(
            f"🗑️ Удалить #{i}", 
            callback_data=f"fav_delete_{tender['tender_id']}"
        )])
    
    if len(favorites) > 10:
        message += f"\n...и еще {len(favorites) - 10} тендеров"
    
    keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data='back_to_menu')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')


async def delete_favorite(query, tender_id):
    """Удалить тендер из избранного"""
    if db.remove_from_favorites(tender_id):
        await query.answer("🗑️ Удалено из избранного")
    else:
        await query.answer("❌ Ошибка удаления")
    
    # Обновляем список
    await show_favorites(query)


async def confirm_clear_db(query):
    """Подтверждение очистки базы данных"""
    keyboard = [
        [InlineKeyboardButton("✅ Да, очистить", callback_data='clear_db_confirm')],
        [InlineKeyboardButton("❌ Отмена", callback_data='clear_db_cancel')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = """
⚠️ <b>ВНИМАНИЕ!</b>

Вы уверены, что хотите очистить всю базу данных?

Это удалит:
• Все найденные тендеры
• Все отклоненные тендеры
• Все избранные тендеры
• Всю историю уведомлений

<b>Это действие необратимо!</b>
    """
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')


async def clear_database(query):
    """Очистить базу данных"""
    await query.edit_message_text("⏳ Очищаю базу данных...")
    
    if db.clear_all_data():
        await query.edit_message_text("✅ База данных успешно очищена!")
        await asyncio.sleep(2)
    else:
        await query.edit_message_text("❌ Ошибка при очистке базы данных!")
        await asyncio.sleep(2)
    
    # Возвращаем в главное меню
    await show_main_menu(query)


def main():
    """Запуск интерактивного бота"""
    logger.info("Запуск интерактивного Telegram бота...")
    
    # Создаем приложение
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Добавляем обработчики
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    # Запускаем бота
    logger.info("Бот запущен! Напишите /start в Telegram")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
