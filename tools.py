import requests
from datetime import datetime, timezone
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
        return '{:,.2f} '.format(amount) + currency_symbol
    else:
        return '{:,.2f} '.format(amount) + ticker


def format_percentage(percentage):
    # Formats integer value to percentage format with 2 decimal rounding and commas for thousands.
    # (e.g -1234.567 -> -1,234.57 %) If value is non-negative, adds '+' symbol (e.g. 6.789 -> +6.79).

    formatted_percentage = '{:,.2f}'.format(round(percentage, 2))
    if formatted_percentage[0] == '-':
        return f"{formatted_percentage} %"
    else:
        return f"+{formatted_percentage} %"


def format_quantity(whole_number):
    # Formats integer value to space-separated whole number (e.g. 21000000 -> 21 000 000).

    formatted_number = '{:,.0f}'.format(whole_number).replace(',', ' ')
    return formatted_number


def format_utc(utc):
    # Strips UTC from 'T', 'Z' symbols and microseconds (e.g. 2024-01-02T23:27:24.911Z -> 2024-01-02 23:27:24).

    utc_time = datetime.strptime(utc, '%Y-%m-%dT%H:%M:%S.%fZ')
    time_without_utc_symbols = utc_time.strftime('%Y-%m-%d %H:%M:%S')
    return time_without_utc_symbols

















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



