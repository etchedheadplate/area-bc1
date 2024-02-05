import concurrent.futures
from memory_profiler import profile
from telegram import ParseMode
from telegram.ext import Updater, ConversationHandler, CommandHandler, MessageHandler, Filters

import config
from news import write_news
from market import draw_market, write_market
from tools import update_databases, convert_date_to_days
from logger import main_logger
from api.telegram import TOKEN


# States:
CHOOSE_DAYS = range(1)


def start(update, context):
    welcome_message = "Use menu button"
    update.message.reply_text(welcome_message)
    main_logger.info('[bot] /start command processed')
    return ConversationHandler.END

def fees(update, context):
    info = 'db/fees/fees.jpg'
    with open(info, 'rb') as img_file:
        img_data = img_file.read()
        context.bot.send_photo(chat_id=update.effective_chat.id,
                                photo=img_data,
                                parse_mode=ParseMode.MARKDOWN)
    main_logger.info('[bot] /fees command processed')
    return ConversationHandler.END

def lightning(update, context):
    plot = 'db/lightning/lightning.jpg'
    markdown = 'db/lightning/lightning.md'
    with open(plot, 'rb') as img_file:
        with open(markdown, 'r') as text_file:
            img_data = img_file.read()
            text_caption = text_file.read()
            context.bot.send_photo(chat_id=update.effective_chat.id,
                                   photo=img_data,
                                   caption=text_caption,
                                   parse_mode=ParseMode.MARKDOWN)
    main_logger.info('[bot] /lightning command processed')
    return ConversationHandler.END

def market(update, context):
    plot = f'db/market/{config.currency_pair}/market.jpg'
    markdown = f'db/market/{config.currency_pair}/market.md'
    if context.args:
        days = convert_date_to_days(context.args[0])
        if type(days) == int:
            if days < 0:
                error_message = 'Future is unknown'
                update.message.reply_text(error_message, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
                return ConversationHandler.END
            elif days == 0:
                plot = f'db/market/{config.currency_pair}/market.jpg'
                markdown = f'db/market/{config.currency_pair}/market.md'
            elif days >= 1:
                draw_market(days)
                write_market(days)
                plot =  f'db/market/{config.currency_pair}/market_days_{days}.jpg'
                markdown = f'db/market/{config.currency_pair}/market_days_{days}.md'
        else:
            if days == 'max':
                draw_market(days)
                write_market(days)
                plot =  f'db/market/{config.currency_pair}/market_days_max.jpg'
                markdown =  f'db/market/{config.currency_pair}/market_days_max.md'
            else:
                hint = 'src/text/hint_dates.md'
                with open(hint, 'r') as hint_text:
                    hint_text = hint_text.read()          
                    update.message.reply_text(hint_text, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
                return ConversationHandler.END
    with open(plot, 'rb') as img_file:
        with open(markdown, 'r') as text_file:
            img_data = img_file.read()
            text_caption = text_file.read()
            context.bot.send_photo(chat_id=update.effective_chat.id,
                                   photo=img_data,
                                   caption=text_caption,
                                   parse_mode=ParseMode.MARKDOWN)
    main_logger.info('[bot] /market command processed')
    return ConversationHandler.END

def network(update, context):
    plot = 'db/network/network.jpg'
    markdown = 'db/network/network.md'
    with open(plot, 'rb') as img_file:
        with open(markdown, 'r') as text_file:
            img_data = img_file.read()
            text_caption = text_file.read()
            context.bot.send_photo(chat_id=update.effective_chat.id,
                                   photo=img_data,
                                   caption=text_caption,
                                   parse_mode=ParseMode.MARKDOWN)
    main_logger.info('[bot] network command processed')
    return ConversationHandler.END

def news(update, context):
    write_news()
    news = 'db/news/news.md'
    with open(news, 'r') as news_text:
        news_message = news_text.read()
        update.message.reply_text(news_message, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
    main_logger.info('[bot] /news command processed')
    return ConversationHandler.END

def pools(update, context):
    diagram = 'db/pools/pools.jpg'
    with open(diagram, 'rb') as img_file:
        img_data = img_file.read()
        context.bot.send_photo(chat_id=update.effective_chat.id,
                                photo=img_data,
                                parse_mode=ParseMode.MARKDOWN)
    main_logger.info('[bot] /pools command processed')
    return ConversationHandler.END

def settings(update, context):
    settings_message = "settings state"
    update.message.reply_text(settings_message)
    main_logger.info('[bot] /settings command processed')
    return ConversationHandler.END

def about(update, context):
    markdown = 'src/text/about.md'
    with open(markdown, 'r') as about_text:
        about_message = about_text.read()
        update.message.reply_text(about_message, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
    main_logger.info('[bot] /about command processed')
    return ConversationHandler.END

def cancel(update, context):
    go_back_message = "returned to /start state"
    update.message.reply_text(go_back_message)
    main_logger.info('[bot] /cancel command processed')
    return ConversationHandler.END

def start_bot():
    # Bot and dispatcher initialization
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher
    handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CommandHandler("fees", fees),
            CommandHandler("lightning", lightning),
            CommandHandler("market", market),
            CommandHandler("network", network),
            CommandHandler("news", news),
            CommandHandler("pools", pools),
            CommandHandler("settings", settings),
            CommandHandler("about", about)
            ],
        states={
#            CHOOSE_DAYS: [MessageHandler(Filters.text & ~Filters.command, handle_days)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    dispatcher.add_handler(handler)
    main_logger.info('[bot] area bc1 started')
    updater.start_polling()
    updater.idle()

@profile
def run_bot():
    with concurrent.futures.ThreadPoolExecutor() as executor:
        run_bot = executor.submit(start_bot)
        run_database_update = executor.submit(update_databases)
        concurrent.futures.wait([run_bot] + [run_database_update])

if __name__ == '__main__':
    run_bot()