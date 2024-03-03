import io
import sys
import json
import math
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter
from matplotlib import font_manager
from PIL import Image, ImageDraw, ImageFont

sys.path.append('.')
import config
from logger import main_logger
from tools import (error_handler_common,
                   define_key_metric_movement,
                   format_amount,
                   format_currency,
                   format_percentage,
                   calculate_percentage_change)



'''
Functions related to creation of plot and markdown files for USA seized database.

Plot based on chart values and made for whole number of days. Dates period based
on API endpoint specified in user configuration. Background image depends on % of
BTC holdings change (positive or negative). Axes have automatic appropriate
scaling to different dates periods.

Markdown based on snapshot and chart values and formatted for user presentation.
'''


@error_handler_common
def draw_seized(days=config.days['seized']):
    # Draws Seized plot with properties specified in user configuration.
    
    # User configuration related variables:
    chart = config.charts['seized']
    chart_file_path = chart['file']['path']
    chart_file_name = chart['file']['name']
    chart_file = chart_file_path + chart_file_name

    # Plot-related variables:
    plot = config.images['seized']
    plot_font = font_manager.FontProperties(fname=plot['font'])
    plot_colors = plot['colors']
    plot_background = plot['backgrounds']
        
    # Creation of plot DataFrame:
    plot_df = pd.read_csv(chart_file)[:-2].sort_index(ascending=False).reset_index()

    # Set time period:
    if isinstance(days, int):
        days = 2 if days < 2 else days
        days = len(plot_df) - 1 if days > len(plot_df) - 1 else days
        plot_file = plot['path'] + f'seized_days_{days}.jpg'
    else:
        days = len(plot_df) - 1
        plot_file = plot['path'] + f'seized_days_max.jpg'

    index_period_end = len(plot_df) - 1
    index_period_start = index_period_end - days

    plot_time_till = plot_df['day'].iloc[index_period_end][:10]
    plot_time_from = plot_df['day'].iloc[index_period_start][:10]

    # Specification of chart data indexes for plot axes:
    plot_index_last = len(plot_df) - 1
    plot_index_first = len(plot_df) - days
    if plot_index_first < 1:
        plot_index_first = 1

    # Key metric related variables for percentage change calculation:
    plot_key_metric = 'BTC_Balance'
    plot_key_metric_new = plot_df[plot_key_metric][plot_index_last]
    plot_key_metric_old = plot_df[plot_key_metric][plot_index_first]
    plot_key_metric_movement = calculate_percentage_change(plot_key_metric_old, plot_key_metric_new)
    plot_key_metric_movement_format = format_percentage(plot_key_metric_movement)

    # Background-related variables:
    background = define_key_metric_movement(plot, plot_key_metric_movement)
    background_path = plot_background[f'{background}']['path']
    background_coordinates = plot_background[f'{background}']['coordinates']
    background_colors = plot_background[f'{background}']['colors']

    # Set rolling avearge to 2% of days:
    rolling_average = math.ceil(days * 0.02)

    # Creation of plot axes
    axis_date = plot_df['day'].str.slice(stop=-17)
    axis_date = axis_date[index_period_start:index_period_end].reset_index(drop=True)
    axis_usd = plot_df['USD_Balance'][index_period_start:index_period_end]
    axis_btc = plot_df['BTC_Balance'][index_period_start:index_period_end]
    axis_price = plot_df['BTC_price'][index_period_start:index_period_end].rolling(window=rolling_average).mean()

    # Creation of plot figure:
    fig, ax1 = plt.subplots(figsize=(12, 7.4))
    fig.patch.set_alpha(0.0)
    fig.patch.set_facecolor('none')
    ax1.grid(True, linestyle="dashed", linewidth=0.5, alpha=0.7)
    ax2 = ax1.twinx()
    ax3 = ax1.twinx()

    # Set axes lines:
    ax1.plot(axis_date, axis_btc, color=plot_colors['btc'], label="btc", alpha=0.0, linewidth=0.0)
    ax2.plot(axis_date, axis_usd, color=plot_colors['usd'], label="usd", alpha=0.0, linewidth=0.0)
    ax3.plot(axis_date, axis_price, color=plot_colors['price'], label="btc", linewidth=10)

    # Set axes left and right borders to first and last date of period. Bottom and top
    # border are set to persentages of axes for better scaling.
    ax1.set_xlim(axis_date.iloc[0], axis_date.iloc[-1])  
    ax1.set_ylim(min(axis_btc) * 0.95, max(axis_btc) * 1.05)
    ax2.set_ylim(min(axis_usd) * 0.95, max(axis_usd) * 1.05)
