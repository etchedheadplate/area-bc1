import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter
from matplotlib import font_manager
from PIL import Image

import config
from tools import (select_data_chart_for_plot,
                   calculate_chart_interval,
                   calculate_percentage_change,
                   format_time_axis,
                   format_money_axis,
                   format_percentage,
                   define_market_movement)


def make_chart_plot(days_period):
    
    # User configuration related variables: 
    chart_file = select_data_chart_for_plot(days_period)

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
    plot_index_last = plot_df.index.max()
    plot_index_first = plot_index_last - chart_interval

    # Market data related variables for percentage change calculation:
    plot_price_new = plot_df['Price'][plot_index_last]
    plot_price_old = plot_df['Price'][plot_index_first]
    plot_market_movement = calculate_percentage_change(plot_price_old, plot_price_new)
    plot_market_movement_format = format_percentage(plot_market_movement)
    plot_market_movement_color = define_market_movement(plot_market_movement)
    print(plot_market_movement_color)


    # Plot figure block:

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


    # Axies block:

        # Set axies lines:    
    ax1.plot(axis_date, axis_price, color=plot_colors['price'], label="Price", linewidth=1)
    ax2.plot(axis_date, axis_total_volume, color=plot_colors['total_volume'], label="Total Volume", alpha=0.5, linewidth=0.5)

        # Set axies left and right borders to first and last date of period. Bottom border
        # is set to min total volume value and 99% of min price value for better user view
    ax1.set_xlim(axis_date.iloc[0], axis_date.iloc[-1])  
    ax1.set_ylim(min(axis_price) * 0.99)
    ax2.set_ylim(min(axis_total_volume))

        # Set axies text format:
    ax1.xaxis.set_major_formatter(FuncFormatter(lambda x, _: format_time_axis(x, days_period)))
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, _: format_money_axis(x)))
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, _: format_money_axis(x)))
    
        # Set horizontal axis ticks text properties:
    plt.setp(ax1.get_xticklabels(), rotation=20, ha='center')

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


    # Legend block:

        # Set plot legend proxies and actual legend:
    legend_proxy_price = Line2D([0], [0], label=f'Price, {config.vs_ticker}')
    legend_proxy_volume = Line2D([0], [0], label=f'Volume, {config.vs_ticker}')
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


    # Save plot image without background:
    plt.savefig(plot_file, bbox_inches='tight', transparent=True, dpi=150)


    # Background block:

        # Background-related variables:
    background = define_market_movement(plot_market_movement)
    background_path = plot_background[f'{background}']['path']
    background_coordinates = plot_background[f'{background}']['coordinates']

        # Creation of plot background:
    background_image = Image.open(background_path).convert("RGB")
    background_overlay = Image.open(plot_file)
    background_image.paste(background_overlay, background_coordinates, mask=background_overlay)

        # Save plot image with background:
    background_image.save(plot_output, "JPEG", quality=95, icc_profile=background_image.info.get('icc_profile', ''))


if __name__ == '__main__':

        make_chart_plot(30)
