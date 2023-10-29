import pandas as pd
from data_tools import get_data
from data_config import cryptocurrency, history_file
from api.coingecko import BASE

list_prices_data = get_data(BASE, f'coins/{cryptocurrency}/market_chart')['prices']  # list
list_market_caps_data = get_data(BASE, f'coins/{cryptocurrency}/market_chart')['market_caps']  # list

prices_data = pd.DataFrame(list_prices_data, columns=['Date', 'Price'])
market_cap_data = pd.DataFrame(list_market_caps_data, columns=['Date', 'Market Cap'])
history_data = prices_data.merge(market_cap_data, on='Date', how='left')
history_data.to_csv(history_file, index=False)