import os
import json
import time
import asyncio
import traceback
import requests
import schedule
import importlib
import functools
import pandas as pd

from datetime import datetime, timedelta
from currency_symbols import CurrencySymbols
from memory_profiler import profile

import config
from logger import main_logger


# Error handlers for all functions to ensure uninterrupted bot operation 
def error_handler_common(common_function):
    def wrapper(*args, **kwargs):
        try:
            return common_function(*args, **kwargs)
        except Exception as e:
            error_trace = traceback.format_exc()
            main_logger.error(f'Error in {common_function.__name__}: {e}, args: {args}, kwargs: {kwargs}\n{error_trace}')
    return wrapper

def error_handler_async(async_function):
    async def wrapper(*args, **kwargs):
        try:
            if asyncio.iscoroutinefunction(async_function):
                return await async_function(*args, **kwargs)
            else:
                return async_function(*args, **kwargs)
        except Exception as e:
            main_logger.error(f'Error in async {async_function.__name__}: {e}, args: {args}, kwargs: {kwargs}')
    return wrapper


'''
Functions for managing database:
- connect to API and get raw data 
- parse raw data by database template
- save parsed data to JSON or CSV file
- schedule continious databases updates
- clean database from user-generated files
'''

@error_handler_common
def get_api_data(base, endpoint, params=False):
# Builds formatted URL to API based on user configuration and retrieves API data.
    query_params = []
    if params: # Build queries list from standart API parameters and custom database parameters
        for query, value in params.items():
            params[f'{query}']=f'{value}'
            query_params.append(f"{query}={value}")
    api_url = f"{base}{endpoint}?{'&'.join(query_params)}"
    api_response = requests.get(api_url)
    return api_response

@error_handler_common
def make_chart_data(database):
    # Creates chart path if it doesn't exists. Distributes API data to columns using
    # 'date' column as common denominator. Saves data to database as CSV file.
    chart = config.charts[f'{database}']

    # User configuration related variables:
    api_base = chart['api']['base']
    api_endpoints = chart['api']['endpoints']
    api_extention = chart['api']['extention']
    api_params = chart['api']['params']
    api_subdict = chart['api']['subdict']
    api_parsed = chart['api']['parsed']

    file_path = chart['file']['path']
    file_name = chart['file']['name']
    file_columns = chart['file']['columns']
    file = file_path + file_name

    # Create chart directory if it doesn' exists:
    if not os.path.isdir(file_path):
        os.makedirs(file_path, exist_ok=True)

    if api_extention == 'json':
        response_columns = pd.DataFrame({'date': []}) # Empty DataFrame for later filling with response DataFrame:
        for api_endpoint in api_endpoints:
            response = get_api_data(api_base, api_endpoint, api_params)
            response = response.json()[api_subdict] if api_subdict else response.json()
            if type(file_columns) is dict: # Response proccesed differently if data returned as list or dict
                if api_parsed == 'list':
                    for row, column in file_columns[api_endpoint].items():
                        response_data = pd.DataFrame(response[row], columns=['date', f'{column}'])
                        response_columns = response_columns.merge(response_data, on='date', how='outer').dropna().sort_values(by='date')
                elif api_parsed == 'dict':
                    response_data = pd.DataFrame(response).rename(columns=file_columns[api_endpoint])
                    response_columns = response_columns.merge(response_data, on='date', how='outer').dropna().sort_values(by='date')
                else:
                    main_logger.warning(f'unknown type of parsed api response for {database}: {type(api_parsed)}')
            elif type(file_columns) is list:
                response_columns = pd.DataFrame(list(response.items()), columns=file_columns)
            else:
                main_logger.warning(f'unknown type of config param file_columns for {database}: {type(file_columns)}')
            time.sleep(5) # 5 seconds between API callsrequests to comply with API limits in case of multiple endpoints
        response_columns.to_csv(file, index=False)
    elif api_extention == 'csv':
        for api_endpoint in api_endpoints:
            response = get_api_data(api_base, api_endpoint, api_params)
            time.sleep(5) # 5 seconds between API callsrequests to comply with API limits in case of multiple endpoints
            with open(file, 'wb') as response_file:
                response_file.write(response.content)
    else:
        main_logger.warning(f'unknown file extention for {database}')

    main_logger.info(f'{database} updated')
    
