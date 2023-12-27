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
from telegram.ext import Updater, CommandHandler

from market_values import latest_values, update_latest_values
# from market_plot import make_market_plot
from config import plot_output_image
import time


def start(update, context):
    welcome_message = "This bot can show you Bitcoin market data. Hit Menu button to see latest Bitcoin stats or history graph."
    update.message.reply_text(welcome_message)

def stats(update, context):
    update_latest_values(latest_values)
#    make_market_plot()
    stats_message = "\n".join([f"{key}: {value}" for key, value in latest_values.items()])
    with open(plot_output_image, 'rb') as img:
        context.bot.send_photo(chat_id=update.effective_chat.id,
                               photo=img,
                               caption=f'```\n{stats_message}```',
                               parse_mode=ParseMode.MARKDOWN)

def graph(update, context):
    graph_message = "this is graph state"
    update.message.reply_text(graph_message)

def settings(update, context):
    settings_message = "this is settings state"
    update.message.reply_text(settings_message)

def about(update, context):
    about_message = "This bot uses [Coingecko API](https://www.coingecko.com/) for market data. " \
                    "You can visit bot's [GitHub page](https://github.com/etchedheadplate/area-bc1)."
    update.message.reply_text(about_message, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)


def main():
    # Bot and dispatcher initialization
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    # Bot handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("stats", stats))
    dispatcher.add_handler(CommandHandler("graph", graph))
    dispatcher.add_handler(CommandHandler("settings", settings))
    dispatcher.add_handler(CommandHandler("about", about))

    # Bot start
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
