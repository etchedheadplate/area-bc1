import os
import time
from datetime import datetime, timedelta

import config
from tools import get_api_data, format_currency, format_percentage, format_utc


def get_db_latest_values(db_latest_values):
    # Makes API call and parses JSON response to values variables. Variables formatted
    # for user presentation. Data is updated with regularity specified in user configuration.

    # User configuration related variables:        
    db_latest_values_path = config.databases[f'{db_latest_values}']['path']
    db_latest_values_file = db_latest_values_path + f'{db_latest_values}.txt'
    db_latest_values_update_time = config.databases[f'{db_latest_values}']['update']['time']
    db_latest_values_update_interval = config.databases[f'{db_latest_values}']['update']['interval']


    print(f'[{db_latest_values}] initializing:')
    if not os.path.isdir(db_latest_values_path):
        os.makedirs(db_latest_values_path, exist_ok=True)
        print(f'[{db_latest_values}]', db_latest_values_path, 'created')
    else:
        print(f'[{db_latest_values}]', db_latest_values_path, 'exists')

    # Regular values updates with new API data according to parameters defined by user configuration:
    while True:

        # Time-related variables formatted as specified in user configuration for correct update period:
        time_current = datetime.strptime(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
        time_update = datetime.strptime(str(time_current)[:-len(db_latest_values_update_time)] + db_latest_values_update_time, '%Y-%m-%d %H:%M:%S')

        print(time_current, f'[{db_latest_values}] updating:')

        # Call to API and creation of values variables based on response data:
        response = get_api_data(db_latest_values)

        LAST_UPDATED = format_utc(response['last_updated'])

        PRICE_CURRENT = format_currency(response['current_price'][f'{config.currency_vs}'], config.currency_vs_ticker)
        PRICE_CHANGE_PERCENTAGE_IN_CURRENCY_24H = format_percentage(response['price_change_percentage_24h_in_currency'][f'{config.currency_vs}'])
        PRICE_CHANGE_24H_IN_CURRENCY = format_currency(response['price_change_24h_in_currency'][f'{config.currency_vs}'], config.currency_vs_ticker)
        PRICE_HIGH_24H = format_currency(response['high_24h'][f'{config.currency_vs}'], config.currency_vs_ticker)
        PRICE_LOW_24H = format_currency(response['low_24h'][f'{config.currency_vs}'], config.currency_vs_ticker)
        
        MARKET_CAP = format_currency(response['market_cap'][f'{config.currency_vs}'], config.currency_vs_ticker)
        MARKET_CAP_CHANGE_24H_PERCENTAGE = format_percentage(response['market_cap_change_percentage_24h_in_currency'][f'{config.currency_vs}'])
        MARKET_CAP_CHANGE_24H = format_currency(response['market_cap_change_24h_in_currency'][f'{config.currency_vs}'], config.currency_vs_ticker)
        FULLY_DILUTED_VALUATION = format_currency(response['fully_diluted_valuation'][f'{config.currency_vs}'], config.currency_vs_ticker)
        
        ALL_TIME_HIGH_CHANGE_PERCENTAGE = format_percentage(response['ath_change_percentage'][f'{config.currency_vs}'])
        ALL_TIME_HIGH = format_currency(response['ath'][f'{config.currency_vs}'], config.currency_vs_ticker)
        ALL_TIME_HIGH_DATE = format_utc(response['ath_date'][f'{config.currency_vs}'])    
        
        TOTAL_VOLUME = format_currency(response['total_volume'][f'{config.currency_vs}'], config.currency_vs_ticker)
        SUPPLY_TOTAL = format_currency(response['total_supply'], config.currency_crypto_ticker)
        SUPPLY_CIRCULATING = format_currency(response['circulating_supply'], config.currency_crypto_ticker)
    
        # Format values for user presentation:
        info_pair_update = f'{config.currency_pair} at {LAST_UPDATED}:\n'
        info_price = f'Price: {PRICE_CURRENT}\nΔ24h: {PRICE_CHANGE_PERCENTAGE_IN_CURRENCY_24H} ({PRICE_CHANGE_24H_IN_CURRENCY})\n24h High: {PRICE_HIGH_24H}\n24h Low: {PRICE_LOW_24H}\n'
        info_market_cap = f'Market Cap: {MARKET_CAP}\nΔ24h: {MARKET_CAP_CHANGE_24H_PERCENTAGE} ({MARKET_CAP_CHANGE_24H})\nFDV: {FULLY_DILUTED_VALUATION}\n'
        info_ath = f'ATH: {ALL_TIME_HIGH_CHANGE_PERCENTAGE} ({ALL_TIME_HIGH})\nATH Date: {ALL_TIME_HIGH_DATE}\n'
        info_supply = f'Total Volume: {TOTAL_VOLUME}\nTotal Supply: {SUPPLY_TOTAL}\nCirculating: {SUPPLY_CIRCULATING}'

        with open(db_latest_values_file, 'w') as file:
            file.write(f"{info_pair_update}\n{info_price}\n{info_market_cap}\n{info_ath}\n{info_supply}")
        
        # Schedule next update time. Check if current time > update time. If is, shift update time
        # by user configuration specified update interval untill update time > current time.
        while time_current > time_update:
            time_update = time_update + timedelta(hours=db_latest_values_update_interval)
            print(time_current, f'[{db_latest_values}] current time > update time, update planned to {time_update}')
        else:
            print(time_current, f'[{db_latest_values}] update planned to {time_update}')

        seconds_untill_upgrade = (time_update - time_current).total_seconds()

        # Update data chart with regularity specified in user configuration:
        time.sleep(seconds_untill_upgrade)


if __name__ == '__main__':
    get_db_latest_values('latest_values')