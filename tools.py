import os
import json
import time
import asyncio
import requests
import schedule
import importlib
import functools
import pandas as pd

from memory_profiler import profile
from datetime import datetime
from currency_symbols import CurrencySymbols

import config
from logger import main_logger




'''
Functions related to fetching raw API data, creating, saving and updating database files.
'''

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
                    main_logger.warning(f'[chart] unknown type of parsed api response for {database}: {type(api_parsed)}')
            elif type(file_columns) is list:
                response_columns = pd.DataFrame(list(response.items()), columns=file_columns)
            else:
                main_logger.warning(f'[chart] unknown type of config param file_columns for {database}: {type(file_columns)}')
        response_columns.to_csv(file, index=False)
    elif api_extention == 'csv':
        for api_endpoint in api_endpoints:
            response = get_api_data(api_base, api_endpoint, api_params)
            with open(file, 'wb') as response_file:
                response_file.write(response.content)
    else:
        main_logger.warning(f'[chart] unknown file extention for {database}')

    main_logger.info(f'[chart] {database} updated')
    

def make_snapshot_data(database):
    # Creates snapshot path if it doesn't exists. Saves data to database as JSON file.
    snapshot = config.snapshots[f'{database}']

    # User configuration related variables:
    api_base = snapshot['api']['base']
    api_endpoints = snapshot['api']['endpoints']
    api_params = snapshot['api']['params']
    api_subdict = snapshot['api']['subdict']

    file_path = snapshot['file']['path']
    file_name = snapshot['file']['name']
    file = file_path + file_name

    # Create snapshot directory if it doesn' exists:
    if not os.path.isdir(file_path):
        os.makedirs(file_path, exist_ok=True)

    # Call to API and creation JSON file based on response data:
    response = get_api_data(api_base, api_endpoints, api_params)
    response = response.json()[api_subdict] if api_subdict else response.json()
    with open(file, 'w') as json_file:
        json.dump(response, json_file)
    
    main_logger.info(f'[snapshot] {database} updated')


