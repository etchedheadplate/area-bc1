import io
import sys
import math
import json
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
from tools import (format_amount,
                   format_currency,
                   format_percentage)


def draw_seized(days=1):
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
    plot_df = pd.read_csv(chart_file).sort_index(ascending=False)

    # Set days value limits and image file name:
    days = len(plot_df)
    plot_file = chart_file_path + 'seized.jpg'

    # Background-related variables:
    background_path = plot_background['path']
    background_coordinates = plot_background['coordinates']
    background_colors = plot_background['colors']

    # Set rolling avearge to 2% of days:
    rolling_average = math.ceil(days * 0.02)

    # Creation of plot axies
    axis_date = plot_df['day'].str.slice(stop=-17)
    axis_usd = plot_df['USD_Balance']
    axis_btc = plot_df['BTC_Balance']
    axis_price = plot_df['BTC_price'].rolling(window=rolling_average).mean()

    # Creation of plot figure:
    fig, ax1 = plt.subplots(figsize=(12, 7.4))
    fig.patch.set_alpha(0.0)
    fig.patch.set_facecolor('none')
    ax1.grid(True, linestyle="dashed", linewidth=0.5, alpha=0.7)
    ax2 = ax1.twinx()
    ax3 = ax1.twinx()

    # Set axies lines:
    ax1.plot(axis_date, axis_usd, color=plot_colors['usd'], label="usd", alpha=0.0, linewidth=0.0)
    ax2.plot(axis_date, axis_btc, color=plot_colors['btc'], label="btc", alpha=0.0, linewidth=0.0)
    ax3.plot(axis_date, axis_price, color=plot_colors['price'], label="btc", linewidth=10)

    # Set axies left and right borders to first and last date of period. Bottom and top
    # border are set to persentages of axies for better scaling.
    ax1.set_xlim(axis_date.iloc[0], axis_date[plot_df.index[-1]])  
    ax1.set_ylim(min(axis_usd) * 0.99, max(axis_usd) * 1.01)
    ax2.set_ylim(min(axis_btc), max(axis_btc) * 1.05)
#    ax3.set_ylim(min(axis_price) * 0.75, max(axis_price) * 1.25)

    # Set axies text format:
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, _: format_amount(x)))
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, _: format_amount(x)))
    
    # Set date axis ticks and text properties:
    date_range_indexes = np.linspace(0, len(axis_date) - 1, num=7, dtype=int)
    ax1.set_xticks(date_range_indexes[::-1])
    ax1.set_xticklabels([axis_date[i] for i in date_range_indexes], rotation=10, ha='center')
    plt.setp(ax1.get_xticklabels(), rotation=10, ha='center')

    # Set axies ticks text color, font and size:
    ax1.tick_params(axis="x", labelcolor=plot_colors['date'])
    ax1.tick_params(axis="y", labelcolor=plot_colors['usd'])
    ax2.tick_params(axis="y", labelcolor=plot_colors['btc'])
    ax3.set_yticks([])

    for label in ax1.get_xticklabels():
        label.set_fontproperties(plot_font)
        label.set_fontsize(12)

    for label in ax1.get_yticklabels() + ax2.get_yticklabels():
        label.set_fontproperties(plot_font)
        label.set_fontsize(18)

    # Set axies order (higher value puts layer to the front):
    ax1.set_zorder(2)
    ax2.set_zorder(1)
    ax3.set_zorder(3)
    
    # Set axies color filling:
    ax1.fill_between(axis_date, axis_usd, color=plot_colors['usd'], alpha=0.7)
    ax2.fill_between(axis_date, axis_btc, color=plot_colors['btc'], alpha=0.8)

    # Set plot legend proxies and actual legend:
    legend_proxy_usd = Line2D([0], [0], label=f'Balance, USD')
    legend_proxy_btc = Line2D([0], [0], label=f'Balance, BTC')
    legend_proxy_price = Line2D([0], [0], label=f'BTC Price, USD')
    legend = ax3.legend(handles=[legend_proxy_usd, legend_proxy_btc, legend_proxy_price], loc="upper left", prop=plot_font, handlelength=0)
    
    # Set legend colors:
    legend.get_texts()[0].set_color(plot_colors['usd'])
    legend.get_texts()[1].set_color(plot_colors['btc'])
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
            {'text': f'bitcoins seized by USA', 'position': background_colors['api'][2], 'font_size': 26, 'text_color': background_colors['api'][0]}]
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

    main_logger.info(f'[image] seized plot drawn')

    return plot_file


