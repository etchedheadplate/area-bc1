import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from matplotlib.lines import Line2D
from matplotlib import font_manager
from matplotlib.ticker import FuncFormatter
from PIL import Image

import config
from tools import (select_data_chart,
                   calculate_chart_interval,
                   calculate_percentage_change,
                   format_time_axis,
                   format_money_axis,
                   define_market_movement,
                   format_percentage,
                   select_plot_background)


def make_chart_plot(days_period):
    
    # User configuration related variables: 
    chart_file = select_data_chart(days_period)

    # Creation of plot data frame and plot-related variables:
    plot_file = config.plot['path']
    plot_font = font_manager.FontProperties(fname=config.plot['font'])
    plot_colors = config.plot['colors']
    plot_background = config.plot['backgrounds']
    plot_output = config.plot['output']

    plot_df = pd.read_csv(chart_file)

    if days_period == 'max':
        days_period = len(plot_df) - 1

    # Specification of chart data indexes for plot axes:
    chart_interval = calculate_chart_interval(days_period)
    plot_index_interval = len(plot_df) - chart_interval
    plot_index_start = plot_df['Date'].index[plot_index_interval]
    plot_index_end = plot_df['Date'].idxmax()

    # Market data related variables for percentage change calculation:
    plot_price_start = plot_df['Price'][plot_index_interval]
    plot_price_end = plot_df['Price'].max()
    plot_market_movement = calculate_percentage_change(plot_price_start, plot_price_end)
    plot_market_movement_format = format_percentage(plot_market_movement)
    plot_market_movement_color = define_market_movement(plot_market_movement)

    print('days period', days_period)
    print('chart', chart_file)
    print('chart_interval', chart_interval)
    print('plot_index_interval', plot_index_interval)
    print('plot_index_start', plot_index_start)
    print('plot_index_end', plot_index_end)
    print('plot_price_start', plot_price_start)
    print('plot_price_end', plot_price_end)



    # Creation of plot axies:
    axis_date = plot_df['Date'][plot_index_start:plot_index_end]
    axis_price = plot_df['Price'][plot_index_start:plot_index_end]
    axis_total_volume = plot_df['Total Volume'][plot_index_start:plot_index_end]

    # Creation of plot figure:
    fig, ax1 = plt.subplots(figsize=(12, 6))
    fig.patch.set_alpha(0.0)
    fig.patch.set_facecolor('none')
    ax1.grid(True, linestyle="--", linewidth=0.5, alpha=0.7)
    ax2 = ax1.twinx()

    # Set axies lines:    
    ax1.plot(axis_date, axis_price, color=plot_colors['price'], label="Price", linewidth=1)
    ax2.plot(axis_date, axis_total_volume, color=plot_colors['total_volume'], label="Total Volume", alpha=0.2, linewidth=0.1)

    # Set axies text format:
    ax1.xaxis.set_major_formatter(FuncFormatter(lambda x, _: format_time_axis(x, days_period)))
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, _: format_money_axis(x)))
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, _: format_money_axis(x)))
    
    # Set horizontal axis text properties:
    plt.setp(ax1.get_xticklabels(), rotation=20, ha='center')

    # Set axies text color and font:
    ax1.tick_params(axis="x", labelcolor=plot_colors['date'])
    ax1.tick_params(axis="y", labelcolor=plot_colors['price'])
    ax2.tick_params(axis="y", labelcolor=plot_colors['total_volume'])
    for label in ax1.get_xticklabels() + ax1.get_yticklabels() + ax2.get_yticklabels():
        label.set_fontproperties(plot_font)

    # Set axies order (higher value puts layer to the front):
    ax1.set_zorder(2)
    ax2.set_zorder(1)
    
    # Set axies color filling:
    ax2.fill_between(axis_date, axis_total_volume, color=plot_colors['total_volume'], alpha=0.15)

    # Set plot legend:
    legend_price = Line2D([0], [0], label=f'Price, {config.vs_ticker}')
    legend_volume = Line2D([0], [0], label=f'Volume, {config.vs_ticker}')
    legend_market = Line2D([0], [0], label=f'Market: {plot_market_movement_format}')

    legend = ax1.legend(handles=[legend_price, legend_volume, legend_market], loc="upper left", prop=plot_font, handlelength=0)
    legend.get_texts()[0].set_color(plot_colors['price'])
    legend.get_texts()[1].set_color(plot_colors['total_volume'])
    legend.get_texts()[2].set_color(plot_colors[f'{plot_market_movement_color}'])
    legend.get_frame().set_facecolor(plot_colors['frame'])
    legend.get_frame().set_alpha(0.7)

    # Save plot image without background:
    plt.savefig(plot_file, bbox_inches='tight', transparent=True, dpi=150)

    # Background-related variables:
    background = select_plot_background(plot_market_movement)
    background_path = plot_background[f'{background}']['path']
    background_coordinates = plot_background[f'{background}']['coordinates']

    # Creation of plot background:
    background_image = Image.open(background_path)
    background_overlay = Image.open(plot_file)
    background_image.paste(background_overlay, background_coordinates, mask=background_overlay)

    # Save plot image with background:
    background_image.save(plot_output)
    

make_chart_plot(4)