def format_update_seconds(seconds):
    # Formats seconds to schedule module format.

    seconds = round(abs(seconds))
    seconds = int(seconds - seconds // 60 * 60) if seconds >= 60 else seconds
    formatted_seconds = f':{seconds}' if seconds >= 10 else f':0{seconds}'
    return formatted_seconds


def clean_databases():
    databases_path = 'db/'
    extentions_to_remove = ['.md', '.jpg']
    files_removed = 0
    for root, dirs, files in os.walk(databases_path):
        for file in files:
            file_name, file_extension = os.path.splitext(file)
            if file_extension.lower() in extentions_to_remove:
                file_path = os.path.join(root, file)
                os.remove(file_path)
                files_removed += 1
    main_logger.info(f'[databases] removed {files_removed} files')


# @profile
def update_databases():
    # Initializes databases. Assigns proper function to handle each database.
    # Schedules regular updates for each database based on user configuration.

    charts = config.charts
    snapshots = config.snapshots
    updates = config.updates
    delay = config.delay

    clean_databases()

    main_logger.info(f'[databases] updating charts (~{len(charts) * delay} seconds)')
    for chart_name in charts.keys():
        make_chart_data(chart_name) # Database chart initialized for the first time
        time.sleep(delay) # Delay to not exceed rate limits for charts with same API
    for chart_name in charts.keys():
        chart_update_minutes = updates[f'{chart_name}']['minutes']
        chart_update_seconds = format_update_seconds(updates[f'{chart_name}']['seconds'])
        schedule.every(chart_update_minutes).minutes.at(chart_update_seconds).do(make_chart_data, chart_name)
    main_logger.info('[databases] future charts updates scheduled')

    main_logger.info(f'[databases] updating snapshots (~{len(snapshots) * delay} seconds)')
    for snapshot_name in snapshots.keys():
        make_snapshot_data(snapshot_name) # Database snapshot initialized for the first time
        time.sleep(delay) # Delay to not exceed rate limits for snapshots with same API
    for snapshot_name in snapshots.keys():
        snapshot_update_minutes = updates[f'{snapshot_name}']['minutes']
        snapshot_update_seconds = format_update_seconds(updates[f'{snapshot_name}']['seconds'] + delay)
        schedule.every(snapshot_update_minutes).minutes.at(snapshot_update_seconds).do(make_snapshot_data, snapshot_name)
    main_logger.info('[databases] future snapshots updates scheduled')

    # List of all databases no matter if chart or snapshot:
    databases = list(charts.keys() | snapshots.keys())
    current_directory = os.path.dirname(os.path.abspath(__file__))
    for database in databases:
        module_file = os.path.join(current_directory, 'commands', f'{database}.py')
        if os.path.exists(module_file):
            module_name = f'commands.{database}'
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
    main_logger.info('[databases] future image updates scheduled')
    main_logger.info('[databases] future markdown updates scheduled')

    schedule.every(1).days.at('00:00:00').do(functools.partial(clean_databases))

    while True:
        schedule.run_pending()
        time.sleep(60)


def define_key_metric_movement(plot, key_metric_change_percentage):
    # Defines % of price change as market movement in given period. Based on
    # market movement selects plot background and color for plot legend.

    for background in plot['backgrounds']:
        key_metric_movement = plot['backgrounds'][f'{background}']['range']
        if key_metric_movement[0] <= key_metric_change_percentage < key_metric_movement[1]:
            return background
        

def format_time_axis(timestamp, days):
    # Converts timestamps from chart's Date columns to UTC and appropriately formats time
    # to plot period.
    
    # Convert milliseconds timestamp to seconds:
    if len(str(int(timestamp))) > 10:
        timestamp /= 1000

    # Convert timestamp to UTC:
    date_object = datetime.utcfromtimestamp(timestamp)

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
Functions related to formatting values data.
'''

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


def format_percentage(percentage):
    # Formats integer value to percentage format with 2 decimal rounding and commas for thousands.
    # (e.g -1234.567 -> -1,234.57 %) If value is non-negative, adds '+' symbol (e.g. 6.789 -> +6.79).

    formatted_percentage = '{:,.2f}'.format(round(percentage, 2))
    if formatted_percentage[0] == '-':
        return f"{formatted_percentage}%"
    else:
        return f"+{formatted_percentage}%"


def format_quantity(whole_number):
    # Formats integer value to space-separated whole number (e.g. 21000000 -> 21 000 000).

    formatted_number = '{:,.0f}'.format(whole_number).replace(',', ' ')
    return formatted_number


def format_utc(utc):
    # Strips UTC from 'T', 'Z' symbols and microseconds (e.g. 2024-01-02T23:27:24.911Z -> 2024-01-02 23:27:24).

    utc_time = datetime.strptime(utc, '%Y-%m-%dT%H:%M:%S.%fZ')
    time_without_utc_symbols = utc_time.strftime('%Y-%m-%d %H:%M:%S')
    return f'{time_without_utc_symbols}'


def convert_timestamp_to_utc(timestamp):
    # Converts milliseconds timestamp to seconds timestamp, then converts timestamp to UTC.
      
    if len(str(timestamp)) > 10: 
        timestamp = int(timestamp) / 1000
    utc = datetime.utcfromtimestamp(timestamp)
    utc_str = utc.strftime('%Y-%m-%d %H:%M:%S')
    return utc_str


def convert_utc_date_to_timestamp(utc):
    # Converts yyyy.mm.dd string to timestamp.
    
    utc_date = datetime.strptime(utc, '%Y-%m-%d')
    timestamp = int(utc_date.timestamp())
    return timestamp


def convert_date_to_days(date):
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


def calculate_percentage_change(old, new):
    # Calculates percentage change between old and new value.

    if old == 0:
        old = 0.001
    percentage_change = new / (old / 100) - 100
    return percentage_change













