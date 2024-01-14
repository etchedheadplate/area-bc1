import logging
import os
from telegram import ParseMode
from telegram.ext import Updater, ConversationHandler, CommandHandler, MessageHandler, Filters

import config
from api.telegram import TOKEN
from market import make_plot, write_history_values


# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# States:
CHOOSE_DAYS = range(1)


def start(update, context):

    welcome_message = "Use menu button"
    update.message.reply_text(welcome_message)
    logger.info("Start command processed")
    return ConversationHandler.END


def market(update, context):

    path = config.databases['market_latest_chart']['file']['path']
    plot = path + 'latest_plot.png'
    values = path + 'latest_values.md'
    with open(plot, 'rb') as img_file:
        with open(values, 'r') as text_file:
            img_data = img_file.read()
            text_caption = text_file.read()
            context.bot.send_photo(chat_id=update.effective_chat.id,
                                   photo=img_data,
                                   caption=text_caption,
                                   parse_mode=ParseMode.MARKDOWN)
    logger.info("Market command processed")
    return ConversationHandler.END


def history(update, context):
    
    history_message = "How many days to the past?"
    update.message.reply_text(history_message)
    logger.info("History command processed")
    return CHOOSE_DAYS


def network(update, context):

    path = config.databases['network_history_chart']['file']['path']
    plot = path + 'network_history_plot.png'
    values = path + 'network_latest_values.md'
    with open(plot, 'rb') as img_file:
        with open(values, 'r') as text_file:
            img_data = img_file.read()
            text_caption = text_file.read()
            context.bot.send_photo(chat_id=update.effective_chat.id,
                                   photo=img_data,
                                   caption=text_caption,
                                   parse_mode=ParseMode.MARKDOWN)
    logger.info("Network command processed")
    return ConversationHandler.END


def lightning(update, context):

    path = config.databases['lightning_history_chart']['file']['path']
    plot = path + 'lightning_history_plot.png'
    values = path + 'lightning_latest_values.md'
    with open(plot, 'rb') as img_file:
        with open(values, 'r') as text_file:
            img_data = img_file.read()
            text_caption = text_file.read()
            context.bot.send_photo(chat_id=update.effective_chat.id,
                                   photo=img_data,
                                   caption=text_caption,
                                   parse_mode=ParseMode.MARKDOWN)
    logger.info("Lightning command processed")
    return ConversationHandler.END


def settings(update, context):

    settings_message = "settings state"
    update.message.reply_text(settings_message)
    logger.info("Settings command processed")
    return ConversationHandler.END


def about(update, context):

    about_file = 'src/text/about.md'
    with open(about_file, 'r') as about_text:
        about_message = about_text.read()
        update.message.reply_text(about_message, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
    logger.info("About command processed")
    return ConversationHandler.END


def handle_days(update, context):

    user_message = update.message.text
    if user_message.isdigit():
        if user_message == '1':
            user_number = 'latest'
        else:
            user_number = int(user_message)
    elif user_message == 'max':
        user_number = 'max'
    else:
         update.message.reply_text('Please send number')

    days = user_number
    path = config.databases['market_history_chart_days_max']['file']['path']
    plot = path + f'history_plot_days_{days}.png'
    values = path + f'history_values_days_{days}.md'
    if not os.path.exists(plot):
        make_plot(days)
    if not os.path.exists(values):
        write_history_values(days)

    with open(plot, 'rb') as img_file:
        with open(values, 'r') as text_file:
            img_data = img_file.read()
            text_caption = text_file.read()
            context.bot.send_photo(chat_id=update.effective_chat.id,
                                   photo=img_data,
                                   caption=text_caption,
                                   parse_mode=ParseMode.MARKDOWN)
    logger.info("Handle Days command processed")
    return ConversationHandler.END

def go_back(update, context):

    go_back_message = "go_back state"
    update.message.reply_text(go_back_message)
    logger.info("Go Back command processed")
    return ConversationHandler.END

def start_bot():

    # Bot and dispatcher initialization
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher
    handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CommandHandler("market", market),
            CommandHandler("history", history),
            CommandHandler("network", network),
            CommandHandler("lightning", lightning),
            CommandHandler("settings", settings),
            CommandHandler("about", about)
            ],
        states={
            CHOOSE_DAYS: [MessageHandler(Filters.text & ~Filters.command, handle_days)]
        },
        fallbacks=[CommandHandler('go_back', go_back)]
    )
    dispatcher.add_handler(handler)


    # Bot start
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    start_bot()
