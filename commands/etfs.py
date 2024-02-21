import io
import sys
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
from tools import (calculate_percentage_change,
                   format_amount,
                   format_currency,
                   format_percentage)


def draw_etfs():
    # Draws ETFs plot with properties specified in user configuration.
    
    # User configuration related variables:
    chart = config.charts['etfs']
    chart_file_path = chart['file']['path']
    chart_file_name = chart['file']['name']
    chart_file = chart_file_path + chart_file_name

    # Plot-related variables:
    plot = config.images['etfs']
    plot_font = font_manager.FontProperties(fname=plot['font'])
    plot_colors = plot['colors']
    plot_background = plot['backgrounds']
    plot_file = plot['path'] + 'etfs.jpg'
        
    # Create plot DataFrame:
    plot_df = pd.read_csv(chart_file)
    plot_df = plot_df.sort_values(by='time')

    holdings_btc_df = plot_df.groupby('time')['tvl'].sum().reset_index() # group items on time collumn and sum TVL for each date
    holdings_usd_df = plot_df.groupby('time')['usd_tvl'].sum().reset_index() # group items on time collumn and sum TVL for each date

    areas_df_percent = plot_df.merge(holdings_btc_df, on='time', suffixes=('', '_total'))
    areas_df_percent['percent'] = (areas_df_percent['tvl'] / areas_df_percent['tvl_total']) * 100
    areas_df_last_day = areas_df_percent[areas_df_percent['time'] == areas_df_percent['time'].max()]
    areas_df_top_issuers = areas_df_last_day.nlargest(5, 'percent')['issuer'].tolist() # top issuers with biggest % at last chart day
    areas_df_percent['issuer_grouped'] = areas_df_percent['issuer'].apply(lambda x: x if x in areas_df_top_issuers else 'Others')
    areas_df = areas_df_percent.pivot_table(index='time', columns='issuer_grouped', values='percent', aggfunc='sum').reset_index()
    
    # Set time period:
    days_df = plot_df[['time']].drop_duplicates()
    chart_time_till = days_df['time'].iloc[-1][:10]
    chart_time_from = days_df['time'].iloc[0][:10]

    # Background-related variables:
    background_path = plot_background['path']
    background_coordinates = plot_background['coordinates']
    background_colors = plot_background['colors']

    # Creation of plot axies:
    axis_date = areas_df['time'].str.slice(stop=-17)
    axis_holdings_btc = holdings_btc_df['tvl']
    axis_holdings_usd = holdings_usd_df['usd_tvl']

    # Creation of plot stacked area:
    issuers_df = areas_df.drop(columns=['time'])
    issuers_df_last_row_sorted = issuers_df.iloc[-1].sort_values(ascending=False)
    issuers_df = issuers_df[issuers_df_last_row_sorted.index]
    
    # Creation of plot figure:
    fig, ax1 = plt.subplots(figsize=(12, 7.4))
    fig.patch.set_alpha(0.0)
    fig.patch.set_facecolor('none')
    ax1.grid(True, axis = 'both', linestyle="dashed", linewidth=0.5, alpha=0.7)
    ax2 = ax1.twinx()
    ax3 = ax1.twinx()

    # Set axies lines to change width depending on days period:
    ax1.plot(axis_date, axis_holdings_btc, color=plot_colors['btc'], label="btc", alpha=0.9, linewidth=14)
    ax2.plot(axis_date, axis_holdings_usd, color=plot_colors['usd'], label="usd", linewidth=10)

    # Set stacked area colors:
    issuers_colors = plot_colors['areas']
    ax3.stackplot(axis_date, issuers_df.T, colors=issuers_colors)

    # Set axies borders for better scaling:
    ax1.set_xlim(axis_date.iloc[0], axis_date.iloc[-1])
    ax3.set_ylim(0, 100)

    # Set axies text format:
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, _: format_amount(x)))
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, _: format_amount(x)))
    
    # Set date axis ticks and text properties:
    date_range_indexes = np.linspace(0, len(axis_date) - 1, num=7, dtype=int)
    ax1.set_xticks(date_range_indexes[0::])
    ax1.set_xticklabels([axis_date[i] for i in date_range_indexes], rotation=10, ha='center')
    plt.setp(ax1.get_xticklabels(), rotation=10, ha='center')

    # Set axies ticks text color, font and size:
    ax1.tick_params(axis="x", labelcolor=plot_colors['date'])
    ax1.tick_params(axis="y", labelcolor=plot_colors['btc'])
    ax2.tick_params(axis="y", labelcolor=plot_colors['usd'])

    for label in ax1.get_xticklabels():
        label.set_fontproperties(plot_font)
        label.set_fontsize(12)

    for label in ax1.get_yticklabels() + ax2.get_yticklabels():
        label.set_fontproperties(plot_font)
        label.set_fontsize(18)

    for label in ax3.get_yticklabels():
        label.set_fontproperties(plot_font)
        label.set_fontsize(1)

    # Set axies order (higher value puts layer to the front):
    ax1.set_zorder(3)
    ax2.set_zorder(2)
    ax3.set_zorder(1)

    # Set plot and stacked area legend proxies:
    plot_legend_proxy_btc = Line2D([0], [0], label=f'Holdings, BTC')
    plot_legend_proxy_usd = Line2D([0], [0], label='Holdings, USD')
    plot_legend_list = [plot_legend_proxy_btc, plot_legend_proxy_usd]
    for issuer in issuers_df:
        issuer_percent = format_percentage(issuers_df[issuer].iloc[-1])[1:]
        plot_legend_issuer = Line2D([0], [0], label=f'{issuer_percent} {issuer}')
        plot_legend_list.insert(2, plot_legend_issuer)
        
    # Set actual plot and stacked area legend:
    plot_legend = ax1.legend(handles=plot_legend_list, loc="upper left", prop=plot_font, handlelength=0)
    
    # Set plot and stacked area legend colors:
    plot_legend.get_texts()[0].set_color(plot_colors['btc'])
    plot_legend.get_texts()[1].set_color(plot_colors['usd'])
    plot_legend.get_texts()[2].set_color(plot_colors['areas'][5])
    plot_legend.get_texts()[3].set_color(plot_colors['areas'][4])
    plot_legend.get_texts()[4].set_color(plot_colors['areas'][3])
    plot_legend.get_texts()[5].set_color(plot_colors['areas'][2])
    plot_legend.get_texts()[6].set_color(plot_colors['areas'][1])
    plot_legend.get_texts()[7].set_color(plot_colors['areas'][0])
    plot_legend.get_frame().set_facecolor(plot_colors['frame'])
    plot_legend.get_frame().set_alpha(0.75)

    # Set plot and stacked area legend text size:
    for text in plot_legend.get_texts():
        text.set_fontsize(16)

    # Open memory buffer and save plot to memory buffer:
    areas_buffer = io.BytesIO()
    plt.savefig(areas_buffer, format='png', bbox_inches='tight', transparent=True, dpi=150)
    matplotlib.pyplot.close()

    # Open background image, draw Lightning title and save image to memory buffer:
    title_image = Image.open(background_path)
    draw = ImageDraw.Draw(title_image)

    # Lightning title related variables:
    title_font = plot['font']
    title_list = [
            [{'text': 'hildobby @ Dune.com', 'position': background_colors['api'][1], 'font_size': 36, 'text_color': background_colors['api'][0]},
            {'text': 'BTC ETF issuers Marketshare', 'position': background_colors['api'][2], 'font_size': 25, 'text_color': background_colors['api'][0]},
             {'text': f'{chart_time_from}', 'position': background_colors['period'][1], 'font_size': 30, 'text_color': background_colors['period'][0]},
             {'text': f'{chart_time_till}', 'position': background_colors['period'][2], 'font_size': 30, 'text_color': background_colors['period'][0]}]
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

    # Overlay plot buffer with Lightning title buffer and save final image:
    background_image = Image.open(title_buffer).convert("RGB")
    title_buffer.seek(0)
    background_overlay = Image.open(areas_buffer)
    areas_buffer.seek(0)

    background_image.paste(background_overlay, background_coordinates, mask=background_overlay)
    background_image.save(plot_file, "JPEG", quality=90, icc_profile=background_image.info.get('icc_profile', ''))
    title_buffer.close()
    areas_buffer.close()
    
    main_logger.info(f'[image] etfs plot drawn')

    return plot_file


def write_etfs():
    
    # User configuration related variables:
    etfs_chart = config.charts['etfs']
    etfs_chart_file_path = etfs_chart['file']['path']
    etfs_chart_file_name = etfs_chart['file']['name']
    etfs_chart_file = etfs_chart_file_path + etfs_chart_file_name

    markdown_file = etfs_chart_file_path + 'etfs.md'

    network_snapshot = config.snapshots['network']
    network_snapshot_file_path = network_snapshot['file']['path']
    network_snapshot_file_name = network_snapshot['file']['name']
    network_snapshot_file = network_snapshot_file_path + network_snapshot_file_name
        
    # Create plot DataFrame:
    etfs_chart_df = pd.read_csv(etfs_chart_file)
    etfs_chart_df = etfs_chart_df.sort_values(by='time')

    holdings_btc_df = etfs_chart_df.groupby('time')['tvl'].sum().reset_index() # group items on time collumn and sum TVL for each date
    holdings_usd_df = etfs_chart_df.groupby('time')['usd_tvl'].sum().reset_index() # group items on time collumn and sum TVL for each date

    btc_df = holdings_btc_df['tvl']
    usd_df = holdings_usd_df['usd_tvl']

    now = len(holdings_btc_df) - 1

    LAST_UPDATE = holdings_btc_df['time'][now][:10]

    HOLDINGS_BTC_CURRENT = format_currency(btc_df[now], config.currency_crypto_ticker, decimal=2)
    HOLDINGS_BTC_1W = format_amount(btc_df[now] - btc_df[now - 7], config.currency_crypto_ticker)
    HOLDINGS_BTC_1W_PERCENTAGE = format_percentage(calculate_percentage_change(btc_df[now - 7], btc_df[now]))
    HOLDINGS_BTC_1M = format_amount(btc_df[now] - btc_df[now - 30], config.currency_crypto_ticker)
    HOLDINGS_BTC_1M_PERCENTAGE = format_percentage(calculate_percentage_change(btc_df[now - 30], btc_df[now]))

    with open (network_snapshot_file, 'r') as network_file:
        network_data = json.load(network_file)
        network_btc_supply = network_data['totalbc'] / 100_000_000
        SUPPLY_BTC_CURRENT = format_amount(network_btc_supply, config.currency_crypto_ticker)
        SUPPLY_BTC_CURRENT_PERCENTAGE = format_percentage(btc_df[now] / network_btc_supply * 100)[1:]

    HOLDINGS_USD_CURRENT = format_currency(usd_df[now], config.currency_vs_ticker, decimal=2)
    HOLDINGS_USD_1W = format_amount(usd_df[now] - usd_df[now - 7], config.currency_vs_ticker)
    HOLDINGS_USD_1W_PERCENTAGE = format_percentage(calculate_percentage_change(usd_df[now - 7], usd_df[now]))
    HOLDINGS_USD_1M = format_amount(usd_df[now] - usd_df[now - 30], config.currency_vs_ticker)
    HOLDINGS_USD_1M_PERCENTAGE = format_percentage(calculate_percentage_change(usd_df[now - 30], usd_df[now]))

    # Format text for user presentation:
    info_holdings = \
        f'BTC: {HOLDINGS_BTC_CURRENT}\n' \
        f'USD: {HOLDINGS_USD_CURRENT}\n' \
        f'{SUPPLY_BTC_CURRENT_PERCENTAGE} of {SUPPLY_BTC_CURRENT} mined\n'
    info_holdings_btc = \
        f'BTC 1w: {HOLDINGS_BTC_1W_PERCENTAGE} ({HOLDINGS_BTC_1W})\n' \
        f'BTC 1m: {HOLDINGS_BTC_1M_PERCENTAGE} ({HOLDINGS_BTC_1M})\n'
    info_holdings_usd = \
        f'USD 1w: {HOLDINGS_USD_1W_PERCENTAGE} ({HOLDINGS_USD_1W})\n' \
        f'USD 1m: {HOLDINGS_USD_1M_PERCENTAGE} ({HOLDINGS_USD_1M})\n' 
    info_update = f'Last update at {LAST_UPDATE}\n'
    Info_links = f'[Source & Additional Stats](https://dune.com/hildobby/btc-etfs)'
    
    # Write text to Markdown file:
    with open (markdown_file, 'w') as markdown:
        markdown.write(f'```ETFs\n{info_holdings}\n{info_holdings_btc}\n{info_holdings_usd}\n{info_update}```{Info_links}')
    
    main_logger.info(f'[markdown] etfs text written')

    return markdown_file




if __name__ == '__main__':
    draw_etfs()
    write_etfs()