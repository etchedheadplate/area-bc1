import io
import os
import json
from datetime import datetime, timezone

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

import config
from logger import main_logger
from tools import (define_key_metric_movement,
                   calculate_percentage_change,
                   format_time_axis,
                   format_amount,
                   convert_timestamp_to_utc,
                   format_utc,
                   format_currency,
                   format_percentage)




'''
Functions related to creation of plot and markdown files for Market database.

Plot based on chart values and made for whole number of days. 24h plot based on 5
minutes data chunks, up to 90 days on 1 hour data chunks, all other on 1 day data
chunks. Dates period based on API endpoint specified in user configuration and can
be set manually by user. Background image depends on % of BTC price change (positive
or negative). Axies have automatic appropriate scaling to different dates periods.

Markdown based on snapshot and chart values and formatted for user presentation.
'''



def select_chart(days=1):
    # Selects chart based on days period. Due to history Markdowns being generated
    # on daily basis additional return is introduced. It skips 90 days chart because
    # of it's 1-hour interval, max days chart used instead.
    
    if isinstance(days, int):
        days = int(days)
        if days <= 1:
            chart = 'market'
            chart_for_markdown = chart
        elif days <= 90:
            chart = 'market_days_90'
            chart_for_markdown = 'market_days_max'
        else:
            chart = 'market_days_max'
            chart_for_markdown = chart
    else:
        chart = 'market_days_max'
        chart_for_markdown = chart
    
    return chart, chart_for_markdown


def calculate_rows_interval(days=1):
    # Calculates interval between chart rows for correct mapping of values to plot axies.
    
    # 1 hour and 1 day chunks corrected due to overlap between 90 and max days charts:
    if isinstance(days, int):
        if days <= 1:
            days_as_five_minutes_chunks = days * 288
            interval = days_as_five_minutes_chunks
        elif days <= 90:
            days_as_one_hour_chunks = days * 24 - 1
            interval = days_as_one_hour_chunks
        else:
            days_as_one_day_chunks = days * 1 + 1
            interval = days_as_one_day_chunks
    else:
        days_as_one_day_chunks = days * 1 + 1
        interval = days_as_one_day_chunks
    
    return interval


