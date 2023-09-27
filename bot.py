import logging
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes, CallbackContext, CallbackQueryHandler
from api.telegram import api_token
from market_values import data_source

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# States constants
CURRENT_INFO, PERIOD_CHANGES, SETTINGS = range(3)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start_text = "Start text as a variable"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=start_text,
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
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

def button_click(update: Update, context: CallbackContext):
    query = update.callback_query
    callback_data = query.data

    if callback_data == "current_info":
        current_info(update, context)

if __name__ == '__main__':
    application = ApplicationBuilder().token(api_token).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button_click))
    application.add_handler(CommandHandler('current_info', current_info))
    application.add_handler(MessageHandler('period_changes', period_changes))
    application.add_handler(MessageHandler('settings', settings))
    application.add_handler(MessageHandler(filters.COMMAND, unknown))

    application.run_polling()