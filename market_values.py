from data_tools import get_data, format_currency, format_percentage, format_things
from data_config import cryptocurrency, vs_currency, ticker
from api.coingecko import BASE

coins_market_data = get_data(BASE, f'coins/{cryptocurrency}')['market_data']

TOTAL_VOLUME = format_currency(coins_market_data['total_volume'][f'{vs_currency}'], ticker)
FULLY_DILUTED_VALUATION = format_currency(coins_market_data['fully_diluted_valuation'][f'{vs_currency}'], ticker)

PRICE_CURRENT = format_currency(coins_market_data['current_price'][f'{vs_currency}'], ticker)
PRICE_CHANGE_24H = format_currency(coins_market_data['price_change_24h'], ticker)
PRICE_CHANGE_24H_IN_CURRENCY = format_currency(coins_market_data['price_change_24h_in_currency'][f'{vs_currency}'], ticker)
PRICE_HIGH_24H = format_currency(coins_market_data['high_24h'][f'{vs_currency}'], ticker)
PRICE_LOW_24H = format_currency(coins_market_data['low_24h'][f'{vs_currency}'], ticker)

PRICE_CHANGE_PERCENTAGE_IN_CURRENCY_1H = format_percentage(coins_market_data['price_change_percentage_1h_in_currency'][f'{vs_currency}'])
PRICE_CHANGE_PERCENTAGE_IN_CURRENCY_24H = format_percentage(coins_market_data['price_change_percentage_24h_in_currency'][f'{vs_currency}'])
PRICE_CHANGE_PERCENTAGE_IN_CURRENCY_7D = format_percentage(coins_market_data['price_change_percentage_7d_in_currency'][f'{vs_currency}'])
PRICE_CHANGE_PERCENTAGE_IN_CURRENCY_14D = format_percentage(coins_market_data['price_change_percentage_14d_in_currency'][f'{vs_currency}'])
PRICE_CHANGE_PERCENTAGE_IN_CURRENCY_30D = format_percentage(coins_market_data['price_change_percentage_30d_in_currency'][f'{vs_currency}'])
PRICE_CHANGE_PERCENTAGE_IN_CURRENCY_60D = format_percentage(coins_market_data['price_change_percentage_60d_in_currency'][f'{vs_currency}'])
PRICE_CHANGE_PERCENTAGE_IN_CURRENCY_200D = format_percentage(coins_market_data['price_change_percentage_200d_in_currency'][f'{vs_currency}'])
PRICE_CHANGE_PERCENTAGE_IN_CURRENCY_1Y = format_percentage(coins_market_data['price_change_percentage_1y_in_currency'][f'{vs_currency}'])

PRICE_CHANGE_PERCENTAGE_24H = format_percentage(coins_market_data['price_change_percentage_24h']) # %
PRICE_CHANGE_PERCENTAGE_7D = format_percentage(coins_market_data['price_change_percentage_7d']) # %
PRICE_CHANGE_PERCENTAGE_14D = format_percentage(coins_market_data['price_change_percentage_14d']) # %
PRICE_CHANGE_PERCENTAGE_30D = format_percentage(coins_market_data['price_change_percentage_30d']) # %
PRICE_CHANGE_PERCENTAGE_60D = format_percentage(coins_market_data['price_change_percentage_60d']) # %
PRICE_CHANGE_PERCENTAGE_200D = format_percentage(coins_market_data['price_change_percentage_200d']) # %
PRICE_CHANGE_PERCENTAGE_1Y = format_percentage(coins_market_data['price_change_percentage_1y']) # %

MARKET_CAP = format_currency(coins_market_data['market_cap'][f'{vs_currency}'], ticker)
MARKET_CAP_CHANGE_24H = format_currency(coins_market_data['market_cap_change_24h_in_currency'][f'{vs_currency}'], ticker)
MARKET_CAP_CHANGE_24H_PERCENTAGE = format_percentage(coins_market_data['market_cap_change_percentage_24h_in_currency'][f'{vs_currency}']) # %

SUPPLY_CIRCULATING = format_things(coins_market_data['circulating_supply']) # pics
SUPPLY_TOTAL = format_things(coins_market_data['total_supply']) # pics

ALL_TIME_HIGH = format_currency(coins_market_data['ath'][f'{vs_currency}'], ticker)
ALL_TIME_HIGH_CHANGE_PERCENTAGE = format_percentage(coins_market_data['ath_change_percentage'][f'{vs_currency}']) # %
ALL_TIME_HIGH_DATE = (coins_market_data['ath_date'][f'{vs_currency}'])


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
