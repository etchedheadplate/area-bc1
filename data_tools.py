'''
Various functions used in other modules.
'''


import requests
from datetime import datetime
from currency_symbols import CurrencySymbols
from data_config import plot_background_path, plot_background_image
from api.coingecko import API_ERROR_CODES, API_ENDPOINTS


# API related functions

def build_api_url(base, endpoint, **kwargs):
    # Builds URL with specific query parameters to API endpoint
    query_parameters = [] # empty list for query parameters
    for key, value in kwargs.items():
        query_parameters.append(f"{key}={value}") # parameters are copied from dictionary to list...
    url = f"{base}{endpoint}?{'&'.join(query_parameters)}" # ...so they can be formated correctly to queries...
    return url # ... and returned as correct URL to API endpoint 

def get_json_data(url):
    # Returns JSON object or error code
    response = requests.get(url) # executes GET command to endpoint
    if response.status_code == 200: # if status code is OK... 
        data = response.json() # ...builds JSON object...
        return data # ...and returns JSON object
    elif response.status_code in API_ERROR_CODES: # if known error status code is recieved...
        return f'{response.status_code}:{API_ERROR_CODES[response.status_code]}' # ...returns status code and description
    else:
        return response.status_code, 'Unknown error' # if error is unknown returns status code

def get_data(base, endpoint, **kwargs):
    # Returns unformatted dictionary with data provided by API endpoint
    endpoint_params = API_ENDPOINTS.get(endpoint) # standart parameters from API parameters dictionary
    for key, value in kwargs.items(): # custom API parameters passed as kwargs
        if key == 'start': # if one of the parameters named 'start'...
            endpoint_params['from']=f'{value}' # ...it renamed to 'from' (due to Python limitations)
        else: # else all standart parameters passed as valid for the link
            endpoint_params[f'{key}']=f'{value}'
    endpoint_url = build_api_url(base, endpoint, **endpoint_params)
    endpoint_data = get_json_data(endpoint_url)
    return endpoint_data


# Functions to display or format data

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

def convert_timestamp_to_utc(timestamp):
    # Converts UNIX timestamp to UTC    
    try:
        if len(str(timestamp)) > 10: # if timestamp in milliseconds...
            timestamp /= 1000 # converts it to seconds
        utc_datetime = datetime.utcfromtimestamp(timestamp)
        return utc_datetime
    except Exception as e:
        return str(e)


# Chart related functions

def select_plot_background(price_change_percentage):
    # Selects plot background based on % of price change in given period and returns path to image
    for image in plot_background_image:
        range = image[1]
        if range[0] <= price_change_percentage <= range[1]:
            return plot_background_path + image[0]

def format_money_axis(amount):
    # Formats money to common abbreviation
    if amount >= 1_000_000_000_000_000:
        formatted_amount = "{:.0f} Qn".format(amount / 1_000_000_000_000_000)
    elif amount >= 1_000_000_000_000:
        formatted_amount = "{:.0f} T".format(amount / 1_000_000_000_000)
    elif amount >= 1_000_000_000:
        formatted_amount = "{:.0f} B".format(amount / 1_000_000_000)
    elif amount >= 1_000_000:
        formatted_amount = "{:.0f} M".format(amount / 1_000_000)
    elif amount >= 1_000:
        formatted_amount = "{:.0f} K".format(amount / 1_000)
    else:
        formatted_amount = "{:.2f}".format(amount)
    return formatted_amount

def format_time_axis(timestamp, period):
    # Converts UNIX timestamp to UTC    
    if len(str(timestamp)) > 10: # if timestamp in milliseconds...
        timestamp /= 1000 # converts it to seconds 
    date_object = datetime.utcfromtimestamp(timestamp)
    if period <= 3:
        try:           
            formatted_date = date_object.strftime('%d.%m.%Y %H:%M:%S')
            return formatted_date
        except Exception as e:
            return str(e)
    elif period > 3:
        try:
            formatted_date = date_object.strftime('%d.%m.%Y')
            return formatted_date
        except Exception as e:
            return str(e)

def convert_utc_to_timestamp():
    # Converts imput in form of dd.mm.yy string to UNIX timestamp  
    start_date = datetime.strptime(str(input('Enter dd.mm.yyyy start date: ')), '%d.%m.%Y')
    end_date = datetime.strptime(str(input('Enter dd.mm.yyyy end date: ')), '%d.%m.%Y')
    start_timestamp = int(start_date.timestamp())
    end_timestamp = int(end_date.timestamp())
    return (f'start={start_timestamp}', f'to={end_timestamp}')

