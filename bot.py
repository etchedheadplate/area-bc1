import logging
from telegram import InlineQueryResultArticle, InputTextMessageContent, Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import InlineQueryHandler, filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes
from api.tgtoken import api_token
from btc_data import build_api_url, get_json_data, view_json_contents, data_source

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# States constants
CURRENT_INFO, PERIOD_CHANGES, SETTINGS = range(3)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hi! We have started",
        reply_markup=main_menu_keyboard())

async def current_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
     data_text = data_source
     await context.bot.send_message(chat_id=update.effective_chat.id, text=data_text,
        reply_markup=main_menu_keyboard())

async def period_changes(update: Update, context: ContextTypes.DEFAULT_TYPE):
     await context.bot.send_message(chat_id=update.effective_chat.id, text="Period changes section",
        reply_markup=main_menu_keyboard())

async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
     await context.bot.send_message(chat_id=update.effective_chat.id, text="Settings section",
        reply_markup=main_menu_keyboard())

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")

# Keyboard with main menu
def main_menu_keyboard():
    keyboard = [
        [KeyboardButton("Current info")],
        [KeyboardButton("Period changes")],
        [KeyboardButton("Settings")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

if __name__ == '__main__':
    application = ApplicationBuilder().token(api_token).build()
    
    start_handler = CommandHandler('start', start)
    current_info_handler = CommandHandler('current_info', current_info)
    period_changes_handler = MessageHandler('period_changes', period_changes)
    settings_handler = MessageHandler('settings', settings)
    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    
    application.add_handler(start_handler)
    application.add_handler(current_info_handler)
    application.add_handler(period_changes_handler)
    application.add_handler(settings_handler)
    application.add_handler(unknown_handler)

    application.run_polling()