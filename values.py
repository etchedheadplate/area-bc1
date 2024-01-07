import json
import pandas as pd

import config
from tools import (calculate_chart_interval,
                   calculate_percentage_change,
                   convert_timestamp_to_utc,
                   format_utc,
                   format_currency,
                   format_percentage)


def write_latest_values():

    # User configuration related variables:
    latest_values_path = config.databases['latest_api_data']['path']    
    latest_api_data_file = latest_values_path + config.databases['latest_api_data']['filename']
    latest_values_file = latest_values_path + 'latest_values.txt'

    with open (latest_api_data_file, 'r') as json_file:
        
        api_data = json.load(json_file)

        LAST_UPDATED = format_utc(api_data['last_updated'])

        PRICE_CURRENT = format_currency(api_data['current_price'][f'{config.currency_vs}'], config.currency_vs_ticker)
        PRICE_CHANGE_PERCENTAGE_IN_CURRENCY_24H = format_percentage(api_data['price_change_percentage_24h_in_currency'][f'{config.currency_vs}'])
        PRICE_CHANGE_24H_IN_CURRENCY = format_currency(api_data['price_change_24h_in_currency'][f'{config.currency_vs}'], config.currency_vs_ticker)
        PRICE_HIGH_24H = format_currency(api_data['high_24h'][f'{config.currency_vs}'], config.currency_vs_ticker)
        PRICE_LOW_24H = format_currency(api_data['low_24h'][f'{config.currency_vs}'], config.currency_vs_ticker)
        
        MARKET_CAP = format_currency(api_data['market_cap'][f'{config.currency_vs}'], config.currency_vs_ticker)
        MARKET_CAP_CHANGE_24H_PERCENTAGE = format_percentage(api_data['market_cap_change_percentage_24h_in_currency'][f'{config.currency_vs}'])
        MARKET_CAP_CHANGE_24H = format_currency(api_data['market_cap_change_24h_in_currency'][f'{config.currency_vs}'], config.currency_vs_ticker)
        FULLY_DILUTED_VALUATION = format_currency(api_data['fully_diluted_valuation'][f'{config.currency_vs}'], config.currency_vs_ticker)
        
        ALL_TIME_HIGH_CHANGE_PERCENTAGE = format_percentage(api_data['ath_change_percentage'][f'{config.currency_vs}'])
        ALL_TIME_HIGH = format_currency(api_data['ath'][f'{config.currency_vs}'], config.currency_vs_ticker)
        ALL_TIME_HIGH_DATE = format_utc(api_data['ath_date'][f'{config.currency_vs}'])    
        
        TOTAL_VOLUME = format_currency(api_data['total_volume'][f'{config.currency_vs}'], config.currency_vs_ticker)
        SUPPLY_TOTAL = format_currency(api_data['total_supply'], config.currency_crypto_ticker)
        SUPPLY_CIRCULATING = format_currency(api_data['circulating_supply'], config.currency_crypto_ticker)
    
        # Format values for user presentation:
        info_pair_update = f'{config.currency_pair} at UTC {LAST_UPDATED}:\n'
        info_price = f'Price: {PRICE_CURRENT}\n' \
            f'24h Change: {PRICE_CHANGE_PERCENTAGE_IN_CURRENCY_24H} ({PRICE_CHANGE_24H_IN_CURRENCY})\n' \
            f'24h High: {PRICE_HIGH_24H}\n' \
            f'24h Low: {PRICE_LOW_24H}\n'
        info_market_cap = f'Market Cap: {MARKET_CAP}\n' \
            f'24h Change: {MARKET_CAP_CHANGE_24H_PERCENTAGE} ({MARKET_CAP_CHANGE_24H})\n' \
            f'FDV: {FULLY_DILUTED_VALUATION}\n'
        info_ath = f'ATH: {ALL_TIME_HIGH_CHANGE_PERCENTAGE} ({ALL_TIME_HIGH})\n' \
            f'ATH Date: UTC {ALL_TIME_HIGH_DATE}\n'
        info_supply = f'Total Volume: {TOTAL_VOLUME}\n' \
            f'Total Supply: {SUPPLY_TOTAL}\n' \
            f'Circulating: {SUPPLY_CIRCULATING}'

        with open (latest_values_file, 'w') as latest_values:
            latest_values.write(f"{info_pair_update}\n{info_price}\n{info_market_cap}\n{info_ath}\n{info_supply}")