def write_seized(days=1):

    seized_chart = config.charts['seized']
    seized_chart_file_path = seized_chart['file']['path']
    seized_chart_file_name = seized_chart['file']['name']
    seized_chart_file = seized_chart_file_path + seized_chart_file_name
    
    network_snapshot = config.snapshots['network']
    network_snapshot_file_path = network_snapshot['file']['path']
    network_snapshot_file_name = network_snapshot['file']['name']
    network_snapshot_file = network_snapshot_file_path + network_snapshot_file_name
    
    seized_chart_data = pd.read_csv(seized_chart_file)
    seized_date = seized_chart_data['day']
    seized_balance_btc = seized_chart_data['BTC_Balance']
    seized_balance_usd = seized_chart_data['USD_Balance']

    markdown_file = seized_chart_file_path + 'seized.md'

    LAST_UPDATE = seized_date[0][:10]

    CURRENT_BALANCE_BTC = format_currency(seized_balance_btc[0], config.currency_crypto_ticker, decimal=2)
    CURRENT_BALANCE_USD = format_currency(seized_balance_usd[0], config.currency_vs_ticker, decimal=2)

    with open (network_snapshot_file, 'r') as network_file:
        network_data = json.load(network_file)
        network_btc_supply = network_data['totalbc'] / 100_000_000
        CURRENT_SUPPLY_BTC = format_currency(network_btc_supply, config.currency_crypto_ticker, decimal=2)
        CURRENT_SUPPLY_PERCENTAGE = format_percentage(seized_balance_btc[0] / network_btc_supply * 100)[1:]

    MAX_BALANCE_BTC = format_currency(seized_balance_btc.max(), config.currency_crypto_ticker, decimal=2)
    MAX_BALANCE_BTC_DATE = seized_date.loc[seized_balance_btc.idxmax()][:10]

    MAX_BALANCE_USD = format_currency(seized_balance_usd.max(), config.currency_vs_ticker, decimal=2)
    MAX_BALANCE_USD_DATE = seized_date.loc[seized_balance_usd.idxmax()][:10]

    # Format text for user presentation:
    info_balance = f'[Balance]\n' \
        f'BTC: {CURRENT_BALANCE_BTC}\n' \
        f'USD: {CURRENT_BALANCE_USD}\n' \
        f'{CURRENT_SUPPLY_PERCENTAGE} of {CURRENT_SUPPLY_BTC} mined\n'
    info_ATH = f'[All-Time-High]\n' \
        f'BTC: {MAX_BALANCE_BTC}\n' \
        f'at {MAX_BALANCE_BTC_DATE}\n' \
        f'USD: {MAX_BALANCE_USD}\n' \
        f'at {MAX_BALANCE_USD_DATE}\n'
    info_update = f'Last update at {LAST_UPDATE}\n'
    Info_links = f'[Source, stats & methology](https://dune.com/21co/us-gov-bitcoin-holdings)\n' \
        f'[More countries & companies](https://bitcointreasuries.net/)\n'
    
    # Write text to Markdown file:
    with open (markdown_file, 'w') as markdown:
        markdown.write(f'```\n{info_balance}\n{info_ATH}\n{info_update}\n```\n{Info_links}')
    
    main_logger.info(f'[markdown] seized text written')

    return markdown_file




if __name__ == '__main__':
    draw_seized()
    write_seized()