def draw_market(days=1):
    # Draws Market plot with properties specified in user configuration.
    
    chart_name = select_chart(days)[0]

    # User configuration related variables:
    chart = config.charts[f'{chart_name}']
    chart_file_path = chart['file']['path']
    chart_file_name = chart['file']['name']
    chart_file = chart_file_path + chart_file_name

    # Plot-related variables:
    plot = config.images['market']
    plot_font = font_manager.FontProperties(fname=plot['font'])
    plot_colors = plot['colors']
    plot_background = plot['backgrounds']
    
    if days == 1:
        plot_output = plot['path'] + 'market.jpg'
    else:
        plot_output = plot['path'] + f'market_days_{days}.jpg'
    
    # Creation of plot DataFrame:
    plot_df = pd.read_csv(chart_file)

    if days == 'max':
        days = len(plot_df) - 2

    chart_time_till = datetime.utcfromtimestamp(os.path.getctime(chart_file)).strftime('%Y-%m-%d')
    chart_time_from = (datetime.utcfromtimestamp(os.path.getctime(chart_file)) - timedelta(days=days)).strftime('%Y-%m-%d')
    if chart_time_from < '2013-04-28':
        chart_time_from = '2013-04-28'

    # Specification of chart indexes for plot axies:
    chart_interval = calculate_rows_interval(days)
    plot_index_last = len(plot_df) - 1
    plot_index_first = plot_index_last - chart_interval
    if plot_index_first < 1:
        plot_index_first = 1

    # Key metric related variables for percentage change calculation:
    plot_key_metric = 'price'
    plot_key_metric_new = plot_df[plot_key_metric][plot_index_last]
    plot_key_metric_old = plot_df[plot_key_metric][plot_index_first]
    plot_key_metric_movement = calculate_percentage_change(plot_key_metric_old, plot_key_metric_new)
    plot_key_metric_movement_format = format_percentage(plot_key_metric_movement)

    # Background-related variables:
    background = define_key_metric_movement(plot, plot_key_metric_movement)
    background_path = plot_background[f'{background}']['path']
    background_coordinates = plot_background[f'{background}']['coordinates']
    background_colors = plot_background[f'{background}']['colors']

    # Creation of plot axies:
    axis_date = plot_df['date'][plot_index_first:plot_index_last]
    axis_price = plot_df['price'][plot_index_first:plot_index_last]
    axis_total_volume = plot_df['total_volume'][plot_index_first:plot_index_last]

    # Creation of plot figure:
    fig, ax1 = plt.subplots(figsize=(12, 7.4))
    fig.patch.set_alpha(0.0)
    fig.patch.set_facecolor('none')
    ax1.grid(True, linestyle="dashed", linewidth=0.5, alpha=0.7)
    ax2 = ax1.twinx()

    # Set axies lines:    
    ax1.plot(axis_date, axis_price, color=plot_colors['price'], label="price", linewidth=8)
    ax2.plot(axis_date, axis_total_volume, color=plot_colors['total_volume'], label="total_volume", alpha=0.3, linewidth=0.1)

    # Set axies left and right borders to first and last date of period. Bottom border
    # is set to min total_volume value and 99% of min price value for better scaling.
    ax1.set_xlim(axis_date.iloc[0], axis_date.iloc[-1])  
    ax1.set_ylim(min(axis_price) * 0.99, max(axis_price) * 1.01)
    ax2.set_ylim(min(axis_total_volume), max(axis_total_volume) * 1.05)

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
    ax1.tick_params(axis="y", labelcolor=plot_colors['price'])
    ax2.tick_params(axis="y", labelcolor=plot_colors['total_volume'])

    for label in ax1.get_xticklabels():
        label.set_fontproperties(plot_font)
        label.set_fontsize(12)

    for label in ax1.get_yticklabels() + ax2.get_yticklabels():
        label.set_fontproperties(plot_font)
        label.set_fontsize(18)

    # Set axies order (higher value puts layer to the front):
    ax1.set_zorder(2)
    ax2.set_zorder(1)
    
    # Set axies color filling:
    ax2.fill_between(axis_date, axis_total_volume, color=plot_colors['total_volume'], alpha=0.8)

    # Set plot legend proxies and actual legend:
    legend_proxy_price = Line2D([0], [0], label=f'Price, {config.currency_vs_ticker}')
    legend_proxy_volume = Line2D([0], [0], label=f'Volume, {config.currency_vs_ticker}')
    legend = ax1.legend(handles=[legend_proxy_price, legend_proxy_volume], loc="upper left", prop=plot_font, handlelength=0)
    
    # Set legend colors:
    legend.get_texts()[0].set_color(plot_colors['price'])
    legend.get_texts()[1].set_color(plot_colors['total_volume'])
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

    # Market title related variables:
    title_font = plot['font']
    title_list = [
            [{'text': 'coingecko.com', 'position': background_colors['api'][1], 'font_size': 36, 'text_color': background_colors['api'][0]},
            {'text': f'{config.currency_pair} market trade', 'position': background_colors['api'][2], 'font_size': 25, 'text_color': background_colors['api'][0]}],

            [{'text': f'{config.currency_crypto_ticker} {plot_key_metric} {plot_key_metric_movement_format}', 'position': background_colors['metric'][1], 'font_size': 36, 'text_color': background_colors['metric'][0]},
            {'text': f'{chart_time_from} - {chart_time_till}', 'position': background_colors['metric'][2], 'font_size': 24, 'text_color': background_colors['metric'][0]}]
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

    # Overlay plot buffer with Market title buffer and save final image:
    background_image = Image.open(title_buffer).convert("RGB")
    title_buffer.seek(0)
    background_overlay = Image.open(plot_buffer)
    plot_buffer.seek(0)

    background_image.paste(background_overlay, background_coordinates, mask=background_overlay)
    background_image.save(plot_output, "JPEG", quality=90, icc_profile=background_image.info.get('icc_profile', ''))
    title_buffer.close()
    plot_buffer.close()

    main_logger.info(f'[image] market (days {days}) plot drawn')


def write_market(days=1):
    # Writes Market markdown for user set days period with properties specified in user configuration.

    # User configuration related variables:
    snapshot = config.snapshots['market']
    snapshot_file_path = snapshot['file']['path']
    snapshot_file_name = snapshot['file']['name']
    snapshot_file = snapshot_file_path + snapshot_file_name

    if days == 1:
        markdown_file = snapshot_file_path + 'market.md'

        with open (snapshot_file, 'r') as json_file:
            snapshot_data = json.load(json_file)

            # Parse snapshot to separate values:
            LAST_UPdATED = format_utc(snapshot_data['last_updated'])

            PRICE_CURRENT = format_currency(snapshot_data['current_price'][f'{config.currency_vs}'], config.currency_vs_ticker)
            PRICE_CHANGE_PERCENTAGE_IN_CURRENCY_24H = format_percentage(snapshot_data['price_change_percentage_24h_in_currency'][f'{config.currency_vs}'])
            PRICE_CHANGE_24H_IN_CURRENCY = format_currency(snapshot_data['price_change_24h_in_currency'][f'{config.currency_vs}'], config.currency_vs_ticker)
            PRICE_HIGH_24H = format_currency(snapshot_data['high_24h'][f'{config.currency_vs}'], config.currency_vs_ticker)
            PRICE_LOW_24H = format_currency(snapshot_data['low_24h'][f'{config.currency_vs}'], config.currency_vs_ticker)
            
            MARKET_CAP = format_amount(snapshot_data['market_cap'][f'{config.currency_vs}'], config.currency_vs_ticker)
            MARKET_CAP_CHANGE_24H_PERCENTAGE = format_percentage(snapshot_data['market_cap_change_percentage_24h_in_currency'][f'{config.currency_vs}'])
            MARKET_CAP_CHANGE_24H = format_amount(snapshot_data['market_cap_change_24h_in_currency'][f'{config.currency_vs}'], config.currency_vs_ticker)
            FULLY_DILUTED_VALUATION = format_amount(snapshot_data['fully_diluted_valuation'][f'{config.currency_vs}'], config.currency_vs_ticker)
            
            ALL_TIME_HIGH = format_currency(snapshot_data['ath'][f'{config.currency_vs}'], config.currency_vs_ticker)
            ALL_TIME_HIGH_CHANGE_PERCENTAGE = format_percentage(snapshot_data['ath_change_percentage'][f'{config.currency_vs}'])
    #        ALL_TIME_HIGH_CHANGE = format_currency((snapshot_data['ath'][f'{config.currency_vs}'] - snapshot_data['SNAPSHOT_PRICE'][f'{config.currency_vs}']), config.currency_vs_ticker)
            ALL_TIME_HIGH_DATE = snapshot_data['ath_date'][f'{config.currency_vs}'][:10]    
            ALL_TIME_HIGH_DAYS = (datetime.now(timezone.utc) - datetime.fromisoformat(snapshot_data['ath_date'][f'{config.currency_vs}'].replace('Z', '+00:00'))).days

            TOTAL_VOLUME = format_amount(snapshot_data['total_volume'][f'{config.currency_vs}'], config.currency_vs_ticker)
    #        SUPPLY_TOTAL = format_amount(snapshot_data['total_supply'], config.currency_crypto_ticker)
            SUPPLY_CIRCULATING = format_currency(snapshot_data['circulating_supply'], config.currency_crypto_ticker, decimal=0)
        
            # Format text for user presentation:
            info_price = f'[Trade]\n' \
                f'Price: {PRICE_CURRENT}\n' \
                f'24h: {PRICE_CHANGE_PERCENTAGE_IN_CURRENCY_24H} ({PRICE_CHANGE_24H_IN_CURRENCY})\n' \
                f'24h High: {PRICE_HIGH_24H}\n' \
                f'24h Low: {PRICE_LOW_24H}\n' \
                f'Trade Volume: {TOTAL_VOLUME}\n'
            info_market_cap = f'[Capitalization]\n' \
                f'Market Cap: {MARKET_CAP}\n' \
                f'24h: {MARKET_CAP_CHANGE_24H_PERCENTAGE} ({MARKET_CAP_CHANGE_24H})\n' \
                f'Supply: {SUPPLY_CIRCULATING}\n' \
                f'Diluted: {FULLY_DILUTED_VALUATION}\n'
            info_ath = f'[All-Time-High]\n' \
                f'Price: {ALL_TIME_HIGH}\n' \
                f'{ALL_TIME_HIGH_DAYS}d: {ALL_TIME_HIGH_CHANGE_PERCENTAGE}\n' \
                f'Date: {ALL_TIME_HIGH_DATE}\n'
            info_update = f'UTC {LAST_UPdATED}\n'

            # Write text to Markdown file:
            with open (markdown_file, 'w') as markdown:
                markdown.write(f"```Market\n{info_price}\n{info_market_cap}\n{info_ath}\n{info_update}```")

    else:
        chart_name = select_chart(days)[1]

        # User configuration related variables:
        chart = config.charts[f'{chart_name}']
        chart_file_path = chart['file']['path']
        chart_file_name = chart['file']['name']
        chart_file = chart_file_path + chart_file_name
        chart_data = pd.read_csv(chart_file)

        chart_markdown_file = chart_file_path + f'market_days_{days}.md'

        if days == 'max':
            days = len(chart_data) - 1

        chart_data_index_last = len(chart_data)
        chart_data_index_first = chart_data_index_last - days
        if chart_data_index_first < 1:
            chart_data_index_first = 1

        chart_date = chart_data['date'][chart_data_index_first : chart_data_index_last]
        chart_price = chart_data['price'][chart_data_index_first : chart_data_index_last]
        chart_market_cap = chart_data['market_cap'][chart_data_index_first : chart_data_index_last]
        chart_total_volume = chart_data['total_volume'][chart_data_index_first : chart_data_index_last]

        with open (snapshot_file, 'r') as json_file:
            snapshot_data = json.load(json_file)

            # CoinGecko does not provide Volume information before 2013-12-27:
            if chart_data_index_first > 244:
                # Parse snapshot and chart to separate values:
                SNAPSHOT_DATE = format_utc(snapshot_data['last_updated'])[:-9]
                SNAPSHOT_PRICE = snapshot_data['current_price'][f'{config.currency_vs}']
                SNAPSHOT_MARKET_CAP = snapshot_data['market_cap'][f'{config.currency_vs}']
                SNAPSHOT_TOTAL_VOLUME = snapshot_data['total_volume'][f'{config.currency_vs}']

                CHART_DATE = convert_timestamp_to_utc(chart_date.iloc[0])[:-9]
                CHART_PRICE = chart_price.iloc[0]
                CHART_MARKET_CAP = chart_market_cap.iloc[0]
                CHART_TOTAL_VOLUME = chart_total_volume.iloc[0]

                CHANGE_PRICE = format_currency(SNAPSHOT_PRICE - CHART_PRICE, f'{config.currency_vs}', decimal=0)
                CHANGE_MARKET_CAP = format_amount(SNAPSHOT_MARKET_CAP - CHART_MARKET_CAP, f'{config.currency_vs}')
                CHANGE_TOTAL_VOLUME = format_amount(SNAPSHOT_TOTAL_VOLUME - CHART_TOTAL_VOLUME, f'{config.currency_vs}')

                PERCENTAGE_CHANGE_PRICE = format_percentage(calculate_percentage_change(CHART_PRICE, SNAPSHOT_PRICE))
                PERCENTAGE_CHANGE_MARKET_CAP = format_percentage(calculate_percentage_change(CHART_MARKET_CAP, SNAPSHOT_MARKET_CAP))
                PERCENTAGE_CHANGE_TOTAL_VOLUME = format_percentage(calculate_percentage_change(CHART_TOTAL_VOLUME, SNAPSHOT_TOTAL_VOLUME))

                HIGH_PRICE = format_currency(chart_price.max().max(), f'{config.currency_vs}', decimal=0)
                HIGH_MARKET_CAP = format_amount(chart_market_cap.max().max(), f'{config.currency_vs}')
                HIGH_TOTAL_VOLUME = format_amount(chart_total_volume.max().max(), f'{config.currency_vs}')

                DATE_HIGH_PRICE = convert_timestamp_to_utc(chart_date[chart_price.idxmax()])[:-9]
                DATE_HIGH_MARKET_CAP = convert_timestamp_to_utc(chart_date[chart_market_cap.idxmax()])[:-9]
                DATE_HIGH_TOTAL_VOLUME = convert_timestamp_to_utc(chart_date[chart_total_volume.idxmax()])[:-9]

                LOW_PRICE = format_currency(chart_price.min().min(), f'{config.currency_vs}', decimal=0)
                LOW_MARKET_CAP = format_amount(chart_market_cap.min().min(), f'{config.currency_vs}')
                LOW_TOTAL_VOLUME = format_amount(chart_total_volume.min().min(), f'{config.currency_vs}')

                DATE_LOW_PRICE = convert_timestamp_to_utc(chart_date[chart_price.idxmin()])[:-9]
                DATE_LOW_MARKET_CAP = convert_timestamp_to_utc(chart_date[chart_market_cap.idxmin()])[:-9]
                DATE_LOW_TOTAL_VOLUME = convert_timestamp_to_utc(chart_date[chart_total_volume.idxmin()])[:-9]

                SNAPSHOT_PRICE = format_currency(SNAPSHOT_PRICE, f'{config.currency_vs}', decimal=0)
                SNAPSHOT_MARKET_CAP = format_amount(SNAPSHOT_MARKET_CAP, f'{config.currency_vs}')
                SNAPSHOT_TOTAL_VOLUME = format_amount(SNAPSHOT_TOTAL_VOLUME, f'{config.currency_vs}')

                CHART_PRICE = format_currency(CHART_PRICE, f'{config.currency_vs}', decimal=0)
                CHART_MARKET_CAP = format_amount(CHART_MARKET_CAP, f'{config.currency_vs}')
                CHART_TOTAL_VOLUME = format_amount(CHART_TOTAL_VOLUME, f'{config.currency_vs}')
                
                # Format text for user presentation:
                info_period = f'{CHART_DATE} --> {SNAPSHOT_DATE}\n'
                info_price = f'[Price]\n' \
                    f'{CHART_PRICE} --> {SNAPSHOT_PRICE}\n' \
                    f'{days}d: {PERCENTAGE_CHANGE_PRICE} ({CHANGE_PRICE})\n' \
                    f'High: {HIGH_PRICE} ({DATE_HIGH_PRICE})\n' \
                    f'Low: {LOW_PRICE} ({DATE_LOW_PRICE})\n'
                info_total_volume = f'[Volume]\n' \
                    f'{CHART_TOTAL_VOLUME} --> {SNAPSHOT_TOTAL_VOLUME}\n' \
                    f'{days}d: {PERCENTAGE_CHANGE_TOTAL_VOLUME} ({CHANGE_TOTAL_VOLUME})\n' \
                    f'High: {HIGH_TOTAL_VOLUME} ({DATE_HIGH_TOTAL_VOLUME})\n' \
                    f'Low: {LOW_TOTAL_VOLUME} ({DATE_LOW_TOTAL_VOLUME})\n'
                info_market_cap = f'[Market-Cap]\n' \
                    f'{CHART_MARKET_CAP} --> {SNAPSHOT_MARKET_CAP}\n' \
                    f'{days}d: {PERCENTAGE_CHANGE_MARKET_CAP} ({CHANGE_MARKET_CAP})\n' \
                    f'High: {HIGH_MARKET_CAP} ({DATE_HIGH_MARKET_CAP})\n' \
                    f'Low: {LOW_MARKET_CAP} ({DATE_LOW_MARKET_CAP})\n'
                
                # Write text to Markdown file:
                with open (chart_markdown_file, 'w') as markdown:
                    markdown.write(f'```Market\n{info_period}\n{info_price}\n{info_total_volume}\n{info_market_cap}```')

            else:
                # Parse snapshot and chart to separate values:
                SNAPSHOT_DATE = format_utc(snapshot_data['last_updated'])[:-9]
                SNAPSHOT_PRICE = snapshot_data['current_price'][f'{config.currency_vs}']
                SNAPSHOT_MARKET_CAP = snapshot_data['market_cap'][f'{config.currency_vs}']
                SNAPSHOT_TOTAL_VOLUME = snapshot_data['total_volume'][f'{config.currency_vs}']

                CHART_DATE = convert_timestamp_to_utc(chart_date.iloc[0])[:-9]
                CHART_PRICE = chart_price.iloc[0]
                CHART_MARKET_CAP = chart_market_cap.iloc[0]
                CHART_TOTAL_VOLUME = 'Unknown'

                CHANGE_PRICE = format_currency(SNAPSHOT_PRICE - CHART_PRICE, f'{config.currency_vs}', decimal=0)
                CHANGE_MARKET_CAP = format_amount(SNAPSHOT_MARKET_CAP - CHART_MARKET_CAP, f'{config.currency_vs}')

                PERCENTAGE_CHANGE_PRICE = format_percentage(calculate_percentage_change(CHART_PRICE, SNAPSHOT_PRICE))
                PERCENTAGE_CHANGE_MARKET_CAP = format_percentage(calculate_percentage_change(CHART_MARKET_CAP, SNAPSHOT_MARKET_CAP))

                HIGH_PRICE = format_currency(chart_price.max().max(), f'{config.currency_vs}', decimal=0)
                HIGH_MARKET_CAP = format_amount(chart_market_cap.max().max(), f'{config.currency_vs}')
                HIGH_TOTAL_VOLUME = format_amount(chart_total_volume.max().max(), f'{config.currency_vs}')

                DATE_HIGH_PRICE = convert_timestamp_to_utc(chart_date[chart_price.idxmax()])[:-9]
                DATE_HIGH_MARKET_CAP = convert_timestamp_to_utc(chart_date[chart_market_cap.idxmax()])[:-9]
                DATE_HIGH_TOTAL_VOLUME = convert_timestamp_to_utc(chart_date[chart_total_volume.idxmax()])[:-9]

                LOW_PRICE = format_currency(chart_price.min().min(), f'{config.currency_vs}', decimal=0)
                LOW_MARKET_CAP = format_amount(chart_market_cap.min().min(), f'{config.currency_vs}')
                LOW_TOTAL_VOLUME = format_amount(chart_total_volume.min().min(), f'{config.currency_vs}')

                DATE_LOW_PRICE = convert_timestamp_to_utc(chart_date[chart_price.idxmin()])[:-9]
                DATE_LOW_MARKET_CAP = convert_timestamp_to_utc(chart_date[chart_market_cap.idxmin()])[:-9]
                DATE_LOW_TOTAL_VOLUME = convert_timestamp_to_utc(chart_date[chart_total_volume.idxmin()])[:-9]

                SNAPSHOT_PRICE = format_currency(SNAPSHOT_PRICE, f'{config.currency_vs}', decimal=0)
                SNAPSHOT_MARKET_CAP = format_amount(SNAPSHOT_MARKET_CAP, f'{config.currency_vs}')
                SNAPSHOT_TOTAL_VOLUME = format_amount(SNAPSHOT_TOTAL_VOLUME, f'{config.currency_vs}')

                CHART_PRICE = format_currency(CHART_PRICE, f'{config.currency_vs}', decimal=0)
                CHART_MARKET_CAP = format_amount(CHART_MARKET_CAP, f'{config.currency_vs}')
                
                # Format text for user presentation:
                info_period = f'{CHART_DATE} --> {SNAPSHOT_DATE}\n'
                info_price = f'[Price]\n' \
                    f'{CHART_PRICE} --> {SNAPSHOT_PRICE}\n' \
                    f'{days}d: {PERCENTAGE_CHANGE_PRICE} ({CHANGE_PRICE})\n' \
                    f'High: {HIGH_PRICE} ({DATE_HIGH_PRICE})\n' \
                    f'Low: {LOW_PRICE} ({DATE_LOW_PRICE})\n'
                info_total_volume = f'[Volume]\n' \
                    f'{CHART_TOTAL_VOLUME} --> {SNAPSHOT_TOTAL_VOLUME}\n' \
                    f'{days}d: Unknown\n' \
                    f'High: {HIGH_TOTAL_VOLUME} ({DATE_HIGH_TOTAL_VOLUME})\n' \
                    f'Low: Unknown\n'
                info_market_cap = f'[Market-Cap]\n' \
                    f'{CHART_MARKET_CAP} --> {SNAPSHOT_MARKET_CAP}\n' \
                    f'{days}d: {PERCENTAGE_CHANGE_MARKET_CAP} ({CHANGE_MARKET_CAP})\n' \
                    f'High: {HIGH_MARKET_CAP} ({DATE_HIGH_MARKET_CAP})\n' \
                    f'Low: {LOW_MARKET_CAP} ({DATE_LOW_MARKET_CAP})\n'
                info_limitations = 'CoinGecko API does not provide Volume information before 2013-12-27\n'

                # Write text to Markdown file:
                with open (chart_markdown_file, 'w') as markdown:
                    markdown.write(f'```Market\n{info_period}\n{info_price}\n{info_total_volume}\n{info_market_cap}\n{info_limitations}```')

    main_logger.info(f'[markdown] market (days {days}) text written')




if __name__ == '__main__':
    
    days = [1, 100]
    
    for day in days:
        draw_market(day)
        write_market(day)
