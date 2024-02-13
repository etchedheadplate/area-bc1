import concurrent.futures
from memory_profiler import profile
from telegram import ParseMode
from telegram.ext import Updater, ConversationHandler, CommandHandler, MessageHandler, Filters

import config
from blockchain import explore_address, explore_block, explore_transaction
from market import draw_market, write_market
from network import draw_network, write_network
from lightning import draw_lightning, write_lightning
from news import write_news
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

def address(update, context):
    if context.args:
        address_data = explore_address(context.args[0])
        if address_data:
            address_image = address_data[0]
            address_text = address_data[1]
        else:
            error_message = f'Address {context.args[0]} does not exists'
            update.message.reply_text(error_message, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
            return ConversationHandler.END
    else:
        hint = 'src/text/hint_address.md'
        with open(hint, 'r') as hint_text:
            hint_text = hint_text.read()          
            update.message.reply_text(hint_text, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
        return ConversationHandler.END
    with open(address_image, 'rb') as img_file:
        with open(address_text, 'r') as text_file:
            img_data = img_file.read()
            text_caption = text_file.read()
            context.bot.send_photo(chat_id=update.effective_chat.id,
                                   photo=img_data,
                                   caption=text_caption,
                                   parse_mode=ParseMode.MARKDOWN)
    main_logger.info('[bot] /address command processed')
    return ConversationHandler.END

def block(update, context):
    if context.args:
        block_data = explore_block(context.args[0])
        if block_data:
            block_image = block_data[0]
            block_text = block_data[1]
        else:
            error_message = f'Block {context.args[0]} does not exists'
            update.message.reply_text(error_message, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
            return ConversationHandler.END    
    else:
        hint = 'src/text/hint_block.md'
        with open(hint, 'r') as hint_text:
            hint_text = hint_text.read()          
            update.message.reply_text(hint_text, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
        return ConversationHandler.END
    with open(block_image, 'rb') as img_file:
        with open(block_text, 'r') as text_file:
            img_data = img_file.read()
            text_caption = text_file.read()
            context.bot.send_photo(chat_id=update.effective_chat.id,
                                   photo=img_data,
                                   caption=text_caption,
                                   parse_mode=ParseMode.MARKDOWN)
    main_logger.info('[bot] /block command processed')
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

def market(update, context):
    plot = f'db/market/{config.currency_pair}/market_days_1.jpg'
    markdown = f'db/market/{config.currency_pair}/market_days_1.md'
    if context.args:
        days = convert_date_to_days(context.args[0])
        if type(days) == int:
            if days < 1:
                error_message = 'Future is unknown'
                update.message.reply_text(error_message, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
                return ConversationHandler.END
            elif days == 1:
                plot = plot
                markdown = markdown
            elif days >= 1:
                plot =  draw_market(days)
                markdown = write_market(days)
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
    plot = 'db/network/network_days_30.jpg'
    markdown = 'db/network/network.md'
    if context.args:
        days = convert_date_to_days(context.args[0])
        if type(days) == int:
            if days < 1:
                error_message = 'Future is unknown'
                update.message.reply_text(error_message, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
                return ConversationHandler.END
            elif days == 1:
                plot = plot
                markdown = markdown
            elif days >= 1:
                plot =  draw_network(days)
                markdown = markdown
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
    main_logger.info('[bot] network command processed')
    return ConversationHandler.END

def lightning(update, context):
    plot = 'db/lightning/lightning_days_30.jpg'
    markdown = 'db/lightning/lightning.md'
    if context.args:
        days = convert_date_to_days(context.args[0])
        if type(days) == int:
            if days < 1:
                error_message = 'Future is unknown'
                update.message.reply_text(error_message, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
                return ConversationHandler.END
            elif days == 1:
                plot = plot
                markdown = markdown
            elif days >= 1:
                plot =  draw_lightning(days)
                markdown = markdown
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
    main_logger.info('[bot] /lightning command processed')
    return ConversationHandler.END

def news(update, context):
    news = write_news()
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

def transaction(update, context):
    if context.args:
        transaction_data = explore_transaction(context.args[0])
        if transaction_data:
            transaction_image = transaction_data[0]
            transaction_text = transaction_data[1]
        else:
            error_message = f'Transaction {context.args[0]} does not exists'
            update.message.reply_text(error_message, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
            return ConversationHandler.END     
    else:
        hint = 'src/text/hint_transaction.md'
        with open(hint, 'r') as hint_text:
            hint_text = hint_text.read()          
            update.message.reply_text(hint_text, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
        return ConversationHandler.END
    with open(transaction_image, 'rb') as img_file:
        with open(transaction_text, 'r') as text_file:
            img_data = img_file.read()
            text_caption = text_file.read()
            context.bot.send_photo(chat_id=update.effective_chat.id,
                                   photo=img_data,
                                   caption=text_caption,
                                   parse_mode=ParseMode.MARKDOWN)
    main_logger.info('[bot] /transaction command processed')
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
            CommandHandler("address", address),
            CommandHandler("block", block),
            CommandHandler("fees", fees),
            CommandHandler("lightning", lightning),
            CommandHandler("market", market),
            CommandHandler("network", network),
            CommandHandler("news", news),
            CommandHandler("pools", pools),
            CommandHandler("transaction", transaction),
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