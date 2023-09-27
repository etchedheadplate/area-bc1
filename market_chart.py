from data_tools import get_data, check_file_length
from data_config import cryptocurrency, vs_currency, ticker, history_file, history_graph, history_graph_background
from api.coingecko import BASE
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

list_prices_data = get_data(BASE, f'coins/{cryptocurrency}/market_chart')['prices']  # list
list_market_caps_data = get_data(BASE, f'coins/{cryptocurrency}/market_chart')['market_caps']  # list

prices_data = pd.DataFrame(list_prices_data, columns=['Date', 'Price'])
market_cap_data = pd.DataFrame(list_market_caps_data, columns=['Date', 'Market Cap'])
history_data = prices_data.merge(market_cap_data, on='Date', how='left')
history_data.to_csv(history_file, index=False)
