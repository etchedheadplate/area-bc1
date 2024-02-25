import asyncio
import schedule
import functools
import concurrent.futures
from telegram import ParseMode, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, ConversationHandler, CommandHandler, MessageHandler, Filters

import config
from commands.blockchain import explore_address, explore_block, explore_transaction
from commands.etfs import draw_etfs, write_etfs
from commands.market import draw_market, write_market
from commands.network import draw_network, write_network
from commands.lightning import draw_lightning, write_lightning
from commands.seized import draw_seized, write_seized
from commands.news import write_news
from tools import update_databases, convert_date_to_days
from logger import main_logger
from api.telegram import TOKEN


# States:
SELECTING_NOTIFICATION_COMMAND, SELECTING_NOTIFICATION_PERIOD = range(2)


'''
Functions for commands accessible to user within bot interface
'''

def start(update, context):
    welcome_message = 'Please use menu button at lower left'
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


def etfs(update, context):
    etfs_image = 'db/etfs/etfs_days_30.jpg'
    etfs_text = 'db/etfs/etfs_days_1.md'
    if context.args:
        days = convert_date_to_days(context.args[0])
        if type(days) == int:
            if days < 1:
                error_message = 'Future is unknown'
                update.message.reply_text(error_message, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
                return ConversationHandler.END
            elif days < 2:
                error_message = 'Available data starts from 2 days to the past:'
                update.message.reply_text(error_message, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
                days = 2
                etfs_image =  draw_etfs(days)
                etfs_text = write_etfs(days)
            else:
                etfs_image =  draw_etfs(days)
                etfs_text = write_etfs(days)
        else:
            hint = 'src/text/hint_dates.md'
            with open(hint, 'r') as hint_text:
                hint_text = hint_text.read()          
                update.message.reply_text(hint_text, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
            return ConversationHandler.END
    with open(etfs_image, 'rb') as img_file:
        with open(etfs_text, 'r') as text_file:
            img_data = img_file.read()
            text_caption = text_file.read()
            context.bot.send_photo(chat_id=update.effective_chat.id,
                                   photo=img_data,
                                   caption=text_caption,
                                   parse_mode=ParseMode.MARKDOWN)
    main_logger.info('[bot] /etfs command processed')


def exchanges(update, context):
    exchanges_image = 'db/exchanges/exchanges.jpg'
    with open(exchanges_image, 'rb') as img_file:
        img_data = img_file.read()
        context.bot.send_photo(chat_id=update.effective_chat.id,
                                photo=img_data,
                                parse_mode=ParseMode.MARKDOWN)
    main_logger.info('[bot] /exchanges command processed')
    return ConversationHandler.END


def fees(update, context):
    fees_image = 'db/fees/fees.jpg'
    with open(fees_image, 'rb') as img_file:
        img_data = img_file.read()
        context.bot.send_photo(chat_id=update.effective_chat.id,
                                photo=img_data,
                                parse_mode=ParseMode.MARKDOWN)
    main_logger.info('[bot] /fees command processed')
    return ConversationHandler.END


def market(update, context):
    market_image = f'db/market/{config.currency_pair}/market_days_1.jpg'
    market_text = f'db/market/{config.currency_pair}/market_days_1.md'
    if context.args:
        days = convert_date_to_days(context.args[0])
        if type(days) == int:
            if days < 1:
                error_message = 'Future is unknown'
                update.message.reply_text(error_message, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
                return ConversationHandler.END
            else:
                market_image =  draw_market(days)
                market_text = write_market(days)
        else:
            hint = 'src/text/hint_dates.md'
            with open(hint, 'r') as hint_text:
                hint_text = hint_text.read()          
                update.message.reply_text(hint_text, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
            return ConversationHandler.END
    with open(market_image, 'rb') as img_file:
        with open(market_text, 'r') as text_file:
            img_data = img_file.read()
            text_caption = text_file.read()
            context.bot.send_photo(chat_id=update.effective_chat.id,
                                   photo=img_data,
                                   caption=text_caption,
                                   parse_mode=ParseMode.MARKDOWN)
    main_logger.info('[bot] /market command processed')
    return ConversationHandler.END


def network(update, context):
    network_image = 'db/network/network_days_30.jpg'
    network_text = 'db/network/network_days_1.md'
    if context.args:
        days = convert_date_to_days(context.args[0])
        if type(days) == int:
            if days < 1:
                error_message = 'Future is unknown'
                update.message.reply_text(error_message, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
                return ConversationHandler.END
            elif days < 2:
                error_message = 'Available data starts from 2 days to the past:'
                update.message.reply_text(error_message, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
                days = 2
                network_image =  draw_network(days)
                network_text = write_network(days)
            else:
                network_image =  draw_network(days)
                network_text = write_network(days)
        else:
            hint = 'src/text/hint_dates.md'
            with open(hint, 'r') as hint_text:
                hint_text = hint_text.read()          
                update.message.reply_text(hint_text, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
            return ConversationHandler.END
    with open(network_image, 'rb') as img_file:
        with open(network_text, 'r') as text_file:
            img_data = img_file.read()
            text_caption = text_file.read()
            context.bot.send_photo(chat_id=update.effective_chat.id,
                                   photo=img_data,
                                   caption=text_caption,
                                   parse_mode=ParseMode.MARKDOWN)
    main_logger.info('[bot] network command processed')
    return ConversationHandler.END


def lightning(update, context):
    lightning_image = 'db/lightning/lightning_days_30.jpg'
    lightning_text = 'db/lightning/lightning_days_1.md'
    if context.args:
        days = convert_date_to_days(context.args[0])
        if type(days) == int:
            if days < 1:
                error_message = 'Future is unknown'
                update.message.reply_text(error_message, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
                return ConversationHandler.END
            elif days < 2:
                error_message = 'Available data starts from 2 days to the past:'
                update.message.reply_text(error_message, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
                days = 2
                lightning_image =  draw_lightning(days)
                lightning_text = write_lightning(days)
            else:
                lightning_image =  draw_lightning(days)
                lightning_text = write_lightning(days)
        else:
            hint = 'src/text/hint_dates.md'
            with open(hint, 'r') as hint_text:
                hint_text = hint_text.read()          
                update.message.reply_text(hint_text, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
            return ConversationHandler.END
    with open(lightning_image, 'rb') as img_file:
        with open(lightning_text, 'r') as text_file:
            img_data = img_file.read()
            text_caption = text_file.read()
            context.bot.send_photo(chat_id=update.effective_chat.id,
                                   photo=img_data,
                                   caption=text_caption,
                                   parse_mode=ParseMode.MARKDOWN)
    main_logger.info('[bot] /lightning command processed')
    return ConversationHandler.END


def news(update, context):
    news_text = write_news()
    with open(news_text, 'r') as text_file:
        news_message = text_file.read()
        update.message.reply_text(news_message, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
    main_logger.info('[bot] /news command processed')
    return ConversationHandler.END


def pools(update, context):
    pools_image = 'db/pools/pools.jpg'
    with open(pools_image, 'rb') as img_file:
        img_data = img_file.read()
        context.bot.send_photo(chat_id=update.effective_chat.id,
                                photo=img_data,
                                parse_mode=ParseMode.MARKDOWN)
    main_logger.info('[bot] /pools command processed')
    return ConversationHandler.END


def seized(update, context):
    seized_image = 'db/seized/seized_days_1095.jpg'
    seized_text = 'db/seized/seized_days_1.md'
    if context.args:
        days = convert_date_to_days(context.args[0])
        if type(days) == int:
            if days < 1:
                error_message = 'Future is unknown'
                update.message.reply_text(error_message, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
                return ConversationHandler.END
            elif days < 2:
                error_message = 'Available data starts from 2 days to the past:'
                update.message.reply_text(error_message, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
                days = 2
                seized_image =  draw_seized(days)
                seized_text = write_seized(days)
            else:
                seized_image =  draw_seized(days)
                seized_text = write_seized(days)
        else:
            hint = 'src/text/hint_dates.md'
            with open(hint, 'r') as hint_text:
                hint_text = hint_text.read()          
                update.message.reply_text(hint_text, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
            return ConversationHandler.END
    with open(seized_image, 'rb') as img_file:
        with open(seized_text, 'r') as text_file:
            img_data = img_file.read()
            text_caption = text_file.read()
            context.bot.send_photo(chat_id=update.effective_chat.id,
                                   photo=img_data,
                                   caption=text_caption,
                                   parse_mode=ParseMode.MARKDOWN)
    main_logger.info('[bot] /seized command processed')


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


def history(update, context):
    markdown = 'src/text/hint_dates.md'
    with open(markdown, 'r') as history_text:
        history_message = history_text.read()
        update.message.reply_text(history_message, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
    main_logger.info('[bot] /history command processed')
    return ConversationHandler.END


def notification(update, context):
    notification_command_message = 'You can setup bot to send you regular notifications. Please choose data to be sent:'
    reply_keyboard = [['Market', 'Network', 'Lightning'], ['ETFs', 'Seized', 'CEX'], ['Pools', 'Fees', 'News'], ['Stop Notifications', 'Cancel']]
    update.message.reply_text(notification_command_message, reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    main_logger.info('[bot] /notification command processed')
    return SELECTING_NOTIFICATION_COMMAND


def about(update, context):
    about_image = 'src/image/backgrounds/about.png'
    about_text = 'src/text/about.md'
    with open(about_image, 'rb') as img_file:
        with open(about_text, 'r') as text_file:
            img_data = img_file.read()
            text_caption = text_file.read()
            context.bot.send_photo(chat_id=update.effective_chat.id,
                                   photo=img_data,
                                   caption=text_caption,
                                   parse_mode=ParseMode.MARKDOWN)
    main_logger.info('[bot] /about command processed')
    return ConversationHandler.END


def cancel(update, context):
    main_logger.info('[bot] /cancel command processed')
    return start(update, context)


'''
Service functions for user functions, not accessible within bot interface
'''

def select_notification_command(update, context):
    selected_command = update.message.text
    
    if selected_command in set(config.notifications):
        context.user_data['selected_command'] = selected_command
        notification_period_message = 'Nice. Bot will send you notification every __ MINUTES (send number):'
        update.message.reply_text(notification_period_message, reply_markup=ReplyKeyboardRemove())
        main_logger.info('[bot] SELECTING_NOTIFICATION_COMMAND state processed')
        return SELECTING_NOTIFICATION_PERIOD
    
    elif selected_command == 'Stop Notifications':
        for notification_params in context.user_data['notifications']:
            notification_job = notification_params.pop()
            schedule.cancel_job(notification_job)
        context.user_data['notifications'] = ''
        notification_stop_message = 'You will no longer recieve any notifications.'
        update.message.reply_text(notification_stop_message)
        main_logger.info('[bot] notification schedule cleared')
        return ConversationHandler.END
    
    elif selected_command == 'Cancel':
        cancel(update, context)
   
    else:
        notification_wrong_command = 'Wrong input, please select one from list below:'
        update.message.reply_text(notification_wrong_command)
        main_logger.info('[bot] notification schedule cleared')
        return SELECTING_NOTIFICATION_COMMAND


def select_notification_period(update, context):
    selected_period = update.message.text
    
    if selected_period.isdigit() and int(selected_period) > 0:
        context.user_data['selected_period'] = selected_period
        user_command = context.user_data['selected_command']
        user_period = int(context.user_data['selected_period'])
        command_name = config.notifications[f'{user_command}']
        command = globals().get(command_name)
        user_notification = schedule.every(user_period).minutes.at(':00').do(functools.partial(command, update=update, context=context))
        
        if not 'notifications' in context.user_data.keys():
            context.user_data['notifications'] = [[user_command, user_period, user_notification]]
        else:
            context.user_data['notifications'].append([user_command, user_period, user_notification])

        notification_set_message = f'Excellent. You will recieve {user_command} data every {user_period} MINUTES. You can stop notifications by running /notification command again.'
        update.message.reply_text(notification_set_message)
        main_logger.info('[bot] SELECTING_NOTIFICATION_PERIOD state processed')
        return ConversationHandler.END
    
    else:
        notification_wrong_period = 'Wrong input, please send whole postive number:'
        update.message.reply_text(notification_wrong_period)
        return SELECTING_NOTIFICATION_PERIOD
    

async def run_schedule():
    while True:
        schedule.run_pending()
        await asyncio.sleep(60)


'''
Functions for bot backend
'''

def start_bot():
    # Bot and dispatcher initialization
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher
    handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start),
            CommandHandler('address', address),
            CommandHandler('block', block),
            CommandHandler('etfs', etfs),
            CommandHandler('exchanges', exchanges),
            CommandHandler('fees', fees),
            CommandHandler('lightning', lightning),
            CommandHandler('market', market),
            CommandHandler('network', network),
            CommandHandler('news', news),
            CommandHandler('pools', pools),
            CommandHandler('seized', seized),
            CommandHandler('transaction', transaction),
            CommandHandler('history', history),
            CommandHandler('notification', notification),
            CommandHandler('about', about)
            ],
        states={
            SELECTING_NOTIFICATION_COMMAND: [MessageHandler(Filters.text & ~Filters.command, select_notification_command)],
            SELECTING_NOTIFICATION_PERIOD: [MessageHandler(Filters.text & ~Filters.command, select_notification_period)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    dispatcher.add_handler(handler)
    main_logger.info('[bot] area bc1 started')
    updater.start_polling()
    updater.idle()


def run_bot():
    with concurrent.futures.ThreadPoolExecutor() as executor:
        run_bot = executor.submit(start_bot)
        run_database_update = executor.submit(update_databases)
        concurrent.futures.wait([run_bot] + [run_database_update])

    asyncio.create_task(run_schedule())




if __name__ == '__main__':
    asyncio.run(run_bot())