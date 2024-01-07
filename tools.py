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


def select_chart(period):
    # Selects chart based on days period. Used for history values and plot selection. 90 days
    # chart skipped because of 1-hour interval, which makes it useless in history values case.
    
    if isinstance(period, int):
        days = int(period)
        if days <= 1:
            chart = 'latest_chart'
            chart_for_history_values = chart
        elif days <= 90:
            chart = 'history_chart_days_90'
            chart_for_history_values = 'history_chart_days_max'
        else:
            chart = 'history_chart_days_max'
            chart_for_history_values = chart
    else:
        chart = 'history_chart_days_max'
        chart_for_history_values = chart
    
    return chart, chart_for_history_values


def calculate_chart_interval(period):
    # Calculates interval between history chart rows based on CoinGecko API intervals.
    
    if isinstance(period, int):
        if period <= 1:
            one_day_as_five_minutes_chunks = period * 288 - 1
            interval = one_day_as_five_minutes_chunks
        elif period <= 90:
            one_day_as_one_hour_chunks = period * 24
            interval = one_day_as_one_hour_chunks
        else:
            one_day_as_one_day_chunks = period * 1
            interval = one_day_as_one_day_chunks
    else:
        one_day_as_one_day_chunks = period * 1
        interval = one_day_as_one_day_chunks
    
    return interval


def calculate_percentage_change(old, new):
    # Calculates percentage change between old and new value.

    percentage_change = new / (old / 100) - 100
    return percentage_change


def format_time_axis(timestamp, period):
    # Formats time axis to show granular time depending on time period.
    
    # Convert milliseconds timestamp to seconds timestamp, then convert timestamp to UTC:
    if len(str(timestamp)) > 10:
        timestamp /= 1000

    date_object = datetime.utcfromtimestamp(timestamp)

    # Format time according to plot time period:
    if period <= 1:
        formatted_date = date_object.strftime('%H:%M')
    elif period <= 6:
        formatted_date = date_object.strftime('%d.%m.%Y\n%H:%M')
    elif period <= 365:
        formatted_date = date_object.strftime('%d.%m.%Y')
    elif period <= 1825:
        formatted_date = date_object.strftime('%m.%Y')
    else:
        formatted_date = date_object.strftime('%Y')
    return formatted_date


def format_money_axis(amount):
    # Formats money axis to common abbreviation depending on money amount.

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



def define_market_movement(percentage_change):
    # Defines % of price change as market movement in given period. Based on
    # market movement selects plot background and color for plot legend.

    for background_name in config.plot['backgrounds']:
        market_movement = config.plot['backgrounds'][f'{background_name}']['range']
        if market_movement[0] <= percentage_change <= market_movement[1]:
            return background_name