@error_handler_common
def make_snapshot_data(database):
    # Creates snapshot path if it doesn't exists. Saves data to database as JSON file.
    snapshot = config.snapshots[f'{database}']

    # User configuration related variables:
    api_base = snapshot['api']['base']
    api_endpoint = snapshot['api']['endpoint']
    api_params = snapshot['api']['params']

    file_path = snapshot['file']['path']
    file_name = snapshot['file']['name']
    file = file_path + file_name

    # Create snapshot directory if it doesn' exists:
    if not os.path.isdir(file_path):
        os.makedirs(file_path, exist_ok=True)

    # Call to API and creation JSON file based on response data:
    response = get_api_data(api_base, api_endpoint, api_params)
    response = response.json()
    with open(file, 'w') as json_file:
        json.dump(response, json_file)
    
    main_logger.info(f'{database} updated')

@error_handler_common
def format_update_seconds(seconds):
    # Formats seconds to schedule module format.
    seconds = round(abs(seconds))
    seconds = int(seconds - seconds // 60 * 60) if seconds >= 60 else seconds
    formatted_seconds = f':{seconds}' if seconds >= 10 else f':0{seconds}'
    return formatted_seconds

@error_handler_common
def clean_databases():
    # Removes files generated by user for last 72 hours
    databases_path = 'db/'
    extensions_to_remove = ['.md', '.jpg']
    files_removed = 0
    current_time = datetime.now()

    for root, dirs, files in os.walk(databases_path):
        for file in files:
            file_path = os.path.join(root, file)
            file_extension = os.path.splitext(file)[1].lower()
            if file_extension in extensions_to_remove:
                creation_time = datetime.fromtimestamp(os.path.getctime(file_path))
                time_difference = current_time - creation_time
                if time_difference.total_seconds() >= 72 * 3600:
                    os.remove(file_path)
                    main_logger.info(f'{file_path} removed')
                    files_removed += 1
    main_logger.info(f'removed {files_removed} files')

# @profile
@error_handler_common
def update_databases():
    # Initializes databases. Assigns proper function to handle each database.
    # Schedules regular updates for each database based on user configuration.
    charts = config.charts
    snapshots = config.snapshots
    updates = config.updates
    delay = config.delay

    clean_databases()
    main_logger.info(f'charts updating (~{len(charts) * delay} seconds)')
    for chart_name in charts.keys():
        make_chart_data(chart_name) # Database chart initialized for the first time
        time.sleep(delay) # Delay to not exceed rate limits for charts with same API
    for chart_name in charts.keys():
        chart_update_minutes = updates[f'{chart_name}']['minutes']
        chart_update_seconds = format_update_seconds(updates[f'{chart_name}']['seconds'])
        schedule.every(chart_update_minutes).minutes.at(chart_update_seconds).do(make_chart_data, chart_name)
    main_logger.info('charts updates scheduled')

    main_logger.info(f'snapshots updating (~{len(snapshots) * delay} seconds)')
    for snapshot_name in snapshots.keys():
        make_snapshot_data(snapshot_name) # Database snapshot initialized for the first time
        time.sleep(delay) # Delay to not exceed rate limits for snapshots with same API
    for snapshot_name in snapshots.keys():
        snapshot_update_minutes = updates[f'{snapshot_name}']['minutes']
        snapshot_update_seconds = format_update_seconds(updates[f'{snapshot_name}']['seconds'] + delay)
        schedule.every(snapshot_update_minutes).minutes.at(snapshot_update_seconds).do(make_snapshot_data, snapshot_name)
    main_logger.info('snapshots updates scheduled')

    # List of all databases no matter if chart or snapshot:
    databases = list(charts.keys() | snapshots.keys())
    current_directory = os.path.dirname(os.path.abspath(__file__))
    for database in databases:
        module_file = os.path.join(current_directory, 'cmds', f'{database}.py')
        if os.path.exists(module_file):
            module_name = f'cmds.{database}'
            module = importlib.import_module(module_name)
            module_draw_image = getattr(module, f'draw_{database}', None)
            module_write_markdown = getattr(module, f'write_{database}', None)
            module_update_minutes = updates[f'{database}']['minutes']
            module_update_seconds = format_update_seconds(updates[f'{database}']['seconds'])
            module_functions = [module_draw_image, module_write_markdown]
            for module_function in module_functions:
                if callable(module_function): # Each database module checked if contains image and/or markdown functions
                    module_function()
                    schedule.every(module_update_minutes).minutes.at(module_update_seconds).do(functools.partial(module_function))
    main_logger.info('image updates scheduled')
    main_logger.info('markdown updates scheduled')

    schedule.every(1).days.at('00:00:00').do(functools.partial(clean_databases))
    main_logger.info('database cleaning scheduled')
    while True:
        schedule.run_pending()
        time.sleep(60)


'''
Functions for plot design:
- choose background image and colors
- format time axis to common abbreviation
'''

@error_handler_common
def define_key_metric_movement(plot, key_metric_change_percentage):
    # Defines backround image and colors based on % of key metric movement
    for background in plot['backgrounds']:
        key_metric_movement = plot['backgrounds'][f'{background}']['range']
        if key_metric_movement[0] <= key_metric_change_percentage < key_metric_movement[1]:
            return background
        
@error_handler_common
def format_time_axis(timestamp, days):
    # Converts timestamps from chart's Date columns to UTC and appropriately formats time to plot period.
    
    if len(str(int(timestamp))) > 10:  # Convert milliseconds timestamp to seconds
        timestamp /= 1000
    date_object = datetime.utcfromtimestamp(timestamp) # Convert timestamp to UTC

    # Format time appropriately to plot period:
    if days <= 1:
        formatted_date = date_object.strftime('%H:%M')
    elif days <= 6:
        formatted_date = date_object.strftime('%Y.%m.%d\n%H:%M')
    elif days <= 365:
        formatted_date = date_object.strftime('%Y.%m.%d')
    elif days <= 1825:
        formatted_date = date_object.strftime('%Y.%m')
    else:
        formatted_date = date_object.strftime('%Y')
    return formatted_date


'''
Functions to decorate raw values for user:
- format values to common abbreviation
- convert values to different types
- calculate new values from old
'''

@error_handler_common
def format_amount(amount, ticker=False, decimal=0):
    # Formats amount to common abbreviation.
    string_amount = str(amount) + '.'
    decimal_places = len(string_amount.split('.')[1]) if decimal is False else decimal

    if amount >= 1_000_000_000_000_000:
        formatted_amount = "{:.1f}Qn".format(amount / 1_000_000_000_000_000)
    elif amount >= 1_000_000_000_000:
        formatted_amount = "{:.1f}T".format(amount / 1_000_000_000_000)
    elif amount >= 1_000_000_000:
        formatted_amount = "{:.1f}B".format(amount / 1_000_000_000)
    elif amount >= 1_000_000:
        formatted_amount = "{:.1f}M".format(amount / 1_000_000)
    elif amount >= 1_000:
        formatted_amount = "{:.1f}K".format(amount / 1_000)
    elif amount <= -1_000_000_000_000_000:
        formatted_amount = "{:.1f}Qn".format(amount / 1_000_000_000_000_000)
    elif amount <= -1_000_000_000_000:
        formatted_amount = "{:.1f}T".format(amount / 1_000_000_000_000)
    elif amount <= -1_000_000_000:
        formatted_amount = "{:.1f}B".format(amount / 1_000_000_000)
    elif amount <= -1_000_000:
        formatted_amount = "{:.1f}M".format(amount / 1_000_000)
    elif amount <= -1_000:
        formatted_amount = "{:.1f}K".format(amount / 1_000)
    else:
        formatted_amount = '{:,.{}f}'.format(amount, decimal_places)
    
    if ticker:
        currency_symbol = CurrencySymbols().get_symbol(ticker)
        if currency_symbol:
            return currency_symbol + formatted_amount
        else:
            return ticker + formatted_amount
    else:
        return formatted_amount
    
@error_handler_common
def format_bytes(size, abbreviation=False):
    # Formats bytes to common abbreviation.
    bytes = size

    if abbreviation:
        if abbreviation == 'KB':
            bytes = size * 1024
        elif abbreviation == 'MB':
            bytes = size * (1024**2)
        elif abbreviation == 'GB':
            bytes = size * (1024**3)
        elif abbreviation == 'TB':
            bytes = size * (1024**4)
        elif abbreviation == 'PB':
            bytes = size * (1024**5)
        else:
            bytes = size

    if bytes >= 1024**5:
        formatted_bytes = "{:.1f} PB".format(bytes / (1024**5))
    elif bytes >= 1024**4:
        formatted_bytes = "{:.1f} TB".format(bytes / (1024**4))
    elif bytes >= 1024**3:
        formatted_bytes = "{:.1f} GB".format(bytes / (1024**3))
    elif bytes >= 1024**2:
        formatted_bytes = "{:.1f} MB".format(bytes / (1024**2))
    elif bytes >= 1024:
        formatted_bytes = "{:.1f} KB".format(bytes / 1024)
    else:
        formatted_bytes = '{:,.0f}'.format(bytes)
    
    return formatted_bytes

@error_handler_common
def format_currency(amount, ticker=False, decimal=False):
    # Formats integer value to currency format (e.g. 1234567.89 -> 1,234,567.89 $).
    # If currency symbol is unknown, replaced by ticker (e.g. 1234567.89 -> 1,234,567.89 USD).
    # If decimal is True, format amount with N decimal places.
    string_amount = str(amount) + '.'
    decimal_places = len(string_amount.split('.')[1]) if decimal is False else decimal
    formatted_amount = '{:,.{}f}'.format(amount, decimal_places)
    if ticker: # Check if currency symbol is available
        currency_symbol = CurrencySymbols().get_symbol(ticker)
        if currency_symbol:
            return currency_symbol + formatted_amount
        else:
            return ticker + formatted_amount
    else:
        return formatted_amount

@error_handler_common
def format_percentage(percentage):
    # Formats integer value to percentage format with 2 decimal rounding and commas for thousands.
    # (e.g -1234.567 -> -1,234.57 %) If value is non-negative, adds '+' symbol (e.g. 6.789 -> +6.79).
    formatted_percentage = '{:,.2f}'.format(round(percentage, 2))
    if formatted_percentage[0] == '-':
        return f"{formatted_percentage}%"
    else:
        return f"+{formatted_percentage}%"

@error_handler_common
def format_quantity(whole_number):
    # Formats integer value to space-separated whole number (e.g. 21000000 -> 21 000 000).
    formatted_number = '{:,.0f}'.format(whole_number).replace(',', ' ')
    return formatted_number

@error_handler_common
def format_utc(utc):
    # Strips UTC from 'T', 'Z' symbols and microseconds (e.g. 2024-01-02T23:27:24.911Z -> 2024-01-02 23:27:24).
    utc_time = datetime.strptime(utc, '%Y-%m-%dT%H:%M:%S.%fZ')
    time_without_utc_symbols = utc_time.strftime('%Y-%m-%d %H:%M:%S')
    return f'{time_without_utc_symbols}'

@error_handler_common
def convert_timestamp_to_utc(timestamp):
    # Converts milliseconds timestamp to seconds timestamp, then converts timestamp to UTC.
    if len(str(timestamp)) > 10: 
        timestamp = int(timestamp) / 1000
    utc = datetime.utcfromtimestamp(timestamp)
    utc_str = utc.strftime('%Y-%m-%d %H:%M:%S')
    return utc_str

@error_handler_common
def convert_utc_date_to_timestamp(utc):
    # Converts yyyy.mm.dd string to timestamp.
    utc_date = datetime.strptime(utc, '%Y-%m-%d')
    timestamp = int(utc_date.timestamp())
    return timestamp

@error_handler_common
def convert_date_to_days(date):
    # Converts yyyy.mm.dd to days between yyyy.mm.dd and now.
    if date.isdigit():
        days = int(date)
        return days
    elif date == 'max':
        days = 'max'
        return days
    else:
        try:
            datetime_past = datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            return 'error'
        datetime_now_utc = datetime.utcnow()
        days = (datetime_now_utc - datetime_past).days
        return days
    
def convert_utc_to_server_timezone(user_time_in_utc):
    # Converts user-provided 'HH:MM' UTC +0 input string to server timezone
    # (e.g. if server timezone is UTC +09:00, then '19:52' --> '04:52')
    server_timezone = datetime.now().astimezone().tzinfo
    server_utc_offset = server_timezone.utcoffset(datetime.utcnow()).total_seconds() / 3600
    user_utc_time = datetime.strptime(user_time_in_utc, "%H:%M")
    server_time = user_utc_time + timedelta(hours=server_utc_offset)
    return server_time.strftime("%H:%M")

@error_handler_common
def calculate_percentage_change(old, new):
    # Calculates percentage change between old and new value.
    if old == 0:
        old = 0.001
    percentage_change = new / (old / 100) - 100
    return percentage_change