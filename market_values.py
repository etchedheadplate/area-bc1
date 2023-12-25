from data_tools import get_data, format_currency, format_percentage, format_things
from data_config import cryptocurrency, vs_currency, ticker
from api.coingecko import BASE

values = {
    'Price     ': None,
    'Market Cap': None,
    'Volume    ': None,
    'Δ24h Price': None,
    'Δ24h Cap  ': None,
    'Timestamp ': None
    }

def update_values(api_response):
    global values
    
    TOTAL_VOLUME = format_currency(api_response['total_volume'][f'{vs_currency}'], ticker)
    FULLY_DILUTED_VALUATION = format_currency(api_response['fully_diluted_valuation'][f'{vs_currency}'], ticker)

    PRICE_CURRENT = format_currency(api_response['current_price'][f'{vs_currency}'], ticker)
    PRICE_CHANGE_24H = format_currency(api_response['price_change_24h'], ticker)
    PRICE_CHANGE_24H_IN_CURRENCY = format_currency(api_response['price_change_24h_in_currency'][f'{vs_currency}'], ticker)
    PRICE_HIGH_24H = format_currency(api_response['high_24h'][f'{vs_currency}'], ticker)
    PRICE_LOW_24H = format_currency(api_response['low_24h'][f'{vs_currency}'], ticker)

    PRICE_CHANGE_PERCENTAGE_IN_CURRENCY_1H = format_percentage(api_response['price_change_percentage_1h_in_currency'][f'{vs_currency}'])
    PRICE_CHANGE_PERCENTAGE_IN_CURRENCY_24H = format_percentage(api_response['price_change_percentage_24h_in_currency'][f'{vs_currency}'])
    PRICE_CHANGE_PERCENTAGE_IN_CURRENCY_7D = format_percentage(api_response['price_change_percentage_7d_in_currency'][f'{vs_currency}'])
    PRICE_CHANGE_PERCENTAGE_IN_CURRENCY_14D = format_percentage(api_response['price_change_percentage_14d_in_currency'][f'{vs_currency}'])
    PRICE_CHANGE_PERCENTAGE_IN_CURRENCY_30D = format_percentage(api_response['price_change_percentage_30d_in_currency'][f'{vs_currency}'])
    PRICE_CHANGE_PERCENTAGE_IN_CURRENCY_60D = format_percentage(api_response['price_change_percentage_60d_in_currency'][f'{vs_currency}'])
    PRICE_CHANGE_PERCENTAGE_IN_CURRENCY_200D = format_percentage(api_response['price_change_percentage_200d_in_currency'][f'{vs_currency}'])
    PRICE_CHANGE_PERCENTAGE_IN_CURRENCY_1Y = format_percentage(api_response['price_change_percentage_1y_in_currency'][f'{vs_currency}'])

    PRICE_CHANGE_PERCENTAGE_24H = format_percentage(api_response['price_change_percentage_24h']) # %
    PRICE_CHANGE_PERCENTAGE_7D = format_percentage(api_response['price_change_percentage_7d']) # %
    PRICE_CHANGE_PERCENTAGE_14D = format_percentage(api_response['price_change_percentage_14d']) # %
    PRICE_CHANGE_PERCENTAGE_30D = format_percentage(api_response['price_change_percentage_30d']) # %
    PRICE_CHANGE_PERCENTAGE_60D = format_percentage(api_response['price_change_percentage_60d']) # %
    PRICE_CHANGE_PERCENTAGE_200D = format_percentage(api_response['price_change_percentage_200d']) # %
    PRICE_CHANGE_PERCENTAGE_1Y = format_percentage(api_response['price_change_percentage_1y']) # %

    MARKET_CAP = format_currency(api_response['market_cap'][f'{vs_currency}'], ticker)
    MARKET_CAP_CHANGE_24H = format_currency(api_response['market_cap_change_24h_in_currency'][f'{vs_currency}'], ticker)
    MARKET_CAP_CHANGE_24H_PERCENTAGE = format_percentage(api_response['market_cap_change_percentage_24h_in_currency'][f'{vs_currency}']) # %

    SUPPLY_CIRCULATING = format_things(api_response['circulating_supply']) # pics
    SUPPLY_TOTAL = format_things(api_response['total_supply']) # pics

    ALL_TIME_HIGH = format_currency(api_response['ath'][f'{vs_currency}'], ticker)
    ALL_TIME_HIGH_CHANGE_PERCENTAGE = format_percentage(api_response['ath_change_percentage'][f'{vs_currency}']) # %
    ALL_TIME_HIGH_DATE = (api_response['ath_date'][f'{vs_currency}'])

    LAST_UPDATED = api_response['last_updated']

    values['Price     '] = PRICE_CURRENT
    values['Market Cap'] = MARKET_CAP
    values['Volume    '] = TOTAL_VOLUME,
    values['Δ24h Price'] = f'{PRICE_CHANGE_PERCENTAGE_24H} ({PRICE_CHANGE_24H})'
    values['Δ24h Cap  '] = f'{MARKET_CAP_CHANGE_24H_PERCENTAGE} ({MARKET_CAP_CHANGE_24H})'
    values['Timestamp '] = LAST_UPDATED
    
 

