import io
import json

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter
from matplotlib import font_manager
from PIL import Image

import config
from tools import (define_key_metric_movement,
                   calculate_percentage_change,
                   convert_timestamp_to_utc,
                   format_time_axis,
                   format_amount,
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

def draw_plot():
    # Draws Network plot with properties specified in user configuration.
    
    # User configuration related variables:
    chart = config.databases['charts']['network']
    chart_file_path = chart['file']['path']
    chart_file_name = chart['file']['name']
    chart_file = chart_file_path + chart_file_name

    # Plot-related variables:
    plot = config.plot['network']
    plot_font = font_manager.FontProperties(fname=plot['font'])
    plot_colors = plot['colors']
    plot_background = plot['backgrounds']
    plot_output = plot['path'] + 'network.jpg'
        
    # Creation of plot DataFrame:
    plot_df = pd.read_csv(chart_file)

    days = len(plot_df)

    # Specification of chart data indexes for plot axes:
    plot_index_last = len(plot_df)
    plot_index_first = 0

    # Key metric related variables for percentage change calculation:
    plot_key_metric = 'hashrate'
    plot_key_metric_new = plot_df[plot_key_metric][plot_index_last - 1]
    plot_key_metric_old = plot_df[plot_key_metric][plot_index_first]
    plot_key_metric_movement = calculate_percentage_change(plot_key_metric_old, plot_key_metric_new)
    plot_key_metric_movement_format = format_percentage(plot_key_metric_movement)
    plot_key_metric_movement_color = define_key_metric_movement(plot, plot_key_metric_movement)

    # Background-related variables:
    background = define_key_metric_movement(plot, plot_key_metric_movement)
    background_path = plot_background[f'{background}']['path']
    background_coordinates = plot_background[f'{background}']['coordinates']

    # Creation of plot axies:
    axis_date = plot_df['date'][plot_index_first:plot_index_last]
    axis_trx_per_block = plot_df['trx_per_block'][plot_index_first:plot_index_last]
    axis_hashrate = plot_df['hashrate'][plot_index_first:plot_index_last]
    axis_price = plot_df['price'][plot_index_first:plot_index_last]

    # Creation of plot figure:
    fig, ax1 = plt.subplots(figsize=(12, 7.4))
    fig.patch.set_alpha(0.0)
    fig.patch.set_facecolor('none')
    ax1.grid(True, linestyle="dashed", linewidth=0.5, alpha=0.7)
    ax2 = ax1.twinx()
    ax3 = ax1.twinx()

    # Set axies lines:    
    ax1.plot(axis_date, axis_hashrate, color=plot_colors['hashrate'], label="hashrate", linewidth=10)
    ax2.plot(axis_date, axis_trx_per_block, color=plot_colors['trx_per_block'], label="trx_per_block", linewidth=6)
    ax3.plot(axis_date, axis_price, color=plot_colors['price'], label="price", alpha=0.0, linewidth=0.0)

    # Set axies left and right borders to first and last date of period. Bottom
    # and top borders are set to 95% of plot values for better scaling.
    ax1.set_xlim(axis_date.iloc[0], axis_date.iloc[-1])  
    ax1.set_ylim(min(axis_hashrate) * 0.95, max(axis_hashrate) * 1.05)
    ax2.set_ylim(min(axis_trx_per_block) * 0.95, max(axis_trx_per_block) * 1.05)
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
    ax3.fill_between(axis_date, axis_price, color=plot_colors['price'], alpha=0.4)
    ax3.set_yticks([])

    # Set plot legend proxies and actual legend:
    legend_period =chart['api']['params']['timespan'][0:2]

    legend_proxy_hashrate = Line2D([0], [0], label='Hashrate, TH/s')
    legend_proxy_trx_per_block = Line2D([0], [0], label=f'TRX Per Block')
    legend_proxy_price = Line2D([0], [0], label=f'Price, {config.currency_vs_ticker}')
    legend_proxy_key_metric_movement = Line2D([0], [0], label=f'{legend_period} Hashrate {plot_key_metric_movement_format}')

    legend = ax2.legend(handles=[legend_proxy_hashrate,
                                 legend_proxy_trx_per_block,
                                 legend_proxy_price,
                                 legend_proxy_key_metric_movement],
                                 loc="upper left",
                                 prop=plot_font,
                                 handlelength=0)
    
    # Set legend colors:
    legend.get_texts()[0].set_color(plot_colors['hashrate'])
    legend.get_texts()[1].set_color(plot_colors['trx_per_block'])
    legend.get_texts()[2].set_color(plot_colors['price'])
    legend.get_texts()[3].set_color(plot_colors[f'{plot_key_metric_movement_color}'])
    legend.get_frame().set_facecolor(plot_colors['frame'])
    legend.get_frame().set_alpha(0.7)

    # Set legend text size:
    for text in legend.get_texts():
        text.set_fontsize(16)

    # Save plot image without background in memory buffer and transfer it to PIL.Image module:
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight', transparent=True, dpi=150)
    matplotlib.pyplot.close()
    background_image = Image.open(background_path).convert("RGB")
    buffer.seek(0)
    background_overlay = Image.open(buffer)

    # Save plot image with background:
    background_image.paste(background_overlay, background_coordinates, mask=background_overlay)
    background_image.save(plot_output, "JPEG", quality=90, icc_profile=background_image.info.get('icc_profile', ''))
    buffer.close()


def write_markdown():
    # Writes Network markdown with properties specified in user configuration.

    # User configuration related variables:
    snapshot = config.databases['snapshots']['network']
    snapshot_file_path = snapshot['file']['path']
    snapshot_file_name = snapshot['file']['name']
    snapshot_file = snapshot_file_path + snapshot_file_name

    markdown_file = snapshot_file_path + 'network.md'

    chart = config.databases['charts']['network']
    chart_file_path = chart['file']['path']
    chart_file_name = chart['file']['name']
    chart_file = chart_file_path + chart_file_name
    chart_data = pd.read_csv(chart_file)

    with open (snapshot_file, 'r') as json_file:
        
        snapshot_data = json.load(json_file)

        # Parse raw API data to separate values:
        LAST_UPDATED = convert_timestamp_to_utc(snapshot_data['timestamp'])

        BLOCKS_HEIGHT = format_quantity(snapshot_data['n_blocks_total'])
        BLOCKS_MINED = format_quantity(snapshot_data['n_blocks_mined'])
        BLOCKS_SIZE = round(snapshot_data['blocks_size'] / (1_024**2) / int(BLOCKS_MINED), 2)
        BLOCKS_MINUTES = round(snapshot_data['minutes_between_blocks'], 1)

        BTC_SUPPLY = format_currency(snapshot_data['totalbc'] / 100_000_000, config.currency_crypto_ticker, 0)
        BTC_MINED = format_currency(snapshot_data['n_btc_mined'] / 100_000_000, config.currency_crypto_ticker)
        BTC_SENT = format_currency(snapshot_data['total_btc_sent'] / 100_000_000, config.currency_crypto_ticker)
        BTC_PRICE = format_currency(snapshot_data['market_price_usd'], config.currency_vs_ticker)

        TRANSACTIONS_BLOCK = round(chart_data['trx_per_block'].iloc[-1], 2)
        TRANSACTIONS_MADE = format_quantity(snapshot_data['n_tx'])
        TRANSACTIONS_COST = format_currency(chart_data['trx_cost'].iloc[-1], config.currency_vs_ticker)

        HASHRATE = format_amount(snapshot_data['hash_rate'] / 1_000)
        DIFFICULTY = format_amount(snapshot_data['difficulty'])
        RETARGET_HEIGHT = format_quantity(snapshot_data['nextretarget'])
        RETARGET_IN = format_quantity(snapshot_data['nextretarget'] - snapshot_data['n_blocks_total'])
    
        # Format values text for user presentation:
        info_blocks = f'[Blocks]\n' \
            f'Height: {BLOCKS_HEIGHT}\n' \
            f'24h Mined: {BLOCKS_MINED} blocks\n' \
            f'24h Size: {BLOCKS_SIZE} MB/block\n' \
            f'24h Time: {BLOCKS_MINUTES} min/block\n'
        info_coin = f'[Bitcoin]\n' \
            f'Supply: {BTC_SUPPLY}\n' \
            f'24h Mined: {BTC_MINED}\n' \
            f'24h Sent: {BTC_SENT}\n' \
            f'24h Price: {BTC_PRICE}\n'
        info_transactions = f'[Transactions]\n' \
            f'Avg: {TRANSACTIONS_BLOCK}/block\n' \
            f'24h Total: {TRANSACTIONS_MADE}\n' \
            f'24h Cost: {TRANSACTIONS_COST}/trx\n'
        info_network = f'[Difficulty]\n' \
            f'Current Target: {DIFFICULTY}\n' \
            f'Retarget: in {RETARGET_IN} blocks\n' \
            f'Hashrate: {HASHRATE} TH/s\n'
        info_update = f'UTC {LAST_UPDATED}\n'

        # Write latest values to Markdown file:
        with open (markdown_file, 'w') as markdown:
            markdown.write(f"```Network\n{info_blocks}\n{info_coin}\n{info_transactions}\n{info_network}\n{info_update}```")




if __name__ == '__main__':
    
    draw_plot()
    write_markdown()