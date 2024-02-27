import os
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
from datetime import datetime, timedelta

sys.path.append('.')
import config
from logger import main_logger
from tools import (define_key_metric_movement,
                   calculate_percentage_change,
                   convert_timestamp_to_utc,
                   format_time_axis,
                   format_amount,
                   format_bytes,
                   format_currency,
                   format_percentage,
                   format_quantity)


'''
Functions related to creation of plot and markdown files for Network database.

Plot based on chart values and made for whole number of days. dates period based
on API endpoint specified in user configuration. Background image depends on % of
hashrate change (positive or negative). Axies have automatic appropriate scaling
to different dates periods.

Markdown based on snapshot and chart values and formatted for user presentation.
'''

def draw_network(days=30):
    # Draws Network plot with properties specified in user configuration.
    
    # User configuration related variables:
    chart = config.charts['network']
    chart_file_path = chart['file']['path']
    chart_file_name = chart['file']['name']
    chart_file = chart_file_path + chart_file_name

    # Plot-related variables:
    plot = config.images['network']
    plot_font = font_manager.FontProperties(fname=plot['font'])
    plot_colors = plot['colors']
    plot_background = plot['backgrounds']
        
    # Creation of plot DataFrame:
    plot_df = pd.read_csv(chart_file)

    # Set days value limits and image file name:
    if isinstance(days, int):
        days = 2 if days < 2 else days
        days = len(plot_df) - 1 if days > len(plot_df) - 1 else days
    else:
        days = len(plot_df) - 1
    plot_file = plot['path'] + f'network_days_{days}.jpg'

    plot_time_till = datetime.utcfromtimestamp(os.path.getctime(chart_file)).strftime('%Y-%m-%d')
    plot_time_from = (datetime.utcfromtimestamp(os.path.getctime(chart_file)) - timedelta(days=days)).strftime('%Y-%m-%d')

    # Specification of chart data indexes for plot axes:
    plot_index_last = len(plot_df)
    plot_index_first = len(plot_df) - days
    if plot_index_first < 1:
        plot_index_first = 1

    # Key metric related variables for percentage change calculation:
    plot_key_metric = 'hashrate'
    plot_key_metric_new = plot_df[plot_key_metric][plot_index_last - 1]
    plot_key_metric_old = plot_df[plot_key_metric][plot_index_first]
    plot_key_metric_movement = calculate_percentage_change(plot_key_metric_old, plot_key_metric_new)
    plot_key_metric_movement_format = format_percentage(plot_key_metric_movement)

    # Background-related variables:
    background = define_key_metric_movement(plot, plot_key_metric_movement)
    background_path = plot_background[f'{background}']['path']
    background_coordinates = plot_background[f'{background}']['coordinates']
    background_colors = plot_background[f'{background}']['colors']

    # Set rolling avearge to 2% of plot interval:
    rolling_average = math.ceil(days * 0.02)

    # Creation of plot axies:
    axis_date = plot_df['date'][plot_index_first:plot_index_last]
    axis_trx_per_block = plot_df['trx_per_block'].rolling(window=rolling_average).mean()[plot_index_first:plot_index_last]
    axis_hashrate = plot_df['hashrate'].rolling(window=rolling_average).mean()[plot_index_first:plot_index_last]
    axis_price = plot_df['price'][plot_index_first:plot_index_last]

    # Creation of plot figure:
    fig, ax1 = plt.subplots(figsize=(12, 7.4))
    fig.patch.set_alpha(0.0)
    fig.patch.set_facecolor('none')
    ax1.grid(True, linestyle="dashed", linewidth=0.5, alpha=0.7)
    ax2 = ax1.twinx()
    ax3 = ax1.twinx()

    # Set axies lines to change width depending on days period:
    linewidth_hashrate = 14 - days * 0.01
    if linewidth_hashrate < 10:
        linewidth_hashrate = 10
    linewidth_trx_per_block = 8 - days * 0.01
    if linewidth_trx_per_block < 6:
        linewidth_trx_per_block = 6

    ax1.plot(axis_date, axis_hashrate, color=plot_colors['hashrate'], label="hashrate", linewidth=linewidth_hashrate)
    ax2.plot(axis_date, axis_trx_per_block, color=plot_colors['trx_per_block'], label="trx_per_block", linewidth=linewidth_trx_per_block)
    ax3.plot(axis_date, axis_price, color=plot_colors['price'], label="price", alpha=0.0, linewidth=0.0)

    # Set axies left and right borders to first and last date of period. Bottom
    # and top borders are set to 95% of plot values for better scaling.
    ax1.set_xlim(axis_date.iloc[0], axis_date.iloc[-1])  
