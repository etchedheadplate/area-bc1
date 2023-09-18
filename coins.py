from data_fetcher import get_data
from api.coingecko import BASE
from currency_symbols import CurrencySymbols
import datetime

cryptocurrency = 'bitcoin'
vs_currency = 'rub'
ticker = vs_currency.upper()

def format_currency(amount, symbol=ticker):
    # Converts endpoint values to vs_currency format
    currency_symbols = CurrencySymbols()
    currency_symbol = currency_symbols.get_symbol(ticker)
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
    return '{:,.0f}'.format(number).replace(',', ' ')

def unix_timestamp_to_datetime(unix_timestamp):
    # Converts UNIX time to a datetime object
    converted_dt = datetime.datetime.fromtimestamp(unix_timestamp)
    return converted_dt

market_data = get_data(BASE, f'coins/{cryptocurrency}')['market_data']

TOTAL_VOLUME = format_currency(market_data['total_volume'][f'{vs_currency}'])
FULLY_DILUTED_VALUATION = format_currency(market_data['fully_diluted_valuation'][f'{vs_currency}'])

PRICE_CURRENT = format_currency(market_data['current_price'][f'{vs_currency}'])
PRICE_CHANGE_24H = format_currency(market_data['price_change_24h'])
PRICE_CHANGE_24H_IN_CURRENCY = format_currency(market_data['price_change_24h_in_currency'][f'{vs_currency}'])
PRICE_HIGH_24H = format_currency(market_data['high_24h'][f'{vs_currency}'])
PRICE_LOW_24H = format_currency(market_data['low_24h'][f'{vs_currency}'])

PRICE_CHANGE_PERCENTAGE_IN_CURRENCY_1H = format_percentage(market_data['price_change_percentage_1h_in_currency'][f'{vs_currency}'])
PRICE_CHANGE_PERCENTAGE_IN_CURRENCY_24H = format_percentage(market_data['price_change_percentage_24h_in_currency'][f'{vs_currency}'])
PRICE_CHANGE_PERCENTAGE_IN_CURRENCY_7D = format_percentage(market_data['price_change_percentage_7d_in_currency'][f'{vs_currency}'])
PRICE_CHANGE_PERCENTAGE_IN_CURRENCY_14D = format_percentage(market_data['price_change_percentage_14d_in_currency'][f'{vs_currency}'])
PRICE_CHANGE_PERCENTAGE_IN_CURRENCY_30D = format_percentage(market_data['price_change_percentage_30d_in_currency'][f'{vs_currency}'])
PRICE_CHANGE_PERCENTAGE_IN_CURRENCY_60D = format_percentage(market_data['price_change_percentage_60d_in_currency'][f'{vs_currency}'])
PRICE_CHANGE_PERCENTAGE_IN_CURRENCY_200D = format_percentage(market_data['price_change_percentage_200d_in_currency'][f'{vs_currency}'])
PRICE_CHANGE_PERCENTAGE_IN_CURRENCY_1Y = format_percentage(market_data['price_change_percentage_1y_in_currency'][f'{vs_currency}'])

PRICE_CHANGE_PERCENTAGE_24H = format_percentage(market_data['price_change_percentage_24h']) # %
PRICE_CHANGE_PERCENTAGE_7D = format_percentage(market_data['price_change_percentage_7d']) # %
PRICE_CHANGE_PERCENTAGE_14D = format_percentage(market_data['price_change_percentage_14d']) # %
PRICE_CHANGE_PERCENTAGE_30D = format_percentage(market_data['price_change_percentage_30d']) # %
PRICE_CHANGE_PERCENTAGE_60D = format_percentage(market_data['price_change_percentage_60d']) # %
PRICE_CHANGE_PERCENTAGE_200D = format_percentage(market_data['price_change_percentage_200d']) # %
PRICE_CHANGE_PERCENTAGE_1Y = format_percentage(market_data['price_change_percentage_1y']) # %

MARKET_CAP = format_currency(market_data['market_cap'][f'{vs_currency}'])
MARKET_CAP_CHANGE_24H = format_currency(market_data['market_cap_change_24h_in_currency'][f'{vs_currency}'])
MARKET_CAP_CHANGE_24H_PERCENTAGE = format_percentage(market_data['market_cap_change_percentage_24h_in_currency'][f'{vs_currency}']) # %

SUPPLY_CIRCULATING = format_things(market_data['circulating_supply']) # pics
SUPPLY_TOTAL = format_things(market_data['total_supply']) # pics

