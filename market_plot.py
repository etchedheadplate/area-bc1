import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib import font_manager
from PIL import Image
from data_tools import format_money_axis, format_time_axis, select_plot_background, get_data, set_24h_time_period, set_custom_time_period, calculate_price_change_percentage
from data_config import cryptocurrency, ticker, database_file, plot_path, plot_font
from api.coingecko import BASE

def make_market_plot():
    dates = set_24h_time_period()
    date_start, date_end, date_period = dates[0], dates[1], dates[2]
    endpoint = f'coins/{cryptocurrency}/market_chart/range'

    list_prices_data = get_data(BASE, endpoint, start=f'{date_start}',to=f'{date_end}')['prices']  # list
    list_market_caps_data = get_data(BASE, endpoint, start=f'{date_start}',to=f'{date_end}')['market_caps']  # list
    list_market_total_volumes = get_data(BASE, endpoint, start=f'{date_start}',to=f'{date_end}')['total_volumes']  # list

    price_start, price_end = list_prices_data[0][1], list_prices_data[-1][1]
    price_change_percentage = calculate_price_change_percentage(price_start, price_end)

    background_params = select_plot_background(price_change_percentage)
    bkg_filename, bkg_DPI, bkg_x, bkg_y = background_params[0], background_params[2], background_params[3], background_params[4]

    prices_data = pd.DataFrame(list_prices_data, columns=['Date', 'Price'])
    market_cap_data = pd.DataFrame(list_market_caps_data, columns=['Date', 'Market Cap'])
    total_volumes_data = pd.DataFrame(list_market_total_volumes, columns=['Date', 'Total Volumes'])
    history_data = prices_data.merge(market_cap_data, on='Date', how='left').merge(total_volumes_data, on='Date', how='left')
    history_data.to_csv(database_file, index=False)
    df = pd.read_csv(database_file)
    df['Supply Circulating'] = df['Market Cap'] / df['Price']
    df.to_csv(database_file, index=False)

    df = pd.read_csv(database_file) # Load data from the CSV file

    # Set the font properties for the text elements on the plot
    custom_font = font_manager.FontProperties(fname=plot_font) # Use the specified font path

    axis_date = df['Date']
    axis_price = df['Price']
    axis_volume = df['Total Volumes']

    fig, ax1 = plt.subplots(figsize=(12, 6)) # Create a figure and axes
    fig.patch.set_alpha(0.0) # Set the background color inside the plot area to be transparent
    ax2 = ax1.twinx() # Create a second y-axis on the right side

    # Left y axis
    line1, = ax1.plot( # line 1 creation
        axis_date, # axis data from start row to end row
        axis_price, # axis data from start row to end row
        color='orange', # line color
        label='Price', # line label
        linewidth=1, # line width
        zorder=1 # layer order (higher value puts layer to the front)
        )
    ax1.xaxis.set_major_formatter(FuncFormatter(lambda x, _: format_time_axis(x, date_period))) # x text format
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, _: format_money_axis(x))) # y text format
    ax1.tick_params(axis='x', labelcolor='white') # x text color
    ax1.tick_params(axis='y', labelcolor='orange') # y text color
    ax1.set_zorder(2) # layer order (higher value puts layer to the front)

    plt.setp(
        ax1.get_xticklabels(),
        rotation=20, # rotates text on x axis
        ha='center')  # alignes to right text on x axis

    # Right y axis
    line2, = ax2.plot( # line 1 creation
        axis_date, # axis data from start row to end row
        axis_volume, # axis data from start row to end row
        color='green', # line color
        label='Total Volumes', # line label
        alpha=0.2, # line transparency
        linewidth=0.1, # line width
        )
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, _: format_money_axis(x))) # y text format
    ax2.tick_params(axis='y', labelcolor='green') # y text color
    ax2.set_zorder(1) # layer order (higher value puts layer to the front)
    ax2.fill_between( # color filling of shape below the line
        axis_date,
        axis_volume,
        color='green', # filling color
        alpha=0.15, # filling transparency
    )

    # Legend
    legend = ax1.legend(
        [line1, line2], # lines in legend
        [f'Price, {ticker}', f'Volume, {ticker}'], # titles of lines
        loc='upper left', # legend location
        prop=custom_font, # legend font
        handlelength=0
        )
    legend.get_texts()[0].set_color('orange')
    legend.get_texts()[1].set_color('green')
    legend.get_frame().set_facecolor('black')  # Set the background color
    legend.get_frame().set_alpha(0.7) 


    # Set font properties for tick labels on both axes
    for label in ax1.get_xticklabels() + ax1.get_yticklabels() + ax2.get_yticklabels():
        label.set_fontproperties(custom_font)

    ax1.grid(True, linestyle='--', linewidth=0.5, alpha=0.7) # Add gridlines to the plot
    fig.patch.set_facecolor('none') # Set transparent background outside the plot area
    dpi_value = bkg_DPI # Set DPI for plot image

    plt.savefig(plot_path, bbox_inches='tight', transparent=True, dpi=dpi_value) # Save the plot to a PNG file with a transparent background

    background = Image.open(bkg_filename) # Open background image
    overlay = Image.open(plot_path) # Open plot image
    x = bkg_x  # X-coordinate for plot image
    y = bkg_y  # Y-coordinate for plot image
    background.paste(overlay, (x, y), overlay) # Paste plot image over background image
    background.save("output.png") # Save the plot with background image

    print(price_change_percentage)
    print(bkg_filename, bkg_DPI, bkg_x, bkg_y)

make_market_plot()