#    ax1.set_ylim(min(axis_hashrate) * 0.95, max(axis_hashrate) * 1.05)
#    ax2.set_ylim(min(axis_trx_per_block) * 0.95, max(axis_trx_per_block) * 1.05)
    ax3.set_ylim(min(axis_price) * 0.95, max(axis_price) * 1.05)

    # Set axies text format:
    ax1.xaxis.set_major_formatter(FuncFormatter(lambda x, _: format_time_axis(x, days)))
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, _: format_amount(x)))
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, _: format_amount(x)))
    
    # Set date axis ticks and text properties:
    axis_date_ticks_positions = np.linspace(axis_date.iloc[0], axis_date.iloc[-1], num=7) 
    ax1.set_xticks(axis_date_ticks_positions)
    plt.setp(ax1.get_xticklabels(), rotation=10, ha='center')

    # Set axies ticks text color, font and size:
    ax1.tick_params(axis="x", labelcolor=plot_colors['date'])
    ax1.tick_params(axis="y", labelcolor=plot_colors['hashrate'])
    ax2.tick_params(axis="y", labelcolor=plot_colors['trx_per_block'])
    ax3.set_yticks([])

    for label in ax1.get_xticklabels():
        label.set_fontproperties(plot_font)
        label.set_fontsize(12)

    for label in ax1.get_yticklabels() + ax2.get_yticklabels():
        label.set_fontproperties(plot_font)
        label.set_fontsize(18)

    # Set axies order (higher value puts layer to the front):
    ax1.set_zorder(3)
    ax2.set_zorder(2)
    ax3.set_zorder(1)
    
    # Set axies color filling and ticks visability:
    ax3.fill_between(axis_date, axis_price, color=plot_colors['price'], alpha=0.8)

    # Set plot legend proxies and actual legend:
    legend_proxy_hashrate = Line2D([0], [0], label='Hashrate, TH/s')
    legend_proxy_trx_per_block = Line2D([0], [0], label=f'TRX Per Block')
    legend_proxy_price = Line2D([0], [0], label=f'Price, {config.currency_vs_ticker}')

    legend = ax1.legend(handles=[legend_proxy_hashrate,
                                 legend_proxy_trx_per_block,
                                 legend_proxy_price],
                                 loc="upper left",
                                 prop=plot_font,
                                 handlelength=0)
    
    # Set legend colors:
    legend.get_texts()[0].set_color(plot_colors['hashrate'])
    legend.get_texts()[1].set_color(plot_colors['trx_per_block'])
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

    # Open background image, draw Network title and save image to memory buffer:
    title_image = Image.open(background_path)
    draw = ImageDraw.Draw(title_image)

    # Network title related variables:
    title_font = plot['font']
    title_list = [
            [{'text': 'blockchain.com', 'position': background_colors['api'][1], 'font_size': 36, 'text_color': background_colors['api'][0]},
            {'text': f'network performance', 'position': background_colors['api'][2], 'font_size': 26, 'text_color': background_colors['api'][0]}],

            [{'text': f'{plot_key_metric} {plot_key_metric_movement_format}', 'position': background_colors['metric'][1], 'font_size': 36, 'text_color': background_colors['metric'][0]},
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

    # Overlay plot buffer with Network title buffer and save final image:
    background_image = Image.open(title_buffer).convert("RGB")
    title_buffer.seek(0)
    background_overlay = Image.open(plot_buffer)
    plot_buffer.seek(0)

    background_image.paste(background_overlay, background_coordinates, mask=background_overlay)
    background_image.save(plot_file, "JPEG", quality=90, icc_profile=background_image.info.get('icc_profile', ''))
    title_buffer.close()
    plot_buffer.close()

    main_logger.info(f'[image] network (days {days}) plot drawn')

    return plot_file


def write_network(days=1):
    # Writes Network markdown with properties specified in user configuration.

    # User configuration related variables:
    snapshot = config.snapshots['network']
    snapshot_file_path = snapshot['file']['path']
    snapshot_file_name = snapshot['file']['name']
    snapshot_file = snapshot_file_path + snapshot_file_name

    markdown_file = snapshot_file_path + 'network.md'

    chart = config.charts['network']
    chart_file_path = chart['file']['path']
    chart_file_name = chart['file']['name']
    chart_file = chart_file_path + chart_file_name
    
    chart_data = pd.read_csv(chart_file)
    chart_date = chart_data['date']
    chart_price = chart_data['price']
    chart_hashrate = chart_data['hashrate']
    chart_trx_per_block = chart_data['trx_per_block']
    chart_blockchain_size = chart_data['blocks-size']

    # Set time period:
    now = len(chart_data) - 1
    if isinstance(days, int):
        days = 1 if days < 1 else days
        days = len(chart_data) - 1 if days > len(chart_data) - 1 else days
    else:
        days = len(chart_data) - 1
    past = len(chart_data) - days
    markdown_file = chart_file_path + f'network_days_{days}.md'

    with open (snapshot_file, 'r') as json_file:
        
        snapshot_data = json.load(json_file)

        # Parse raw API data to separate values:
        LAST_UPDATED = convert_timestamp_to_utc(snapshot_data['timestamp'])

        TIME_NOW = convert_timestamp_to_utc(chart_date[now])[:10]
        TIME_PAST = convert_timestamp_to_utc(chart_date[past])[:10]

        BLOCKS_HEIGHT = format_quantity(snapshot_data['n_blocks_total'])
        BLOCKS_MINED = format_quantity(snapshot_data['n_blocks_mined'])
        BLOCKS_SIZE = round(snapshot_data['blocks_size'] / (1_024**2) / int(BLOCKS_MINED), 2)
        BLOCKS_MINUTES = round(snapshot_data['minutes_between_blocks'], 1)

        BTC_SUPPLY = format_currency(snapshot_data['totalbc'] / 100_000_000, config.currency_crypto_ticker, decimal=0)
        BTC_MINED = format_currency(snapshot_data['n_btc_mined'] / 100_000_000, config.currency_crypto_ticker)
        BTC_SENT = format_currency(snapshot_data['total_btc_sent'] / 100_000_000, config.currency_crypto_ticker, decimal=0)
        BTC_PRICE = format_currency(snapshot_data['market_price_usd'], config.currency_vs_ticker, decimal=2)

        TRANSACTIONS_BLOCK = round(chart_trx_per_block.iloc[-1], 2)
        TRANSACTIONS_MADE = format_quantity(snapshot_data['n_tx'])
        TRANSACTIONS_COST = format_currency(chart_trx_per_block.iloc[-1], config.currency_vs_ticker, decimal=2)

        HASHRATE = format_amount(snapshot_data['hash_rate'] / 1_000)
        DIFFICULTY = format_amount(snapshot_data['difficulty'])
        RETARGET_HEIGHT = format_quantity(snapshot_data['nextretarget'])
        RETARGET_IN = format_quantity(snapshot_data['nextretarget'] - snapshot_data['n_blocks_total'])

        PRICE_NOW = format_currency(chart_price[now], config.currency_vs_ticker, decimal=2)
        PRICE_PAST = format_currency(chart_price[past], config.currency_vs_ticker, decimal=2)
        PRICE_PAST_CHANGE = format_currency(chart_price[now] - chart_price[past], config.currency_vs_ticker, decimal=2)
        PRICE_PAST_CHANGE_PERCENTAGE = format_percentage(calculate_percentage_change(chart_price[past], chart_price[now]))

        HASHRATE_NOW = format_amount(chart_hashrate[now])
        HASHRATE_PAST = format_amount(chart_hashrate[past])
        HASHRATE_PAST_CHANGE = format_amount((chart_hashrate[now] - chart_hashrate[past]))
        HASHRATE_PAST_CHANGE_PERCENTAGE = format_percentage(calculate_percentage_change(chart_hashrate[past], chart_hashrate[now]))

        TRX_PER_BLOCK_NOW = format_amount(chart_trx_per_block[now])
        TRX_PER_BLOCK_PAST = format_amount(chart_trx_per_block[past])
        TRX_PER_BLOCK_PAST_CHANGE = format_amount(chart_trx_per_block[now] - chart_trx_per_block[past])
        TRX_PER_BLOCK_PAST_CHANGE_PERCENTAGE = format_percentage(calculate_percentage_change(chart_trx_per_block[past], chart_trx_per_block[now]))

        BLOCKCHAIN_SIZE_NOW = format_bytes(chart_blockchain_size[now], 'MB')
        BLOCKCHAIN_SIZE_PAST = format_bytes(chart_blockchain_size[past], 'MB')
        BLOCKCHAIN_SIZE_PAST_CHANGE = format_bytes(chart_blockchain_size[now] - chart_blockchain_size[past], 'MB')
        BLOCKCHAIN_SIZE_PAST_CHANGE_PERCENTAGE = format_percentage(calculate_percentage_change(chart_blockchain_size[past], chart_blockchain_size[now]))
    
        # Format values text for user presentation:
        if days == 1:
            info_blocks = \
                f'Block Height: {BLOCKS_HEIGHT}\n' \
                f'24h Mined: {BLOCKS_MINED} blocks\n' \
                f'24h Size: {BLOCKS_SIZE} MB/block\n' \
                f'24h Time: {BLOCKS_MINUTES} min/block\n'
            info_coin = \
                f'Supply: {BTC_SUPPLY}\n' \
                f'24h Mined: {BTC_MINED}\n' \
                f'24h Sent: {BTC_SENT}\n' \
                f'24h Price: {BTC_PRICE}\n'
            info_transactions = \
                f'Transactions: {TRANSACTIONS_MADE}\n' \
                f'24h Avg: {TRANSACTIONS_BLOCK}/block\n' \
                f'24h Cost: {TRANSACTIONS_COST}/trx\n'
            info_network = \
                f'Blockchain Size: {BLOCKCHAIN_SIZE_NOW}\n' \
                f'Current Target: {DIFFICULTY}\n' \
                f'Retarget: {RETARGET_IN} blocks\n' \
                f'Hashrate: {HASHRATE} TH/s\n'
            info_update = f'UTC {LAST_UPDATED}\n'

            # Write latest values to Markdown file:
            with open (markdown_file, 'w') as markdown:
                markdown.write(f'```Network\n{info_blocks}\n{info_coin}\n{info_transactions}\n{info_network}\n{info_update}```')
        else:
            info_period = f'{TIME_PAST} --> {TIME_NOW}\n'
            info_trx_per_block = \
                f'Avg trx/block: {TRX_PER_BLOCK_PAST} --> {TRX_PER_BLOCK_NOW}\n' \
                f'{days}d: {TRX_PER_BLOCK_PAST_CHANGE_PERCENTAGE} ({TRX_PER_BLOCK_PAST_CHANGE}/block)\n'
            info_hashrate = \
                f'Hashrate: {HASHRATE_PAST} TH/s --> {HASHRATE_NOW} TH/s\n' \
                f'{days}d: {HASHRATE_PAST_CHANGE_PERCENTAGE} ({HASHRATE_PAST_CHANGE} TH/s)\n'
            info_blockchain_size = \
                f'Blockchain: {BLOCKCHAIN_SIZE_PAST} --> {BLOCKCHAIN_SIZE_NOW}\n' \
                f'{days}d: {BLOCKCHAIN_SIZE_PAST_CHANGE_PERCENTAGE} ({BLOCKCHAIN_SIZE_PAST_CHANGE})\n'
            info_price = \
                f'Price: {PRICE_PAST} --> {PRICE_NOW}\n' \
                f'{days}d: {PRICE_PAST_CHANGE_PERCENTAGE} ({PRICE_PAST_CHANGE})\n'
            
            # Write latest values to Markdown file:
            with open (markdown_file, 'w') as markdown:
                markdown.write(f'```Network\n{info_period}\n{info_trx_per_block}\n{info_hashrate}\n{info_blockchain_size}\n{info_price}```')

    main_logger.info(f'[markdown] network (days {days}) text written')

    return markdown_file




if __name__ == '__main__':

    days = [-1, 0, 1, 2, 90, 400, 1000, 'max']
    for day in days:
        draw_network(day)
        write_network(day)
  
    from tools import convert_date_to_days
    dates = ['2022-03-01', '2024-02-12']
    for date in dates:
        day = convert_date_to_days(date)
        draw_network(day)
        write_network(day)
