import os
import json
import requests
import schedule
import importlib
import pandas as pd

from datetime import datetime
from currency_symbols import CurrencySymbols

import config


'''
Functions related to fetching raw API data, creating, saving and updating database files.
'''

def get_api_data(base, endpoint, params=False, subdict=False):
# Builds formatted URL to API based on user configuration and retrieves JSON data.

    # Build queries list from standart API parameters and custom database parameters:
    query_params = []
    if params:
        for query, value in params.items():
            params[f'{query}']=f'{value}'
            query_params.append(f"{query}={value}")

    
    # Build formatted URL to API and get data response. If response type is JSON,
    # check if needed data is a subdictionary of retrieved JSON:
    api_url = f"{base}{endpoint}?{'&'.join(query_params)}"
    api_response = requests.get(api_url)
    response_data = api_response.json()
    if subdict:
        return response_data[subdict]
    else:
        return response_data


def make_chart_data(database):
    # Creates chart path if it doesn't exists. Distributes API data to columns using
    # 'date' column as common denominator. Saves data to database as CSV file.

    time_current = datetime.strptime(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
    chart = config.databases['charts'][f'{database}']

    # User configuration related variables:
    api_base = chart['api']['base']
    api_endpoints = chart['api']['endpoints']
    api_params = chart['api']['params']
    api_subdict = chart['api']['subdict']
    api_response_type = chart['api']['response_type']

    file_path = chart['file']['path']
    file_name = chart['file']['name']
    file_columns = chart['file']['columns']
    file = file_path + file_name

    # Create chart directory if it doesn' exists:
    if not os.path.isdir(file_path):
        os.makedirs(file_path, exist_ok=True)

    # Empty DataFrame for later filling with response DataFrame:
    response_columns = pd.DataFrame({'date': []})

    # Call to API and creation of DataFrame objects based on response data:
    for api_endpoint in api_endpoints:
        response = get_api_data(
                api_base,
                api_endpoint,
                api_params,
                api_subdict)
        
        # Response proccesed differently if data returned as list or dict:
        if api_response_type == list:
            for row, column in file_columns[api_endpoint].items():
                response_data = pd.DataFrame(response[row], columns=['date', f'{column}'])
                response_columns = response_columns.merge(response_data, on='date', how='outer').dropna().sort_values(by='date')
        else:
            response_data = pd.DataFrame(response).rename(columns=file_columns[api_endpoint])
            response_columns = response_columns.merge(response_data, on='date', how='outer').dropna().sort_values(by='date')

    # DataFrame with response data saved to file:
    response_columns.to_csv(file, index=False)
    print(time_current, f'[{database}] chart made')

    try:
        # Dynamically import module associated with database and draw plot:
        module_name = database
        module = importlib.import_module(module_name)
        draw_plot_function = getattr(module, 'draw_plot', None)

        if draw_plot_function is not None and callable(draw_plot_function):
            draw_plot_function()
            print(time_current, f'[{database}] plot drawn')
        else:
            print(time_current, f'[{database}] draw_plot() not found in module {module_name}')
    except ImportError:
        print(time_current, f'[{database}] module not found')
    

def make_snapshot_data(database):
    # Creates snapshot path if it doesn't exists. Saves data to database as JSON file.

    time_current = datetime.strptime(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
    snapshot = config.databases['snapshots'][f'{database}']

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
    response = get_api_data(
        api_base,
        api_endpoints,
        api_params,
        api_subdict)

    with open(file, 'w') as json_file:
        json.dump(response, json_file)
        print(time_current, f'[{database}] snapshot made')

    # Dynamically import module associated with database and make markdown:
    module_name = database
    module = importlib.import_module(module_name)
    write_markdown_function = getattr(module, 'write_markdown', None)

    if write_markdown_function is not None and callable(write_markdown_function):
        write_markdown_function()
        print(time_current, f'[{database}] markdown written')
    else:
        print(time_current, f'[{database}] write_markdown() not found in module {module_name}')


def update_all_databases():
    # Assigns proper function to handle database. Schedules regular updates
    # based on user configuration.
    
    for db_type, db_list in config.databases.items():
        for db_name, params in db_list.items():
            update_interval = params['update']['interval']
            update_seconds = params['update']['seconds']
            update_function = make_chart_data if db_type == 'charts' else make_snapshot_data
            schedule.every(update_interval).minutes.at(update_seconds).do(update_function, db_name)
    
    while True:
        schedule.run_pending()

'''
Functions related to formatting plot data.
'''

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
        formatted_date = date_object.strftime('%d.%m.%Y\n%H:%M')
    elif days <= 365:
        formatted_date = date_object.strftime('%d.%m.%Y')
    elif days <= 1825:
        formatted_date = date_object.strftime('%m.%Y')
    else:
        formatted_date = date_object.strftime('%Y')
    return formatted_date


'''
Functions related to formatting values data.
'''

def format_amount(amount, ticker=False):
    # Formats amount to common abbreviation.

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
        formatted_amount = "{:.2f}".format(amount)
    
    if ticker:
        currency_symbol = CurrencySymbols().get_symbol(ticker)
        if currency_symbol:
            return currency_symbol + formatted_amount
        else:
            return ticker + formatted_amount
    else:
        return formatted_amount


def format_currency(amount, ticker, decimal=False):
    # Formats integer value to currency format (e.g. 1234567.89 -> 1,234,567.89 $).
    # If currency symbol is unknown, replaced by ticker (e.g. 1234567.89 -> 1,234,567.89 USD).
    # If decimal is True, format amount with N decimal places.

    # Check if currency symbol is available
    currency_symbol = CurrencySymbols().get_symbol(ticker)

    # Set decimal places based on decimal argument
    decimal_places = 2 if decimal is False else decimal

    # Format amount with the specified decimal places
    formatted_amount = '{:,.{}f}'.format(amount, decimal_places)

    if currency_symbol:
        return currency_symbol + formatted_amount
    else:
        return ticker + formatted_amount


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


def calculate_percentage_change(old, new):
    # Calculates percentage change between old and new value.

    if old == 0:
        old = 0.001
    percentage_change = new / (old / 100) - 100
    return percentage_change













