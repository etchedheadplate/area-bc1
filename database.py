import pandas as pd
from data_tools import get_data, format_things
from data_config import cryptocurrency, database_file
from api.coingecko import BASE

list_prices_data = get_data(BASE, f'coins/{cryptocurrency}/market_chart')['prices']  # list
list_market_caps_data = get_data(BASE, f'coins/{cryptocurrency}/market_chart')['market_caps']  # list
list_market_total_volumes = get_data(BASE, f'coins/{cryptocurrency}/market_chart')['total_volumes']  # list

prices_data = pd.DataFrame(list_prices_data, columns=['Date', 'Price'])
market_cap_data = pd.DataFrame(list_market_caps_data, columns=['Date', 'Market Cap'])
total_volumes_data = pd.DataFrame(list_market_total_volumes, columns=['Date', 'Total Volumes'])
history_data = prices_data.merge(market_cap_data, on='Date', how='left').merge(total_volumes_data, on='Date', how='left')
history_data.to_csv(database_file, index=False)
df = pd.read_csv(database_file)
df['Supply Circulating'] = df['Market Cap'] / df['Price']
df.to_csv(database_file, index=False)