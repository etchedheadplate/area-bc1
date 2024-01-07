import io
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter
from matplotlib import font_manager
from PIL import Image

import config
from tools import (select_chart,
                   calculate_chart_interval,
                   calculate_percentage_change,
                   format_time_axis,
                   format_money_axis,
                   format_percentage,
                   define_market_movement)


def make_chart_plot(days):
    
    # User configuration related variables:
    chart_name = select_chart(days)[0]
    chart_file = config.databases[f'{chart_name}']['path'] + chart_name + '.csv'

    # Plot-related variables:
    plot_font = font_manager.FontProperties(fname=config.plot['font'])
    plot_colors = config.plot['colors']
    plot_background = config.plot['backgrounds']
    
    if days == 1:
        plot_output = config.plot['path'] + 'latest/latest_plot.png'
    else:
        plot_output = config.plot['path'] + f'history/history_plot_days_{days}.png'
    
    # Creation of plot data frame
    plot_df = pd.read_csv(chart_file)

    if days == 'max':
        days = len(plot_df) - 1

    # Specification of chart data indexes for plot axes:
    chart_interval = calculate_chart_interval(days)
    plot_index_last = plot_df.index.max()
    plot_index_first = plot_index_last - chart_interval

    # Market data related variables for percentage change calculation:
    plot_price_new = plot_df['Price'][plot_index_last]
    plot_price_old = plot_df['Price'][plot_index_first]
    plot_market_movement = calculate_percentage_change(plot_price_old, plot_price_new)
    plot_market_movement_format = format_percentage(plot_market_movement)
    plot_market_movement_color = define_market_movement(plot_market_movement)

    # Background-related variables:
    background = define_market_movement(plot_market_movement)
    background_path = plot_background[f'{background}']['path']
    background_coordinates = plot_background[f'{background}']['coordinates']

    # Creation of plot axies:
    axis_date = plot_df['Date'][plot_index_first:plot_index_last]
    axis_price = plot_df['Price'][plot_index_first:plot_index_last]
    axis_total_volume = plot_df['Total Volume'][plot_index_first:plot_index_last]

    # Creation of plot figure:
    fig, ax1 = plt.subplots(figsize=(12, 7.4))
    fig.patch.set_alpha(0.0)
    fig.patch.set_facecolor('none')
    ax1.grid(True, linestyle="dashed", linewidth=0.5, alpha=0.7)
    ax2 = ax1.twinx()

    # Set axies lines:    
    ax1.plot(axis_date, axis_price, color=plot_colors['price'], label="Price", linewidth=1)
    ax2.plot(axis_date, axis_total_volume, color=plot_colors['total_volume'], label="Total Volume", alpha=0.3, linewidth=0.1)

    # Set axies left and right borders to first and last date of period. Bottom border
    # is set to min total volume value and 99% of min price value for better user view
    ax1.set_xlim(axis_date.iloc[0], axis_date.iloc[-1])  
    ax1.set_ylim(min(axis_price) * 0.99)
    ax2.set_ylim(min(axis_total_volume))

    # Set axies text format:
    ax1.xaxis.set_major_formatter(FuncFormatter(lambda x, _: format_time_axis(x, days)))
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, _: format_money_axis(x)))
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, _: format_money_axis(x)))
    
    # Set date axis ticks and text properties:
    axis_date_ticks_positions = np.linspace(axis_date.iloc[0], axis_date.iloc[-1], num=6) 
    ax1.set_xticks(axis_date_ticks_positions)
    plt.setp(ax1.get_xticklabels(), rotation=10, ha='center')

    # Set axies ticks text color and font:
    ax1.tick_params(axis="x", labelcolor=plot_colors['date'])
    ax1.tick_params(axis="y", labelcolor=plot_colors['price'])
    ax2.tick_params(axis="y", labelcolor=plot_colors['total_volume'])

    # Set axies ticks text size:
    for label in ax1.get_xticklabels() + ax1.get_yticklabels() + ax2.get_yticklabels():
        label.set_fontproperties(plot_font)
        label.set_fontsize(14)

    # Set axies order (higher value puts layer to the front):
    ax1.set_zorder(2)
    ax2.set_zorder(1)
    
    # Set axies color filling:
    ax2.fill_between(axis_date, axis_total_volume, color=plot_colors['total_volume'], alpha=0.3)

    # Set plot legend proxies and actual legend:
    legend_proxy_price = Line2D([0], [0], label=f'Price, {config.currency_vs_ticker}')
    legend_proxy_volume = Line2D([0], [0], label=f'Volume, {config.currency_vs_ticker}')
    legend_proxy_market = Line2D([0], [0], label=f'Market: {plot_market_movement_format}')
    legend = ax1.legend(handles=[legend_proxy_price, legend_proxy_volume, legend_proxy_market], loc="upper left", prop=plot_font, handlelength=0)
    
    # Set legend colors
    legend.get_texts()[0].set_color(plot_colors['price'])
    legend.get_texts()[1].set_color(plot_colors['total_volume'])
    legend.get_texts()[2].set_color(plot_colors[f'{plot_market_movement_color}'])
    legend.get_frame().set_facecolor(plot_colors['frame'])
    legend.get_frame().set_alpha(0.5)

    # Set legend text size
    for text in legend.get_texts():
        text.set_fontsize(12)

    # Save plot image without background in memory buffer and transfer it to PIL.Image module:
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight', transparent=True, dpi=150)
    background_image = Image.open(background_path).convert("RGB")
    buffer.seek(0)
    background_overlay = Image.open(buffer)

    # Save plot image with background:
    background_image.paste(background_overlay, background_coordinates, mask=background_overlay)
    background_image.save(plot_output, "PNG", quality=100, icc_profile=background_image.info.get('icc_profile', ''))
    buffer.close()




if __name__ == '__main__':

    days = [1,2,6,7,365,366,1825,1826,'max']
    for day in days:
        make_chart_plot(day)
