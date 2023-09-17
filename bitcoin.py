from data_fetcher import get_data
from api.coingecko import BASE
from money import Money
import datetime

btc_dict = get_data(BASE, '/simple/price')
print(btc_dict)

def format_currency(amount, currency_symbol='$'):
    money = Money(amount, 'EUR')  # Указываем валюту (здесь 'USD' как пример)
    formatted_amount = f"{money.amount:,.2f}{currency_symbol}"  # Добавляем символ валюты вручную
    return formatted_amount

def unix_timestamp_to_datetime(unix_timestamp):
    # Преобразовываем UNIX время в объект datetime
    dt = datetime.datetime.fromtimestamp(unix_timestamp)
    return dt

BTC_USD_PRICE = format_currency(btc_dict['bitcoin']['usd'])
MARKET_CAP = format_currency(btc_dict['bitcoin']['usd_market_cap'])
USD_24H_VOL = format_currency(btc_dict['bitcoin']['usd_24h_vol'])
USD_24H_CHANGE = format_currency(btc_dict['bitcoin']['usd_24h_change'])
LAST_UPDATED_AT = unix_timestamp_to_datetime(btc_dict['bitcoin']['last_updated_at'])

print(BTC_USD_PRICE, MARKET_CAP, USD_24H_VOL, USD_24H_CHANGE, LAST_UPDATED_AT, sep='\n')