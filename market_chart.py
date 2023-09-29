from data_tools import get_data, format_currency, convert_timestamp_to_utc
from data_config import cryptocurrency, ticker, history_file, history_graph, history_graph_font
from api.coingecko import BASE
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib import font_manager

list_prices_data = get_data(BASE, f'coins/{cryptocurrency}/market_chart')['prices']  # list
list_market_caps_data = get_data(BASE, f'coins/{cryptocurrency}/market_chart')['market_caps']  # list

prices_data = pd.DataFrame(list_prices_data, columns=['Date', 'Price'])
market_cap_data = pd.DataFrame(list_market_caps_data, columns=['Date', 'Market Cap'])
history_data = prices_data.merge(market_cap_data, on='Date', how='left')
history_data.to_csv(history_file, index=False)

# Load data from the CSV file
df = pd.read_csv(history_file)

# Convert the 'Date' column to UTC (Assuming you have implemented the conversion function)
df['Date'] = df['Date'].apply(convert_timestamp_to_utc)

# Create a figure and axes
fig, ax1 = plt.subplots(figsize=(10, 6))

# Set the background color inside the plot area to be transparent
fig.patch.set_alpha(0.0)

# Create a second y-axis on the right side
ax2 = ax1.twinx()

# Plot Price on the left axis in orange
line1, = ax1.plot(df['Date'], df['Price'], color='orange', label='Price')
ax1.set_xlabel('Date')
ax1.set_ylabel('Price', color='orange')
ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, _: format_currency(x, ticker)))
ax1.tick_params(axis='y', labelcolor='orange')

# Plot Market Cap on the right axis in green
line2, = ax2.plot(df['Date'], df['Market Cap'], color='green', label='Market Cap')
ax2.set_ylabel('Market Cap', color='green')
ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, _: format_currency(x, ticker)))
ax2.tick_params(axis='y', labelcolor='green')

# Combine legends for both axes with South Park font
ax1.legend([line1, line2], ['Price', 'Market Cap'], loc='upper left', prop={'family': 'South Park', 'size': 12})

# Set the font properties for the text elements on the plot
font_path = history_graph_font  # Use the specified font path
prop = font_manager.FontProperties(fname=font_path)

ax1.set_title('Graph Title', fontproperties=prop)
ax1.set_xlabel('Date', fontproperties=prop)
ax1.set_ylabel('Price', color='orange', fontproperties=prop)
ax2.set_ylabel('Market Cap', color='green', fontproperties=prop)

# Set font properties for tick labels on both axes
for label in ax1.get_xticklabels() + ax1.get_yticklabels() + ax2.get_yticklabels():
    label.set_fontproperties(prop)

# Add gridlines to the plot
ax1.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)

# Set transparent background outside the plot area
fig.patch.set_facecolor('none')

# Save the plot to a PNG file with a transparent background
plt.savefig(history_graph, bbox_inches='tight', transparent=True)

# Show the plot
plt.show()