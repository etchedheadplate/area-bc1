import config
from tools import get_api_data, format_currency, format_percentage, format_quantity, format_utc

def update_granular_data(granular_data):
    response = get_api_data(granular_data)
    
    granular_data_api = config.databases[f'{granular_data}']['api']
    granular_data_type = config.databases[f'{granular_data}']['type']
    granular_data_file = config.databases[f'{granular_data}']['path']
    granular_data_values = config.api[f'{granular_data_api}']['endpoint'][f'{granular_data_type}']['values']
#    granular_data_update_time = config.databases[f'{granular_data}']['update']['time']
#    granular_data_update_interval = config.databases[f'{granular_data}']['update']['interval']
#    granular_data_update_allow_rewrite = config.databases[f'{granular_data}']['update']['allow_rewrite']

    currency_values = []
    for key, value in granular_data_values['currency'].items():
        currency_values.append(f"{key}: {format_currency(response[f'{value}'][f'{config.vs_currency}'], config.ticker)}")

    percentage_values = []
    for key, value in granular_data_values['percentage'].items():
        percentage_values.append(f"{key}: {format_percentage(response[f'{value}'][f'{config.vs_currency}'])}")
    
    quantity_values = []
    for key, value in granular_data_values['quantity'].items():
        quantity_values.append(f"{key}: {format_quantity(response[f'{value}'])}")

    dates_values = []
    for key, value in granular_data_values['dates'].items():
        dates_values.append(f"{key}: {format_utc(response[f'{value}'])}")


    with open(granular_data_file, 'w') as file:
        for value in currency_values:
            file.write(f"{value}\n")
        for value in percentage_values:
            file.write(f"{value}\n")
        for value in quantity_values:
            file.write(f"{value}\n")
        for value in dates_values:
            file.write(f"{value}\n")


update_granular_data('data_granular_latest')