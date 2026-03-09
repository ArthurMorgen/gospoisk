"""
ТЕСТОВЫЙ бот для проверки нового функционала
Использует тестовый токен из config_test.py
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
from config import PLATFORMS, FILTER_CONFIG
from config_test import NOTIFICATION_CONFIG  # ТЕСТОВЫЙ ТОКЕН!

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

print(f"🧪 ТЕСТОВЫЙ БОТ")
print(f"📌 Токен: {BOT_TOKEN[:20]}...")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start - главное меню"""
    keyboard = [
        [InlineKeyboardButton("📋 ЕИС", callback_data='parse_eis')],
        [InlineKeyboardButton("🏛️ МосРег", callback_data='parse_suppliers')],
        [InlineKeyboardButton("🏢 Портал поставщиков", callback_data='parse_portal_new')],
        [InlineKeyboardButton("🔷 РТС-Тендер", callback_data='parse_rts')],
        [InlineKeyboardButton("🟢 Росэлторг", callback_data='parse_roseltorg')],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = """
🧪 <b>ТЕСТОВЫЙ БОТ - Парсер Госзакупок</b>

Выберите площадку для тестирования:

<b>📋 ЕИС</b> - zakupki.gov.ru
<b>🏛️ МосРег</b> - old.zakupki.mos.ru (API)
<b>🏢 Портал поставщиков</b> - zakupki.mos.ru (Selenium) ✨ НОВЫЙ
<b>🔷 РТС-Тендер</b> - rts-tender.ru
<b>🟢 Росэлторг</b> - roseltorg.ru (44-ФЗ) ✨ НОВЫЙ
    """
    
    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='HTML')


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на кнопки"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'parse_eis':
        await parse_eis_test(query)
    
    elif query.data == 'parse_suppliers':
        await parse_suppliers_test(query)
    
    elif query.data == 'parse_portal_new':
        await parse_portal_new_test(query)
    
    elif query.data == 'parse_rts':
        await parse_rts_test(query)
    
    elif query.data == 'parse_roseltorg':
        await parse_roseltorg_test(query)
    
    elif query.data == 'back_to_menu':
        await show_main_menu(query)


async def parse_eis_test(query):
    """Тест ЕИС"""
    await query.edit_message_text("⏳ Тестирую ЕИС...")
    try:
        tenders = eis_parser.search_tenders(keywords=FILTER_CONFIG.get('keywords'))
        await query.edit_message_text(f"✅ ЕИС: найдено {len(tenders)} тендеров")
    except Exception as e:
        await query.edit_message_text(f"❌ Ошибка ЕИС: {e}")


async def parse_suppliers_test(query):
    """Тест МосРег (API)"""
    await query.edit_message_text("⏳ Тестирую МосРег (API)...")
    try:
        tenders = suppliers_parser.search_tenders(keywords=FILTER_CONFIG.get('keywords'))
        await query.edit_message_text(f"✅ МосРег: найдено {len(tenders)} тендеров")
    except Exception as e:
        await query.edit_message_text(f"❌ Ошибка МосРег: {e}")


async def parse_portal_new_test(query):
    """Тест Портала поставщиков (Selenium)"""
    await query.edit_message_text("⏳ Тестирую Портал поставщиков (Selenium)...\n\n🌐 Это может занять 30-60 секунд...")
    try:
        tenders = suppliers_portal_new_parser.search_tenders(
            keywords=FILTER_CONFIG.get('keywords'),
            max_results=20
        )
        
        if not tenders:
            await query.edit_message_text("❌ Тендеры не найдены. Возможно проблема с Selenium или селекторами.")
            return
        
        # Формируем сообщение
        message = f"✅ <b>Портал поставщиков (Selenium)</b>\n\n"
        message += f"Найдено: <b>{len(tenders)}</b> тендеров\n\n"
        
        for i, tender in enumerate(tenders[:5], 1):
            message += f"{i}. <b>{tender['title'][:60]}...</b>\n"
            if tender.get('tender_type'):
                message += f"   📋 {tender['tender_type']}\n"
            if tender.get('price', 0) > 0:
                message += f"   💰 {tender['price']:,.0f} ₽\n"
            message += f"   🔗 <a href='{tender['url']}'>Открыть</a>\n\n"
        
        keyboard = [[InlineKeyboardButton("🏠 Назад", callback_data='back_to_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML', disable_web_page_preview=True)
        
    except Exception as e:
        logger.error(f"Ошибка: {e}", exc_info=True)
        await query.edit_message_text(f"❌ Ошибка Портала: {e}")


async def parse_rts_test(query):
    """Тест РТС-Тендер"""
    await query.edit_message_text("⏳ Тестирую РТС-Тендер...")
    try:
        tenders = rts_parser.search_tenders(keywords=FILTER_CONFIG.get('keywords'), max_results=10)
        await query.edit_message_text(f"✅ РТС-Тендер: найдено {len(tenders)} тендеров")
    except Exception as e:
        await query.edit_message_text(f"❌ Ошибка РТС: {e}")


async def parse_roseltorg_test(query):
    """Тест Росэлторг"""
    await query.edit_message_text("⏳ Тестирую Росэлторг (Selenium)...\n\n🌐 Это может занять 30-60 секунд...")
    try:
        tenders = roseltorg_parser.search_tenders(keywords=FILTER_CONFIG.get('keywords'))
        
        if not tenders:
            await query.edit_message_text("❌ Тендеры не найдены. Возможно проблема с Selenium или селекторами.")
            return
        
        # Формируем сообщение
        message = f"✅ <b>Росэлторг (44-ФЗ)</b>\n\n"
        message += f"Найдено: <b>{len(tenders)}</b> тендеров\n\n"
        
        for i, tender in enumerate(tenders[:5], 1):
            message += f"{i}. <b>{tender['title'][:60]}...</b>\n"
            if tender.get('tender_type'):
                message += f"   📋 {tender['tender_type']}\n"
            if tender.get('price', 0) > 0:
                message += f"   💰 {tender['price']:,.0f} ₽\n"
            message += f"   🔗 <a href='{tender['url']}'>Открыть</a>\n\n"
        
        keyboard = [[InlineKeyboardButton("🏠 Назад", callback_data='back_to_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML', disable_web_page_preview=True)
        
    except Exception as e:
        logger.error(f"Ошибка Росэлторг: {e}", exc_info=True)
        await query.edit_message_text(f"❌ Ошибка Росэлторг: {e}")


async def show_main_menu(query):
    """Показать главное меню"""
    keyboard = [
        [InlineKeyboardButton("📋 ЕИС", callback_data='parse_eis')],
        [InlineKeyboardButton("🏛️ МосРег", callback_data='parse_suppliers')],
        [InlineKeyboardButton("🏢 Портал поставщиков", callback_data='parse_portal_new')],
        [InlineKeyboardButton("🔷 РТС-Тендер", callback_data='parse_rts')],
        [InlineKeyboardButton("🟢 Росэлторг", callback_data='parse_roseltorg')],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = """
🧪 <b>ТЕСТОВЫЙ БОТ - Парсер Госзакупок</b>

Выберите площадку для тестирования:
    """
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')


def main():
    """Запуск тестового бота"""
    logger.info("🧪 Запуск ТЕСТОВОГО бота...")
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    logger.info("🧪 ТЕСТОВЫЙ бот запущен! Напишите /start в Telegram")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
