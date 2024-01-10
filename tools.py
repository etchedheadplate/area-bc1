import requests
from datetime import datetime
from currency_symbols import CurrencySymbols

import config


def get_api_data(database):
# Builds formatted URL to API based on user configuration and retrieves JSON data.

    # User configuration related variables:
    db_api = config.databases[f'{database}']['api']
    db_type = config.databases[f'{database}']['type']
    db_custom_params = config.databases[f'{database}']['custom_params'] 

    api_base = config.api[f'{db_api}']['base']
    api_endpoint = config.api[f'{db_api}']['endpoint'][f'{db_type}']['name']
    api_params = config.api[f'{db_api}']['endpoint'][f'{db_type}']['params']
    api_response_subdict = config.api[f'{db_api}']['endpoint'][f'{db_type}']['subdict']

    # Build queries list from standart API parameters and custom database parameters:
    api_params.update(db_custom_params)
    query_params = []
    for query, value in api_params.items():
        api_params[f'{query}']=f'{value}'
        query_params.append(f"{query}={value}")
    
    # Build formatted URL to API and retrieve JSON:
    api_url = f"{api_base}{api_endpoint}?{'&'.join(query_params)}"
    api_response = requests.get(api_url)
    response_data = api_response.json()

    # Check if needed data is a subdictionary of retrieved JSON:
    if api_response_subdict:
        return response_data[api_response_subdict]
    else:
        return response_data


def format_currency(amount, ticker):
    # Formats integer value to currency format (e.g. 1234567.89 -> 1,234,567.89 $).
    # If currency symbol is unknown replaced by ticker (e.g. 1234567.89 -> 1,234,567.89 USD).
    
    currency_symbol = CurrencySymbols().get_symbol(ticker)
    if currency_symbol:
        return currency_symbol + ' {:,.2f}'.format(amount)
    else:
        return ticker + ' {:,.2f}'.format(amount)


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

    percentage_change = new / (old / 100) - 100
    return percentage_change













