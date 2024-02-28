import re
import asyncio
import schedule
import functools
import concurrent.futures
from telegram import ParseMode, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, PicklePersistence, ConversationHandler, CommandHandler, MessageHandler, Filters

import config
from cmds.blockchain import explore_address, explore_block, explore_transaction
from cmds.etfs import draw_etfs, write_etfs
from cmds.market import draw_market, write_market
from cmds.network import draw_network, write_network
from cmds.lightning import draw_lightning, write_lightning
from cmds.seized import draw_seized, write_seized
from cmds.news import write_news
from tools import update_databases, convert_date_to_days
from logger import main_logger
from api.telegram import TOKEN


# States:
(SELECTING_PLOT_CHART,
 SELECTING_PLOT_PERIOD,
 SELECTING_NOTIFICATION_COMMAND,
 SELECTING_NOTIFICATION_PERIOD,
 REMOVING_NOTIFICATION) = range(5)


'''
Functions for user commands. Accessible to user within bot interface.
'''

def start(update, context):
    welcome_message = 'Please use menu button at lower left'
    update.message.reply_text(welcome_message, reply_markup=ReplyKeyboardRemove())
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


def notifications(update, context):
    select_notification_reply_keyboard = [['Market', 'Network', 'Lightning'], ['ETFs', 'Seized', 'CEX'], ['Pools', 'Fees', 'News'], ['⚙️ Manage', '🗿 Exit']]
    chat_type = update.effective_chat.type
    if chat_type == 'private':
        notifications_command_message = 'You can setup bot to send you regular notifications. Please choose data to be sent:'
        update.message.reply_text(notifications_command_message, reply_markup=ReplyKeyboardMarkup(select_notification_reply_keyboard, one_time_keyboard=False))
        main_logger.info('[bot] /notification command processed')
        return SELECTING_NOTIFICATION_COMMAND
    elif chat_type == 'group' or chat_type == 'supergroup':
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        chat_member = context.bot.get_chat_member(chat_id, user_id)
        if chat_member.status == 'creator':
            notifications_command_message = 'You can setup bot to send you regular notifications. Please choose data to be sent:'
            update.message.reply_text(notifications_command_message, reply_markup=ReplyKeyboardMarkup(select_notification_reply_keyboard, one_time_keyboard=False))
            main_logger.info('[bot] /notification command processed')
            return SELECTING_NOTIFICATION_COMMAND
        else:
            notifications_error_message = f'This command can only be used by Chat Owner'
            update.message.reply_text(notifications_error_message, reply_markup=ReplyKeyboardRemove())
            return ConversationHandler.END
    else:
        notifications_error_message = f'This command can only be used directly in {config.bot_name}'
        update.message.reply_text(notifications_error_message, reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END


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
Service functions for user commands. Not accessible within bot interface.
'''
def select_notification_command(update, context):
    selected_command = update.message.text
    select_notification_reply_keyboard = [['1 hour', '3 hours', '6 hours'], ['1 day', '7 days', '↩️ Go Back']]
    manage_reply_keyboard = [['🗑 Remove All', '↩️ Go Back']]
    
    if selected_command in set(config.notifications):
        context.chat_data['selected_command'] = selected_command
        if 'scheduled_notifications' in context.chat_data.keys():
            scheduled_commands = set()
            for notification_params in context.chat_data['scheduled_notifications']:
                scheduled_commands.add(notification_params[0])
            if context.chat_data['selected_command'] in scheduled_commands:
                error_notification_exists = f'Notification for {context.chat_data["selected_command"]} already exists. Remove it first by ⚙️ Manage in /notifications'
                update.message.reply_text(error_notification_exists)
                return notifications(update, context)
            else:
                select_notification_message = 'Use buttons below or type in period manually: \
                                            ```Periods\n1 hour 04:20\n9 h\n5 days\n2 d 13:12```'
                update.message.reply_text(select_notification_message, parse_mode=ParseMode.MARKDOWN, reply_markup=ReplyKeyboardMarkup(select_notification_reply_keyboard, one_time_keyboard=False))
                main_logger.info('[bot] entering SELECTING_NOTIFICATION_PERIOD state')
                return SELECTING_NOTIFICATION_PERIOD
        else:
            select_notification_message = 'Use buttons below or type in period manually. Syntaxis examples: \
                                        ```Periods\n1 hour 04:20\n9 h\n5 days\n2 d 13:12```'
            update.message.reply_text(select_notification_message, parse_mode=ParseMode.MARKDOWN, reply_markup=ReplyKeyboardMarkup(select_notification_reply_keyboard, one_time_keyboard=False))
            main_logger.info('[bot] entering SELECTING_NOTIFICATION_PERIOD state')
            return SELECTING_NOTIFICATION_PERIOD

    elif selected_command == '⚙️ Manage':
        if 'scheduled_notifications' in context.chat_data.keys():
            manage_remove_message = 'Please send number of notification to remove:\n\n'
            for scheduled_notification in context.chat_data['scheduled_notifications']:
                scheduled_index = context.chat_data['scheduled_notifications'].index(scheduled_notification)
                manage_index = scheduled_index + 1
                manage_view = context.chat_data['scheduled_notifications'][scheduled_index][2]
                manage_remove_message += f'{manage_index}. {manage_view}\n'
            update.message.reply_text(manage_remove_message, reply_markup=ReplyKeyboardMarkup(manage_reply_keyboard, one_time_keyboard=False))
            main_logger.info('[bot] entering REMOVING_NOTIFICATION state')
            return REMOVING_NOTIFICATION
        else:
            error_no_notifications_message = 'You have no notifications'
            update.message.reply_text(error_no_notifications_message)
            main_logger.info('[bot] notifications schedule cleared')
            return notifications(update, context)
    
    elif selected_command == '🗿 Exit':
        return cancel(update, context)
   
    else:
        error_wrong_command_message = 'Wrong input, please follow example:'
        update.message.reply_text(error_wrong_command_message, reply_markup=ReplyKeyboardMarkup(select_notification_reply_keyboard, one_time_keyboard=False))
        return SELECTING_NOTIFICATION_COMMAND


def select_notification_period(update, context):
    selected_period = update.message.text
    selected_command = context.chat_data['selected_command']
    select_notification_reply_keyboard = [['1 hour', '3 hours', '6 hours'], ['1 day', '7 days', '↩️ Go Back']]
    parsed_period = selected_period.split(' ')
    time_pattern = r'^\d{2}:\d{2}$'

    if len(parsed_period) > 1 and selected_period[0].isdigit():
        parsed_number = parsed_period[0]
        if parsed_number.isdigit() and int(parsed_number) > 0:
            available_units = ['H', 'HOUR', 'HOURS', 'D', 'DAY', 'DAYS']
            parsed_unit  = parsed_period[1]
            user_number = int(parsed_number)
            user_unit = parsed_unit.upper()[0]
            user_command = globals().get(config.notifications[f'{selected_command}'])
            parsed_time = parsed_period[2] if len(parsed_period) > 2 else '19:52'
            if re.match(time_pattern, parsed_time):
                if parsed_unit.upper() in available_units and user_unit == 'H':
                    user_unit = 'hours' if user_number > 1 else 'hour'
                    notification_job = schedule.every(user_number).hours.at(parsed_time).do(functools.partial(user_command, update=update, context=context))
                    notification_next_run = notification_job.next_run
                    notification_view = f'{selected_command} every {user_number} {user_unit}, next run {notification_next_run}'
                    if 'scheduled_notifications' in context.chat_data.keys():
                        context.chat_data['scheduled_notifications'].append([selected_command, selected_period, notification_view])
                        context.chat_data['notification_jobs'].append(notification_job)
                    else:
                        context.chat_data['scheduled_notifications'] = [[selected_command, selected_period, notification_view]]
                        context.chat_data['notification_jobs'] = [notification_job]
                    notification_set_message = f'Excellent. You will recieve {selected_command} data every {user_number} {user_unit} \n' \
                                                f'at {parsed_time}. You can ⚙️ Manage it by running /notifications again.'
                    update.message.reply_text(notification_set_message)
                    user_id = update.effective_user.id
                    chat_id = update.effective_chat.id
                    main_logger.info(f'[bot] notification for {selected_command} set by user {user_id} in chat {chat_id}')
                    return notifications(update, context)
                elif parsed_unit.upper() in available_units and user_unit == 'D':
                    user_unit = 'days' if user_number > 1 else 'day'
                    notification_job = schedule.every(user_number).days.at(parsed_time).do(functools.partial(user_command, update=update, context=context))
                    notification_next_run = notification_job.next_run
                    notification_view = f'{selected_command}: every {user_number} {user_unit} at {parsed_time}, next run {notification_next_run}'
                    if 'scheduled_notifications' in context.chat_data.keys():
                        context.chat_data['scheduled_notifications'].append([selected_command, selected_period, notification_view])
                        context.chat_data['notification_jobs'].append(notification_job)
                    else:
                        context.chat_data['scheduled_notifications'] = [[selected_command, selected_period, notification_view]]
                        context.chat_data['notification_jobs'] = [notification_job]
                    notification_set_message = f'Excellent. You will recieve {selected_command} data every {user_number} {user_unit} \n' \
                                            f'at {parsed_time}. You can ⚙️ Manage it by running /notifications again.'
                    update.message.reply_text(notification_set_message)
                    user_id = update.effective_user.id
                    chat_id = update.effective_chat.id
                    main_logger.info(f'[bot] notification for {selected_command} set by user {user_id} in chat {chat_id}')
                    return notifications(update, context)
                else:
                    notification_wrong_unit = f'Period must be in days or hours'
                    update.message.reply_text(notification_wrong_unit, reply_markup=ReplyKeyboardMarkup(select_notification_reply_keyboard, one_time_keyboard=False))
                    return SELECTING_NOTIFICATION_PERIOD
            else:
                notification_wrong_time = f'Time must be in hh:mm format'
                update.message.reply_text(notification_wrong_time, reply_markup=ReplyKeyboardMarkup(select_notification_reply_keyboard, one_time_keyboard=False))
                return SELECTING_NOTIFICATION_PERIOD
        else:
            notification_wrong_number = f'Days or hours must be whole positive number'
            update.message.reply_text(notification_wrong_number, reply_markup=ReplyKeyboardMarkup(select_notification_reply_keyboard, one_time_keyboard=False))
            return SELECTING_NOTIFICATION_PERIOD
    elif selected_period == '↩️ Go Back':
        return notifications(update, context)
    else:
        error_wrong_period = 'Could not parse input syntaxis'
        update.message.reply_text(error_wrong_period)
        return notifications(update, context)


def remove_notification(update, context):
    remove_notification_number = update.message.text
    manage_reply_keyboard = [['🗑 Remove All', '↩️ Go Back']]

    if remove_notification_number.isdigit() and int(remove_notification_number) - 1 in range(len(context.chat_data['notification_jobs'])):
        remove_notification_index = int(remove_notification_number) - 1
        remove_notification_job = context.chat_data['notification_jobs'][remove_notification_index]
        schedule.cancel_job(remove_notification_job)
        context.chat_data['notification_jobs'].pop(remove_notification_index)
        context.chat_data['scheduled_notifications'].pop(remove_notification_index)
        remove_notification_message = f'Notification removed'
        update.message.reply_text(remove_notification_message)
        if len(context.chat_data['notification_jobs']) == 0:
            context.chat_data.pop('notification_jobs')
            return notifications(update, context)
        else:
            return notifications(update, context)
    elif remove_notification_number == '🗑 Remove All':
        remove_notification_message = 'You will no longer recieve any notifications.'
        for notification_job in context.chat_data['notification_jobs']:
            schedule.cancel_job(notification_job)
        context.chat_data.pop('notification_jobs')
        context.chat_data.pop('scheduled_notifications')
        update.message.reply_text(remove_notification_message)
        return notifications(update, context)
    elif remove_notification_number == '↩️ Go Back':
        return notifications(update, context)
    else:
        error_wrong_notification_number = f'Please send number from 1 to {len(context.chat_data["scheduled_notifications"])}:'
        update.message.reply_text(error_wrong_notification_number, reply_markup=ReplyKeyboardMarkup(manage_reply_keyboard, one_time_keyboard=False))
        return REMOVING_NOTIFICATION
    

async def run_schedule():
    while True:
        schedule.run_pending()
        await asyncio.sleep(60)


'''
Functions for bot backend
'''

def start_bot():
    # Bot and dispatcher initialization
#    my_persistence = PicklePersistence(filename=config.bot_settings)
#    updater = Updater(TOKEN, persistence=my_persistence, use_context=True)
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
            CommandHandler('notifications', notifications),
            CommandHandler('about', about)
            ],
        states={
            SELECTING_NOTIFICATION_COMMAND: [MessageHandler(Filters.text & ~Filters.command, select_notification_command)],
            SELECTING_NOTIFICATION_PERIOD: [MessageHandler(Filters.text & ~Filters.command, select_notification_period)],
            REMOVING_NOTIFICATION: [MessageHandler(Filters.text & ~Filters.command, remove_notification)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    dispatcher.add_handler(handler)
    main_logger.info('[bot] area bc1 started')
    updater.start_polling()
    updater.idle()


async def run_bot():
    with concurrent.futures.ThreadPoolExecutor() as executor:
        run_bot = executor.submit(start_bot)
        run_database_update = executor.submit(update_databases)
        concurrent.futures.wait([run_bot] + [run_database_update])

    asyncio.create_task(run_schedule())




if __name__ == '__main__':
    asyncio.run(run_bot())