#    ax3.set_ylim(min(axis_price) * 0.75, max(axis_price) * 1.25)

    # Set axes text format:
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, _: format_amount(x)))
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, _: format_amount(x)))
    
    # Set date axis ticks and text properties:
    date_range_indexes = np.linspace(0, len(axis_date) - 1, num=7, dtype=int)
    ax1.set_xticks(date_range_indexes)
    ax1.set_xticklabels([axis_date[i] for i in date_range_indexes], rotation=10, ha='center')
    plt.setp(ax1.get_xticklabels(), rotation=10, ha='center')

    # Set axes ticks text color, font and size:
    ax1.tick_params(axis="x", labelcolor=plot_colors['date'])
    ax1.tick_params(axis="y", labelcolor=plot_colors['btc'])
    ax2.tick_params(axis="y", labelcolor=plot_colors['usd'])
    ax3.set_yticks([])

    for label in ax1.get_xticklabels():
        label.set_fontproperties(plot_font)
        label.set_fontsize(12)

    for label in ax1.get_yticklabels() + ax2.get_yticklabels():
        label.set_fontproperties(plot_font)
        label.set_fontsize(18)

    # Set axes order (higher value puts layer to the front):
    ax1.set_zorder(1)
    ax2.set_zorder(2)
    ax3.set_zorder(3)
    
    # Set axes color filling:
    ax1.fill_between(axis_date, axis_btc, color=plot_colors['btc'], alpha=0.8)
    ax2.fill_between(axis_date, axis_usd, color=plot_colors['usd'], alpha=0.7)

    # Set plot legend proxies and actual legend:
    legend_proxy_usd = Line2D([0], [0], label=f'Balance, BTC')
    legend_proxy_btc = Line2D([0], [0], label=f'Balance, USD')
    legend_proxy_price = Line2D([0], [0], label=f'BTC Price, USD')
    legend = ax3.legend(handles=[legend_proxy_usd, legend_proxy_btc, legend_proxy_price], loc="upper left", prop=plot_font, handlelength=0)
    
    # Set legend colors:
    legend.get_texts()[0].set_color(plot_colors['btc'])
    legend.get_texts()[1].set_color(plot_colors['usd'])
    legend.get_texts()[2].set_color(plot_colors['price'])
    legend.get_frame().set_facecolor(plot_colors['frame'])
    legend.get_frame().set_alpha(0.7)

    # Set legend text size:
    for text in legend.get_texts():
        text.set_fontsize(16)

    # Open memory buffer and save plot to memory buffer:
    plot_buffer = io.BytesIO()
    plt.savefig(plot_buffer, format='png', bbox_inches='tight', transparent=True, dpi=150)
    matplotlib.pyplot.close()

    # Open background image, draw Market title and save image to memory buffer:
    title_image = Image.open(background_path)
    draw = ImageDraw.Draw(title_image)

    # Seized title related variables:
    title_font = plot['font']
    title_list = [
            [{'text': '21.co @ dune.com', 'position': background_colors['api'][1], 'font_size': 36, 'text_color': background_colors['api'][0]},
            {'text': f'bitcoins seized by USA', 'position': background_colors['api'][2], 'font_size': 26, 'text_color': background_colors['api'][0]}],

            [{'text': f'BTC {plot_key_metric_movement_format}', 'position': background_colors['metric'][1], 'font_size': 36, 'text_color': background_colors['metric'][0]},
            {'text': f'{plot_time_from} - {plot_time_till}', 'position': background_colors['metric'][2], 'font_size': 24, 'text_color': background_colors['metric'][0]}]
    ]
    
    for title in title_list:
        for param in title:
            text = param.get('text')
            position = param.get('position')
            size = param.get('font_size')
            font = ImageFont.truetype(title_font, size)
            text_color = param.get('text_color')

            draw.text(position, text, font=font, fill=text_color)

    title_buffer = io.BytesIO()
    title_image.save(title_buffer, 'PNG')

    # Overlay plot buffer with Seized title buffer and save final image:
    background_image = Image.open(title_buffer).convert("RGB")
    title_buffer.seek(0)
    background_overlay = Image.open(plot_buffer)
    plot_buffer.seek(0)

    background_image.paste(background_overlay, background_coordinates, mask=background_overlay)
    background_image.save(plot_file, "JPEG", quality=90, icc_profile=background_image.info.get('icc_profile', ''))
    title_buffer.close()
    plot_buffer.close()

    main_logger.info(f'[image] seized (days {days}) plot drawn')

    return plot_file