ALL_TIME_HIGH = format_currency(market_data['ath'][f'{vs_currency}'])
ALL_TIME_HIGH_CHANGE_PERCENTAGE = format_percentage(market_data['ath_change_percentage'][f'{vs_currency}']) # %
ALL_TIME_HIGH_DATE = (market_data['ath_date'][f'{vs_currency}'])


if __name__ == '__main__':
    print(
        'TOTAL_VOLUME ****************************** ', TOTAL_VOLUME, '\n',
        'FULLY_DILUTED_VALUATION ******************* ', FULLY_DILUTED_VALUATION, '\n',
        '\n',
        'PRICE_CURRENT ***************************** ', PRICE_CURRENT, '\n',
        'PRICE_CHANGE_24H ************************** ', PRICE_CHANGE_24H, '\n',
        'PRICE_CHANGE_24H_IN_CURRENCY ************** ', PRICE_CHANGE_24H_IN_CURRENCY, '\n',
        'PRICE_HIGH_24H **************************** ', PRICE_HIGH_24H, '\n',
        'PRICE_LOW_24H ***************************** ', PRICE_LOW_24H, '\n',
        '\n',
        'PRICE_CHANGE_PERCENTAGE_IN_CURRENCY_24H *** ', PRICE_CHANGE_PERCENTAGE_IN_CURRENCY_24H, '\n',
        'PRICE_CHANGE_PERCENTAGE_IN_CURRENCY_7D **** ', PRICE_CHANGE_PERCENTAGE_IN_CURRENCY_7D, '\n',
        'PRICE_CHANGE_PERCENTAGE_IN_CURRENCY_14D *** ', PRICE_CHANGE_PERCENTAGE_IN_CURRENCY_14D, '\n',
        'PRICE_CHANGE_PERCENTAGE_IN_CURRENCY_30D *** ', PRICE_CHANGE_PERCENTAGE_IN_CURRENCY_30D, '\n',
        'PRICE_CHANGE_PERCENTAGE_IN_CURRENCY_60D *** ', PRICE_CHANGE_PERCENTAGE_IN_CURRENCY_60D, '\n',
        'PRICE_CHANGE_PERCENTAGE_IN_CURRENCY_200D ** ', PRICE_CHANGE_PERCENTAGE_IN_CURRENCY_200D, '\n',
        'PRICE_CHANGE_PERCENTAGE_IN_CURRENCY_1Y **** ', PRICE_CHANGE_PERCENTAGE_IN_CURRENCY_1Y, '\n',
        '\n',
        'PRICE_CHANGE_PERCENTAGE_24H *************** ', PRICE_CHANGE_PERCENTAGE_24H, '\n',
        'PRICE_CHANGE_PERCENTAGE_7D **************** ', PRICE_CHANGE_PERCENTAGE_7D, '\n',
        'PRICE_CHANGE_PERCENTAGE_14D *************** ', PRICE_CHANGE_PERCENTAGE_14D, '\n',
        'PRICE_CHANGE_PERCENTAGE_30D *************** ', PRICE_CHANGE_PERCENTAGE_30D, '\n',
        'PRICE_CHANGE_PERCENTAGE_60D *************** ', PRICE_CHANGE_PERCENTAGE_60D, '\n',
        'PRICE_CHANGE_PERCENTAGE_200D ************** ', PRICE_CHANGE_PERCENTAGE_200D, '\n',
        'PRICE_CHANGE_PERCENTAGE_1Y **************** ', PRICE_CHANGE_PERCENTAGE_1Y, '\n',
        '\n',
        'MARKET_CAP ******************************** ', MARKET_CAP, '\n',
        'MARKET_CAP_CHANGE_24H ********************* ', MARKET_CAP_CHANGE_24H, '\n',
        'MARKET_CAP_CHANGE_24H_PERCENTAGE ********** ', MARKET_CAP_CHANGE_24H_PERCENTAGE, '\n',
        '\n',
        'SUPPLY_CIRCULATING ************************ ', SUPPLY_CIRCULATING, '\n',
        'SUPPLY_TOTAL ****************************** ', SUPPLY_TOTAL, '\n',
        '\n',
        'ALL_TIME_HIGH ***************************** ', ALL_TIME_HIGH, '\n',
        'ALL_TIME_HIGH_CHANGE_PERCENTAGE *********** ', ALL_TIME_HIGH_CHANGE_PERCENTAGE, '\n',
        'ALL_TIME_HIGH_DATE ************************ ', ALL_TIME_HIGH_DATE,
        sep=''
    )
