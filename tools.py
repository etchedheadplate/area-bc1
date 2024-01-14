import requests
import numpy as np
from datetime import datetime
from currency_symbols import CurrencySymbols

import config


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

    percentage_change = new / (old / 100) - 100
    return percentage_change













