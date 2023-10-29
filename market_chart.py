import pandas as pd
import matplotlib.pyplot as plt
from data_tools import format_currency, convert_timestamp_to_utc, select_chart_background
from data_config import ticker, database_file, chart_path, chart_font
from api.coingecko import BASE
from matplotlib.ticker import FuncFormatter
from matplotlib import font_manager
from PIL import Image

df = pd.read_csv(database_file) # Load data from the CSV file
df['Date'] = df['Date'].apply(convert_timestamp_to_utc) # Convert the 'Date' column to UTC

fig, ax1 = plt.subplots(figsize=(10, 6)) # Create a figure and axes
fig.patch.set_alpha(0.0) # Set the background color inside the plot area to be transparent
ax2 = ax1.twinx() # Create a second y-axis on the right side

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
prop = font_manager.FontProperties(fname=chart_font) # Use the specified font path

ax1.set_title('Graph Title', fontproperties=prop)
ax1.set_xlabel('Date', fontproperties=prop)
ax1.set_ylabel('Price', color='orange', fontproperties=prop)
ax2.set_ylabel('Market Cap', color='green', fontproperties=prop)

# Set font properties for tick labels on both axes
for label in ax1.get_xticklabels() + ax1.get_yticklabels() + ax2.get_yticklabels():
    label.set_fontproperties(prop)

ax1.grid(True, linestyle='--', linewidth=0.5, alpha=0.7) # Add gridlines to the plot
fig.patch.set_facecolor('none') # Set transparent background outside the plot area
dpi_value = 150 # Set DPI for plot image
plt.savefig(chart_path, bbox_inches='tight', transparent=True, dpi=dpi_value) # Save the plot to a PNG file with a transparent background

background = Image.open(history_chart_background) # Open background image
overlay = Image.open(chart_path) # Open plot image
x = 750  # X-coordinate for plot image
y = 85  # Y-coordinate for plot image
background.paste(overlay, (x, y), overlay) # Paste plot image over background image
background.save("output.png") # Save the plot with background image