def write_history_values(days):

    # User configuration related variables:
    history_chart = 'history_chart_days_max'

    history_values_path = config.databases[f'{history_chart}']['path']
    history_values_file = history_values_path + f'history_values_days_{days}.txt'

    history_chart_path = config.databases[f'{history_chart}']['path']
    history_chart_file = history_chart_path + history_chart + '.csv'
    history_chart_data = pd.read_csv(history_chart_file)

    if days == 'max':
        days = len(history_chart_data) - 1

    history_chart_interval = calculate_chart_interval(days)
    history_chart_data_index_last = history_chart_data.index.max()
    history_chart_data_index_first = history_chart_data_index_last - history_chart_interval

    history_date = history_chart_data['Date'][history_chart_data_index_first : history_chart_data_index_last]
    history_price = history_chart_data['Price'][history_chart_data_index_first : history_chart_data_index_last]
    history_market_cap = history_chart_data['Market Cap'][history_chart_data_index_first : history_chart_data_index_last]
    history_total_volume = history_chart_data['Total Volume'][history_chart_data_index_first : history_chart_data_index_last]

    latest_api_data_file = config.databases['latest_api_data']['path'] + config.databases['latest_api_data']['filename']

    with open (latest_api_data_file, 'r') as json_file:
        
        data_current = json.load(json_file)

        if history_chart_interval < 3664:

            CURRENT_DATE = format_utc(data_current['last_updated'])[:-9]
            CURRENT_PRICE = data_current['current_price'][f'{config.currency_vs}']
            CURRENT_MCAP = data_current['market_cap'][f'{config.currency_vs}']
            CURRENT_VOL = data_current['total_volume'][f'{config.currency_vs}']

            HISTORY_DATE = convert_timestamp_to_utc(history_date.iloc[0])[:-9]
            HISTORY_PRICE = history_price.iloc[0]
            HISTORY_MCAP = history_market_cap.iloc[0]
            HISTORY_VOL = history_total_volume.iloc[0]

            CHANGE_PRICE = format_currency(CURRENT_PRICE - HISTORY_PRICE, f'{config.currency_vs}')
            CHANGE_MCAP = format_currency(CURRENT_MCAP - HISTORY_MCAP, f'{config.currency_vs}')
            CHANGE_VOL = format_currency(CURRENT_VOL - HISTORY_VOL, f'{config.currency_vs}')

            PERCENTAGE_CHANGE_PRICE = format_percentage(calculate_percentage_change(HISTORY_PRICE, CURRENT_PRICE))
            PERCENTAGE_CHANGE_MCAP = format_percentage(calculate_percentage_change(HISTORY_MCAP, CURRENT_MCAP))
            PERCENTAGE_CHANGE_VOL = format_percentage(calculate_percentage_change(HISTORY_VOL, CURRENT_VOL))

            HIGH_PRICE = format_currency(history_price.max().max(), f'{config.currency_vs}')
            HIGH_MCAP = format_currency(history_market_cap.max().max(), f'{config.currency_vs}')
            HIGH_VOL = format_currency(history_total_volume.max().max(), f'{config.currency_vs}')

            DATE_HIGH_PRICE = convert_timestamp_to_utc(history_date[history_price.idxmax()])[:-9]
            DATE_HIGH_MCAP = convert_timestamp_to_utc(history_date[history_market_cap.idxmax()])[:-9]
            DATE_HIGH_VOL = convert_timestamp_to_utc(history_date[history_total_volume.idxmax()])[:-9]

            LOW_PRICE = format_currency(history_price.min().min(), f'{config.currency_vs}')
            LOW_MCAP = format_currency(history_market_cap.min().min(), f'{config.currency_vs}')
            LOW_VOL = format_currency(history_total_volume.min().min(), f'{config.currency_vs}')

            DATE_LOW_PRICE = convert_timestamp_to_utc(history_date[history_price.idxmin()])[:-9]
            DATE_LOW_MCAP = convert_timestamp_to_utc(history_date[history_market_cap.idxmin()])[:-9]
            DATE_LOW_VOL = convert_timestamp_to_utc(history_date[history_total_volume.idxmin()])[:-9]

            CURRENT_PRICE = format_currency(CURRENT_PRICE, f'{config.currency_vs}')
            CURRENT_MCAP = format_currency(CURRENT_MCAP, f'{config.currency_vs}')
            CURRENT_VOL = format_currency(CURRENT_VOL, f'{config.currency_vs}')

            HISTORY_PRICE = format_currency(HISTORY_PRICE, f'{config.currency_vs}')
            HISTORY_MCAP = format_currency(HISTORY_MCAP, f'{config.currency_vs}')
            HISTORY_VOL = format_currency(HISTORY_VOL, f'{config.currency_vs}')
            
            info_period = f'{config.currency_pair} from {HISTORY_DATE} to {CURRENT_DATE}:\n'
            info_price = f'Price:\n' \
                f'{HISTORY_PRICE} --> {CURRENT_PRICE}\n' \
                f'Change: {PERCENTAGE_CHANGE_PRICE} ({CHANGE_PRICE})\n' \
                f'High: {HIGH_PRICE} ({DATE_HIGH_PRICE})\n' \
                f'Low: {LOW_PRICE} ({DATE_LOW_PRICE})\n'
            info_market_cap = f'Market Cap:\n' \
                f'{HISTORY_MCAP} --> {CURRENT_MCAP}\n' \
                f'Change: {PERCENTAGE_CHANGE_MCAP} ({CHANGE_MCAP})\n' \
                f'High: {HIGH_MCAP} ({DATE_HIGH_MCAP})\n' \
                f'Low: {LOW_MCAP} ({DATE_LOW_MCAP})\n'
            info_total_volume = f'Total Volume:\n' \
                f'{HISTORY_VOL} --> {CURRENT_VOL}\n' \
                f'Change: {PERCENTAGE_CHANGE_VOL} ({CHANGE_VOL})\n' \
                f'High: {HIGH_VOL} ({DATE_HIGH_VOL})\n' \
                f'Low: {LOW_VOL} ({DATE_LOW_VOL})\n'

            with open (history_values_file, 'w') as latest_values:
                latest_values.write(f'{info_period}\n{info_price}\n{info_market_cap}\n{info_total_volume}')

        else:

            CURRENT_DATE = format_utc(data_current['last_updated'])[:-9]
            CURRENT_PRICE = data_current['current_price'][f'{config.currency_vs}']
            CURRENT_MCAP = data_current['market_cap'][f'{config.currency_vs}']
            CURRENT_VOL = data_current['total_volume'][f'{config.currency_vs}']

            HISTORY_DATE = convert_timestamp_to_utc(history_date.iloc[0])[:-9]
            HISTORY_PRICE = history_price.iloc[0]
            HISTORY_MCAP = history_market_cap.iloc[0]
            HISTORY_VOL = 'Unknown'

            CHANGE_PRICE = format_currency(CURRENT_PRICE - HISTORY_PRICE, f'{config.currency_vs}')
            CHANGE_MCAP = format_currency(CURRENT_MCAP - HISTORY_MCAP, f'{config.currency_vs}')

            PERCENTAGE_CHANGE_PRICE = format_percentage(calculate_percentage_change(HISTORY_PRICE, CURRENT_PRICE))
            PERCENTAGE_CHANGE_MCAP = format_percentage(calculate_percentage_change(HISTORY_MCAP, CURRENT_MCAP))

            HIGH_PRICE = format_currency(history_price.max().max(), f'{config.currency_vs}')
            HIGH_MCAP = format_currency(history_market_cap.max().max(), f'{config.currency_vs}')
            HIGH_VOL = format_currency(history_total_volume.max().max(), f'{config.currency_vs}')

            DATE_HIGH_PRICE = convert_timestamp_to_utc(history_date[history_price.idxmax()])[:-9]
            DATE_HIGH_MCAP = convert_timestamp_to_utc(history_date[history_market_cap.idxmax()])[:-9]
            DATE_HIGH_VOL = convert_timestamp_to_utc(history_date[history_total_volume.idxmax()])[:-9]

            LOW_PRICE = format_currency(history_price.min().min(), f'{config.currency_vs}')
            LOW_MCAP = format_currency(history_market_cap.min().min(), f'{config.currency_vs}')
            LOW_VOL = format_currency(history_total_volume.min().min(), f'{config.currency_vs}')

            DATE_LOW_PRICE = convert_timestamp_to_utc(history_date[history_price.idxmin()])[:-9]
            DATE_LOW_MCAP = convert_timestamp_to_utc(history_date[history_market_cap.idxmin()])[:-9]
            DATE_LOW_VOL = convert_timestamp_to_utc(history_date[history_total_volume.idxmin()])[:-9]

            CURRENT_PRICE = format_currency(CURRENT_PRICE, f'{config.currency_vs}')
            CURRENT_MCAP = format_currency(CURRENT_MCAP, f'{config.currency_vs}')
            CURRENT_VOL = format_currency(CURRENT_VOL, f'{config.currency_vs}')

            HISTORY_PRICE = format_currency(HISTORY_PRICE, f'{config.currency_vs}')
            HISTORY_MCAP = format_currency(HISTORY_MCAP, f'{config.currency_vs}')
            
            info_period = f'{config.currency_pair} from {HISTORY_DATE} to {CURRENT_DATE}:\n'
            info_price = f'Price:\n' \
                f'{HISTORY_PRICE} --> {CURRENT_PRICE}\n' \
                f'Change: {PERCENTAGE_CHANGE_PRICE} ({CHANGE_PRICE})\n' \
                f'High: {HIGH_PRICE} ({DATE_HIGH_PRICE})\n' \
                f'Low: {LOW_PRICE} ({DATE_LOW_PRICE})\n'
            info_market_cap = f'Market Cap:\n' \
                f'{HISTORY_MCAP} --> {CURRENT_MCAP}\n' \
                f'Change: {PERCENTAGE_CHANGE_MCAP} ({CHANGE_MCAP})\n' \
                f'High: {HIGH_MCAP} ({DATE_HIGH_MCAP})\n' \
                f'Low: {LOW_MCAP} ({DATE_LOW_MCAP})\n'
            info_total_volume = f'Total Volume:\n' \
                f'{HISTORY_VOL} --> {CURRENT_VOL}\n' \
                f'Unable to get Total Volume change\n' \
                f'High: {HIGH_VOL} ({DATE_HIGH_VOL})\n' \
                f'Low: unable to get Total Volume low\n'
            info_limitations = 'CoinGecko does not provide information\n' \
                'about Total Volume before 2013-12-27.\n'

            with open (history_values_file, 'w') as latest_values:
                latest_values.write(f'{info_period}\n{info_price}\n{info_market_cap}\n{info_total_volume}\n{info_limitations}')




if __name__ == '__main__':
    
    write_latest_values()

    days = [1,2,6,7,365,366,1825,1826,3663,3664,3665,'max']
    for day in days:
        write_history_values(day)