'''
market_values_full = {
    'TOTAL_VOLUME ****************************** ':TOTAL_VOLUME,
    'FULLY_DILUTED_VALUATION ******************* ':FULLY_DILUTED_VALUATION,
    'PRICE_CURRENT ***************************** ':PRICE_CURRENT,
    'PRICE_CHANGE_24H ************************** ':PRICE_CHANGE_24H,
    'PRICE_CHANGE_24H_IN_CURRENCY ************** ':PRICE_CHANGE_24H_IN_CURRENCY,
    'PRICE_HIGH_24H **************************** ':PRICE_HIGH_24H,
    'PRICE_LOW_24H ***************************** ':PRICE_LOW_24H,

    'PRICE_CHANGE_PERCENTAGE_IN_CURRENCY_24H *** ':PRICE_CHANGE_PERCENTAGE_IN_CURRENCY_24H,
    'PRICE_CHANGE_PERCENTAGE_IN_CURRENCY_7D **** ':PRICE_CHANGE_PERCENTAGE_IN_CURRENCY_7D,
    'PRICE_CHANGE_PERCENTAGE_IN_CURRENCY_14D *** ':PRICE_CHANGE_PERCENTAGE_IN_CURRENCY_14D,
    'PRICE_CHANGE_PERCENTAGE_IN_CURRENCY_30D *** ':PRICE_CHANGE_PERCENTAGE_IN_CURRENCY_30D,
    'PRICE_CHANGE_PERCENTAGE_IN_CURRENCY_60D *** ':PRICE_CHANGE_PERCENTAGE_IN_CURRENCY_60D,
    'PRICE_CHANGE_PERCENTAGE_IN_CURRENCY_200D ** ':PRICE_CHANGE_PERCENTAGE_IN_CURRENCY_200D,
    'PRICE_CHANGE_PERCENTAGE_IN_CURRENCY_1Y **** ':PRICE_CHANGE_PERCENTAGE_IN_CURRENCY_1Y,

    'PRICE_CHANGE_PERCENTAGE_24H *************** ':PRICE_CHANGE_PERCENTAGE_24H,
    'PRICE_CHANGE_PERCENTAGE_7D **************** ':PRICE_CHANGE_PERCENTAGE_7D,
    'PRICE_CHANGE_PERCENTAGE_14D *************** ':PRICE_CHANGE_PERCENTAGE_14D,
    'PRICE_CHANGE_PERCENTAGE_30D *************** ':PRICE_CHANGE_PERCENTAGE_30D,
    'PRICE_CHANGE_PERCENTAGE_60D *************** ':PRICE_CHANGE_PERCENTAGE_60D,
    'PRICE_CHANGE_PERCENTAGE_200D ************** ':PRICE_CHANGE_PERCENTAGE_200D,
    'PRICE_CHANGE_PERCENTAGE_1Y **************** ':PRICE_CHANGE_PERCENTAGE_1Y,

    'MARKET_CAP ******************************** ':MARKET_CAP,
    'MARKET_CAP_CHANGE_24H ********************* ':MARKET_CAP_CHANGE_24H,
    'MARKET_CAP_CHANGE_24H_PERCENTAGE ********** ':MARKET_CAP_CHANGE_24H_PERCENTAGE,

    'SUPPLY_CIRCULATING ************************ ':SUPPLY_CIRCULATING,
    'SUPPLY_TOTAL ****************************** ':SUPPLY_TOTAL,

    'ALL_TIME_HIGH ***************************** ':ALL_TIME_HIGH,
    'ALL_TIME_HIGH_CHANGE_PERCENTAGE *********** ':ALL_TIME_HIGH_CHANGE_PERCENTAGE,
    'ALL_TIME_HIGH_DATE ************************ ':ALL_TIME_HIGH_DATE,
}
'''