@error_handler_common
def write_seized(days=1):

    seized_chart = config.charts['seized']
    seized_chart_file_path = seized_chart['file']['path']
    seized_chart_file_name = seized_chart['file']['name']
    seized_chart_file = seized_chart_file_path + seized_chart_file_name
    
    network_snapshot = config.snapshots['network']
    network_snapshot_file_path = network_snapshot['file']['path']
    network_snapshot_file_name = network_snapshot['file']['name']
    network_snapshot_file = network_snapshot_file_path + network_snapshot_file_name
    
    seized_chart_data = pd.read_csv(seized_chart_file).sort_index(ascending=False).reset_index(drop=True)
    seized_date = seized_chart_data['day']
    seized_balance_btc = seized_chart_data['BTC_Balance']
    seized_balance_usd = seized_chart_data['USD_Balance']

    # Set time period:
    now = len(seized_chart_data) - 1
    if isinstance(days, int):
        days = 1 if days < 1 else days
        days = len(seized_chart_data) - 1 if days > len(seized_chart_data) - 1 else days
    else:
        days = len(seized_chart_data) - 1
    past = len(seized_chart_data) - days
    markdown_file = seized_chart_file_path + f'seized_days_{days}.md'

    # Parse chart to separate values:

    TIME_NOW = seized_date[now][:10]
    TIME_PAST = seized_date[past][:10]

    BALANCE_BTC_CURRENT = format_currency(seized_balance_btc[now], config.currency_crypto_ticker, decimal=2)
    BALANCE_USD_CURRENT = format_currency(seized_balance_usd[now], config.currency_vs_ticker, decimal=2)

    ATH_BALANCE_BTC = format_amount(seized_balance_btc.max(), config.currency_crypto_ticker)
    ATH_BALANCE_BTC_DATE = seized_date.loc[seized_balance_btc.idxmax()][:10]

    ATH_BALANCE_USD = format_amount(seized_balance_usd.max(), config.currency_vs_ticker)
    ATH_BALANCE_USD_DATE = seized_date.loc[seized_balance_usd.idxmax()][:10]

    with open (network_snapshot_file, 'r') as network_file:
        network_data = json.load(network_file)
        network_btc_supply = network_data['totalbc'] / 100_000_000
        SUPPLY_BTC_CURRENT = format_amount(network_btc_supply, config.currency_crypto_ticker)
        SUPPLY_BTC_CURRENT_PERCENTAGE = format_percentage(seized_balance_btc[now] / network_btc_supply * 100)[1:]


    BALANCE_BTC_NOW_AMOUNT = format_amount(seized_balance_btc[now], config.currency_crypto_ticker) 
    BALANCE_BTC_PAST_AMOUNT = format_amount(seized_balance_btc[past], config.currency_crypto_ticker) 
    BALANCE_BTC_PAST_CHANGE = format_amount(seized_balance_btc[now] - seized_balance_btc[past], config.currency_crypto_ticker)
    BALANCE_BTC_PAST_CHANGE_PERCENTAGE = format_percentage(calculate_percentage_change(seized_balance_btc[past], seized_balance_btc[now]))

    BALANCE_USD_NOW_AMOUNT = format_amount(seized_balance_usd[now], config.currency_vs_ticker)
    BALANCE_USD_PAST_AMOUNT = format_amount(seized_balance_usd[past], config.currency_vs_ticker)
    BALANCE_USD_PAST_CHANGE = format_amount(seized_balance_usd[now] - seized_balance_usd[past], config.currency_vs_ticker)
    BALANCE_USD_PAST_CHANGE_PERCENTAGE = format_percentage(calculate_percentage_change(seized_balance_usd[past], seized_balance_usd[now]))

    # Format text for user presentation:
    if days == 1:
        info_balance = \
            f'BTC: {BALANCE_BTC_CURRENT}\n' \
            f'USD: {BALANCE_USD_CURRENT}\n'
        info_supply = f'{SUPPLY_BTC_CURRENT_PERCENTAGE} of {SUPPLY_BTC_CURRENT} mined\n'
        info_ATH = \
            f'ATH BTC: {ATH_BALANCE_BTC_DATE} ({ATH_BALANCE_BTC})\n' \
            f'ATH USD: {ATH_BALANCE_USD_DATE} ({ATH_BALANCE_USD})\n'
        info_update = f'Last updated {TIME_NOW}\n'
        Info_links = f'[Methology & additional Stats](https://dune.com/21co/us-gov-bitcoin-holdings)\n' \
            f'[More Countries & Companies](https://bitcointreasuries.net/)'
        
        # Write text to Markdown file:
        with open (markdown_file, 'w') as markdown:
            markdown.write(f'```Seized\n{info_balance}\n{info_supply}\n{info_ATH}\n{info_update}```{Info_links}')
    else:
        info_period = f'{TIME_PAST} --> {TIME_NOW}\n'
        info_balance_btc = \
            f'BTC: {BALANCE_BTC_PAST_AMOUNT} --> {BALANCE_BTC_NOW_AMOUNT}\n' \
            f'{days}d: {BALANCE_BTC_PAST_CHANGE_PERCENTAGE} ({BALANCE_BTC_PAST_CHANGE})\n'
        info_balance_usd = \
            f'USD: {BALANCE_USD_PAST_AMOUNT} --> {BALANCE_USD_NOW_AMOUNT}\n' \
            f'{days}d: {BALANCE_USD_PAST_CHANGE_PERCENTAGE} ({BALANCE_USD_PAST_CHANGE})\n'
        Info_links = f'[Methology & additional Stats](https://dune.com/21co/us-gov-bitcoin-holdings)\n' \
            f'[More Countries & Companies](https://bitcointreasuries.net/)'
        
        # Write text to Markdown file:
        with open (markdown_file, 'w') as markdown:
            markdown.write(f'```ETFs\n{info_period}\n{info_balance_btc}\n{info_balance_usd}```{Info_links}')
    
    main_logger.info(f'[markdown] seized (days {days}) text written')

    return markdown_file




if __name__ == '__main__':

    test_days = [-1, 0, 1, 2, 10, 100, 365, 690, 1095, 'max']
    for day in test_days:
        draw_seized(day)
        write_seized(day)

    from tools import convert_date_to_days
    test_dates = ['2022-06-22']
    for date in test_dates:
        day = convert_date_to_days(date)
        draw_seized(day)
        write_seized(day)