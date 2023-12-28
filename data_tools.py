'''
Various functions used in other modules.
'''


import requests
from datetime import datetime, timezone
from currency_symbols import CurrencySymbols

import config


'''API related functions'''

def get_api_data(database):
# Builds formatted URL to API based on user configuration and retrieves JSON data

    # Local user configuration related variables:       
    api_name = config.database[f'{database}']['api']
    api_base = config.api[f'{api_name}']['base']
    api_endpoint = config.api[f'{api_name}']['endpoint'][f'{database}']['name']
    api_params = config.api[f'{api_name}']['endpoint'][f'{database}']['params']

    # Specific queries defined by user configuration
    query_params = []
    for query, value in api_params.items():
        api_params[f'{query}']=f'{value}'
        query_params.append(f"{query}={value}")
    
    # Build formatted url to API and retrieve JSON
    api_url = f"{api_base}{api_endpoint}?{'&'.join(query_params)}"
    api_response = requests.get(api_url)
    api_data = api_response.json()

    return api_data


'''Functions to display or format data'''

def view_json_contents(json, indent=0):
    # Allows to view nested dictionaries in human-readable form
    for key, value in json.items():
        if isinstance(value, dict): # if value is nested dictionary
            print(' ' * indent + f'{key}:') # prints key associated with value as nested dictionary
            view_json_contents(value, indent + 4) # recursively calls view_json_contents() until no nested dictionaries left
        else:
            print(' ' * indent + f'{key}: {value}') # prints key and value

def check_file_length(file_path):
    file=open(file_path, 'r')
    file_lines = file.readlines()
    list_of_lines=[]
    for line in file_lines:
        list_of_lines.append(line)
    print(len(list_of_lines))
    file.close()

def format_currency(amount, ticker):
    # Converts endpoint values to currency format with spaces, commas and currency symbol
    currency_symbols = CurrencySymbols()
    currency_symbol = currency_symbols.get_symbol(ticker)
    symbol = ''
    if currency_symbol:
        symbol = currency_symbol
    else:
        symbol = ticker
    formatted_amount = '{:,.2f} '.format(amount) + symbol # formatted with symbols
    return formatted_amount

def format_percentage(percentage):
    # Converts endpoint values to percentage format
    formatted_percentage = f"{percentage:.2f} %"
    return formatted_percentage

def format_things(number):
    # Converts endpoint values to space-separated whole number
    formatted_number = '{:,.0f}'.format(number).replace(',', ' ')
    return formatted_number


'''Functions to display or format time'''

def convert_timestamp_to_utc(timestamp):
    # Converts UNIX timestamp to UTC    
    try:
        if len(str(timestamp)) > 10: # if timestamp in milliseconds...
            timestamp /= 1000 # converts it to seconds
        utc_datetime = datetime.utcfromtimestamp(timestamp)
        return utc_datetime
    except Exception as e:
        return str('convert_timestamp_to_utc failed')

def convert_utc_to_timestamp(utc):
    # Converts imput in form of dd.mm.yyyy string to UNIX timestamp  
    formatted_utc = datetime.strptime(str(utc), '%Y-%m-%d %H:%M:%S').strftime('%d.%m.%Y')
    date_utc = datetime.strptime(formatted_utc, '%d.%m.%Y')
    date_timestamp = int(date_utc.timestamp())
    return date_timestamp

def strip_utc_symbols(utc):
    # Strips UTC from 'T' an 'Z' symbols
    utc_time = datetime.strptime(utc, '%Y-%m-%dT%H:%M:%S.%fZ')
    time_without_utc_symbols = utc_time.strftime('%Y-%m-%d %H:%M:%S')
    return time_without_utc_symbols

def set_24h_time_period():
    current_datetime_utc = datetime.now(timezone.utc)
    current_date_utc = current_datetime_utc.date()
    combined_current_datetime = datetime.combine(current_date_utc, datetime.min.time())
    period_timestamp = 86400
    today_timestamp = int(combined_current_datetime.timestamp())
    yesterday_timestamp = today_timestamp - period_timestamp
    return yesterday_timestamp, today_timestamp, period_timestamp

def set_custom_time_period():
    # Converts input in form of 2 dd.mm.yy strings to UNIX timestamp and calculates the difference
    start_date = datetime.strptime(str(input('Enter dd.mm.yyyy start date: ')), '%d.%m.%Y')
    end_date = datetime.strptime(str(input('Enter dd.mm.yyyy end date: ')), '%d.%m.%Y')
    start_timestamp = convert_utc_to_timestamp(start_date)
    end_timestamp = convert_utc_to_timestamp(end_date)
    period_timestamp = end_timestamp - start_timestamp
    return start_timestamp, end_timestamp, period_timestamp


'''Chart related functions'''

def calculate_price_change_percentage(start_price, end_price):
    price_change_percentage = end_price / (start_price / 100) - 100
    return price_change_percentage

'''def select_plot_background(price_change_percentage):
    # Selects plot background based on % of price change in given period and returns path to image
    for image_params in plot_background_image:
        percentage_range = image_params[1]
        if percentage_range[0] <= price_change_percentage <= percentage_range[1]:
            return image_params'''

def format_money_axis(amount):
    # Formats money to common abbreviation
    if amount >= 1_000_000_000_000_000:
        formatted_amount = "{:.1f} Qn".format(amount / 1_000_000_000_000_000)
    elif amount >= 1_000_000_000_000:
        formatted_amount = "{:.1f} T".format(amount / 1_000_000_000_000)
    elif amount >= 1_000_000_000:
        formatted_amount = "{:.1f} B".format(amount / 1_000_000_000)
    elif amount >= 1_000_000:
        formatted_amount = "{:.1f} M".format(amount / 1_000_000)
    elif amount >= 1_000:
        formatted_amount = "{:.1f} K".format(amount / 1_000)
    else:
        formatted_amount = "{:.2f}".format(amount)
    return formatted_amount

def format_time_axis(timestamp, period):
    # Converts UNIX timestamp to UTC    
    days = period / 60 / 60 / 24 # converts period timestamp to days
    if len(str(timestamp)) > 10: # if timestamp in milliseconds...
        timestamp /= 1000 # converts it to seconds 
    date_object = datetime.utcfromtimestamp(timestamp)
    if days <= 90:
        try:           
            formatted_date = date_object.strftime('%d.%m.%Y\n%H:%M')
            return formatted_date
        except Exception as e:
            return str(e)
    elif days > 90:
        try:
            formatted_date = date_object.strftime('%d.%m.%Y')
            return formatted_date
        except Exception as e:
            return str(e)



