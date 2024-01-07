from api.telegram import TOKEN
import logging

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

from telegram import ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

import os

import config
from updates import run_parallel_database_update
from plot import make_history_plot
from values import write_history_values


# States:
START, HISTORY, SETTINGS, ABOUT = range(4)


def start(update, context):

    path = config.databases['latest_api_data']['path']
    plot = path + 'latest_plot.png'
    values = path + 'latest_values.txt'
    with open(plot, 'rb') as img_file:
        with open(values, 'r') as text_file:
            img_data = img_file.read()
            text_caption = text_file.read()
            context.bot.send_photo(chat_id=update.effective_chat.id,
                                   photo=img_data,
                                   caption=text_caption,
                                   parse_mode=ParseMode.MARKDOWN)
    
    return START

def history(update, context):
       
    days = handle_days(update.message.text)
    path = config.databases['history_chart_days_max']['path']
    plot = path + f'history_plot_days_{days}.png'
    values = path + f'history_values_days_{days}.txt'

    if not os.path.exists(plot):
        make_history_plot(days)
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
    
    return HISTORY

def settings(update, context):

    settings_message = "settings state"
    update.message.reply_text(settings_message)
    
    return SETTINGS

def about(update, context):

    settings_message = "This bot uses [CoinGecko API](https://www.coingecko.com/) for market data. " \
                    "You can visit bot's [GitHub page](https://github.com/etchedheadplate/area-bc1)."
    update.message.reply_text(settings_message, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
    
    return ABOUT

def handle_days(update):

    user_message = update.message.text
    if user_message.isdigit():
        user_number = int(user_message)
    else:
        user_number = 'max'
    
    return user_number

def main():

    # Bot and dispatcher initialization
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_days))
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("history", history))
    dispatcher.add_handler(CommandHandler("settings", settings))
    dispatcher.add_handler(CommandHandler("about", about))

    # Bot start
    updater.start_polling()
    updater.idle()




if __name__ == '__main__':
    
    main()
