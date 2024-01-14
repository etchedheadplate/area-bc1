import io
import os
import time
import json
from datetime import datetime, timedelta

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
from tools import (get_api_data,
                   define_key_metric_movement,
                   calculate_percentage_change,
                   format_time_axis,
                   format_amount,
                   convert_timestamp_to_utc,
                   format_currency,
                   format_percentage,
                   format_quantity)






'''
Functions related to fetching blockchain data from Blockchain.com API and
updating local database at ./db/blockchain/. All blockchain data stored
localy as files which are used as source of data for plots and values.
All database files are updated regulary as specified in user configuration.
'''


def get_blockchain_chart():
    # Creates chart path if it doesn't exists for selected chart. Creates empty
    # chart file with columns specified in user configuration. Fetches API data
    # from Blockchain.com and distributes it to columns using 'Date' column as common
    # denominator. Updates chart with regularity specified in user configuration.

    # User configuration related variables:
    chart = config.databases['blockchain_history_chart']
    chart_api_base = chart['api']['base']
    chart_api_endpoint = chart['api']['endpoint']
    chart_api_params = chart['api']['params']
    chart_api_subdict = chart['api']['subdict']
    chart_file_path = chart['file']['path']
    chart_file_name = chart['file']['name']
    chart_columns = chart['file']['columns']
    chart_file = chart_file_path + chart_file_name
    chart_update_time = chart['update']['time']
    chart_update_interval = chart['update']['interval']

    # Create chart directory if it doesn' exists:
    if not os.path.isdir(chart_file_path):
        os.makedirs(chart_file_path, exist_ok=True)

    # Empty DataFrame for later filling with response DataFrame:
    response_columns = pd.DataFrame({'Date': []})

    for endpoint in chart_api_endpoint:
        
        # Time-related variables formatted as specified in user configuration for correct calculation of update period:
        time_current = datetime.strptime(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
        time_update = datetime.strptime(str(time_current)[:-len(chart_update_time)] + chart_update_time, '%Y-%m-%d %H:%M:%S')

        # Special variable to tie endpoint with column name:
        column_name_index = chart_api_endpoint.index(endpoint)

        # Call to API and creation of DataFrame objects based on response data:
        response = get_api_data(
            chart_api_base,
            endpoint,
            chart_api_params,
            chart_api_subdict)

        # Response data assigned to columns specified in user configuration
        response_data = pd.DataFrame(response).rename(columns={'x': 'Date', 'y': f'{chart_columns[column_name_index]}'})
        response_columns = response_columns.merge(response_data, on='Date', how='outer').dropna().sort_values(by='Date')
    
    # Filled with response data DataFrame saved to file:
    response_columns.to_csv(chart_file, index=False)


def get_blockchain_latest_raw_values():
    # Fetches raw API data for latest values and saves it to database.
    # Updates JSON file with regularity specified in user configuration.

    latest_raw_values_name = 'blockchain_latest_raw_values'

    # User configuration related variables:
    latest_raw_values = config.databases[f'{latest_raw_values_name}']
    latest_raw_values_api_base = latest_raw_values['api']['base']
    latest_raw_values_api_endpoint = latest_raw_values['api']['endpoint']
    latest_raw_values_file_path = latest_raw_values['file']['path']
    latest_raw_values_file_name = latest_raw_values['file']['name']
    latest_raw_values_file = latest_raw_values_file_path + latest_raw_values_file_name
    latest_raw_values_update_time = latest_raw_values['update']['time']
    latest_raw_values_update_interval = latest_raw_values['update']['interval']

    # Update raw API data for latest values:
    while True:

        # Time-related variables formatted as specified in user configuration for correct calculation of update period:
        time_current = datetime.strptime(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
        time_update = datetime.strptime(str(time_current)[:-len(latest_raw_values_update_time)] + latest_raw_values_update_time, '%Y-%m-%d %H:%M:%S')

        # Call to API and creation JSON file based on response data:
        response = get_api_data(
            latest_raw_values_api_base,
            latest_raw_values_api_endpoint)

        with open(latest_raw_values_file, 'w') as json_file:
            json.dump(response, json_file)
            print(time_current, f'[{latest_raw_values_name}] re-written')
        
        # Make latest values data
        write_latest_values()
        print(time_current, f'[{latest_raw_values_name}] values updated')
        make_plot()
        print(time_current, f'[{latest_raw_values_name}] plot updated')

        # Schedule next update time. Check if current time > update time. If is, shift update time
        # by user configuration specified update interval untill update time > current time.
        while time_current > time_update:
            time_update = time_update + timedelta(hours=latest_raw_values_update_interval)
        else:
            print(time_current, f'[{latest_raw_values_name}] update planned to {time_update}')

        seconds_untill_upgrade = (time_update - time_current).total_seconds()

        # Update JSON file and latest values with regularity specified in user configuration:
        time.sleep(seconds_untill_upgrade)






'''
Functions related to creation of plot. Plot based on interval of chart values
and made for whole number of days. Plot's background depends on % of cost per
transaction change in chart interval (positive or negative) as specified in user
configuration. Axies have automatic appropriate scaling to different plot periods.
'''


def make_plot():
    # Creates plot file with properties specified in user configuration.
    
    # User configuration related variables:
    chart = config.databases['blockchain_history_chart']
    chart_file_path = chart['file']['path']
    chart_file_name = chart['file']['name']
    chart_columns = chart['file']['columns']
    chart_file = chart_file_path + chart_file_name

    # Plot-related variables:
    plot = config.plot['blockchain']
    plot_font = font_manager.FontProperties(fname=plot['font'])
    plot_colors = plot['colors']
    plot_background = plot['backgrounds']
    plot_output = plot['path'] + 'history_plot.png'
        
    # Creation of plot data frame:
    plot_df = pd.read_csv(chart_file)

    days = len(plot_df) - 1

    # Specification of chart data indexes for plot axes:
    plot_index_last = len(plot_df) - 1
    plot_index_first = plot_index_last - days
    if plot_index_first < 1:
        plot_index_first = 1

    # Blockchain data related variables for percentage change calculation:
    plot_key_metric = 'TRX Cost'
    plot_key_metric_new = plot_df[plot_key_metric][plot_index_last]
    plot_key_metric_old = plot_df[plot_key_metric][plot_index_first]
    plot_key_metric_movement = calculate_percentage_change(plot_key_metric_old, plot_key_metric_new)
    plot_key_metric_movement_format = format_percentage(plot_key_metric_movement)
    plot_key_metric_movement_color = define_key_metric_movement(plot, plot_key_metric_movement)

    # Background-related variables:
    background = define_key_metric_movement(plot, plot_key_metric_movement)
    background_path = plot_background[f'{background}']['path']
    background_coordinates = plot_background[f'{background}']['coordinates']

    # Creation of plot axies:
    axis_date = plot_df['Date'][plot_index_first:plot_index_last]
    axis_trx_cost = plot_df['TRX Cost'][plot_index_first:plot_index_last]
    axis_hashrate = plot_df['Hashrate'][plot_index_first:plot_index_last]
    axis_price = plot_df['Price'][plot_index_first:plot_index_last]

    # Creation of plot figure:
    fig, ax1 = plt.subplots(figsize=(12, 7.4))
    fig.patch.set_alpha(0.0)
    fig.patch.set_facecolor('none')
    ax1.grid(True, linestyle="dashed", linewidth=0.5, alpha=0.7)
    ax2 = ax1.twinx()
    ax3 = ax1.twinx()

    # Set axies lines:    
    ax1.plot(axis_date, axis_trx_cost, color=plot_colors['trx_cost'], label="TRX Cost", linewidth=5)
    ax2.plot(axis_date, axis_hashrate, color=plot_colors['hashrate'], label="Hashrate", linewidth=2)
    ax3.plot(axis_date, axis_price, color=plot_colors['price'], label="Price", alpha=0.15, linewidth=0.1)

    # Set axies left and right borders to first and last date of period. Bottom border
    # is set to 95% of plot values for better scaling
    ax1.set_xlim(axis_date.iloc[0], axis_date.iloc[-1])  
    ax1.set_ylim(min(axis_trx_cost) * 0.95)
    ax2.set_ylim(min(axis_hashrate) * 0.95)
    ax3.set_ylim(min(axis_price) * 0.95)

    # Set axies text format:
    ax1.xaxis.set_major_formatter(FuncFormatter(lambda x, _: format_time_axis(x, days)))
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, _: format_amount(x)))
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, _: format_amount(x)))
    
    # Set date axis ticks and text properties:
    axis_date_ticks_positions = np.linspace(axis_date.iloc[0], axis_date.iloc[-1], num=6) 
    ax1.set_xticks(axis_date_ticks_positions)
    plt.setp(ax1.get_xticklabels(), rotation=10, ha='center')

    # Set axies ticks text color and font:
    ax1.tick_params(axis="x", labelcolor=plot_colors['date'])
    ax1.tick_params(axis="y", labelcolor=plot_colors['trx_cost'])
    ax2.tick_params(axis="y", labelcolor=plot_colors['hashrate'])

    # Set axies ticks text size:
    for label in ax1.get_xticklabels() + ax1.get_yticklabels() + ax2.get_yticklabels():
        label.set_fontproperties(plot_font)
        label.set_fontsize(14)

    # Set axies order (higher value puts layer to the front):
    ax1.set_zorder(3)
    ax2.set_zorder(2)
    ax3.set_zorder(1)
    
    # Set axies color filling:
    ax3.fill_between(axis_date, axis_price, color=plot_colors['price'], alpha=0.3)

    # Set plot legend proxies and actual legend:
    legend_proxy_trx_cost = Line2D([0], [0], label=f'TRX Cost, {config.currency_vs_ticker}')
    legend_proxy_hashrate = Line2D([0], [0], label='Hashrate, TH/s')
    legend_proxy_price = Line2D([0], [0], label=f'Price, {config.currency_vs_ticker}')
    legend_proxy_hashrate_change = Line2D([0], [0], label=f'TRX Cost {plot_key_metric_movement_format}')
    legend = ax2.legend(handles=[legend_proxy_trx_cost, legend_proxy_hashrate, legend_proxy_price, legend_proxy_hashrate_change], loc="upper left", prop=plot_font, handlelength=0)
    
    # Set legend colors
    legend.get_texts()[0].set_color(plot_colors['trx_cost'])
    legend.get_texts()[1].set_color(plot_colors['hashrate'])
    legend.get_texts()[2].set_color(plot_colors['price'])
    legend.get_texts()[3].set_color(plot_colors[f'{plot_key_metric_movement_color}'])
    legend.get_frame().set_facecolor(plot_colors['frame'])
    legend.get_frame().set_alpha(0.7)

    # Set legend text size
    for text in legend.get_texts():
        text.set_fontsize(12)

    # Save plot image without background in memory buffer and transfer it to PIL.Image module:
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight', transparent=True, dpi=150)
    matplotlib.pyplot.close()
    background_image = Image.open(background_path).convert("RGB")
    buffer.seek(0)
    background_overlay = Image.open(buffer)

    # Save plot image with background:
    background_image.paste(background_overlay, background_coordinates, mask=background_overlay)
    background_image.save(plot_output, "PNG", quality=100, icc_profile=background_image.info.get('icc_profile', ''))
    buffer.close()






'''
Functions related to creation of values. Values parsed from raw API data and
chart. Resulting separate values combined to text for user presentation and
saved as Markdown files in database.
'''


def write_latest_values():
    # Parses raw API data to separate values and generates Markdown file with latest values.

    latest_raw_values_name = 'blockchain_latest_raw_values'

    # User configuration related variables:
    latest_raw_values = config.databases[f'{latest_raw_values_name}']
    latest_raw_values_file_path = latest_raw_values['file']['path']
    latest_raw_values_file_name = latest_raw_values['file']['name']
    latest_raw_values_file = latest_raw_values_file_path + latest_raw_values_file_name
    latest_values_file = latest_raw_values_file_path + 'latest_values.md'

    history_chart = config.databases['blockchain_history_chart']
    history_chart_file_path = history_chart['file']['path']
    history_chart_file_name = history_chart['file']['name']
    history_chart_file = history_chart_file_path + history_chart_file_name
    history_chart_data = pd.read_csv(history_chart_file)

    with open (latest_raw_values_file, 'r') as json_file:
        
        api_data = json.load(json_file)

        # Parse raw API data to separate values:
        LAST_UPDATED = convert_timestamp_to_utc(api_data['timestamp'])

        BLOCKS_HEIGHT = format_quantity(api_data['n_blocks_total'])
        BLOCKS_MINED = format_quantity(api_data['n_blocks_mined'])
        BLOCKS_SIZE = round(api_data['blocks_size'] / (1_024**2) / int(BLOCKS_MINED), 4)
        BLOCKS_MINUTES = round(api_data['minutes_between_blocks'], 1)

        BTC_SUPPLY = format_currency(api_data['totalbc'] / 100_000_000, config.currency_crypto_ticker)
        BTC_MINED = format_currency(api_data['n_btc_mined'] / 100_000_000, config.currency_crypto_ticker)
        BTC_SENT = format_currency(api_data['total_btc_sent'] / 100_000_000, config.currency_crypto_ticker)
        BTC_PRICE = format_currency(api_data['market_price_usd'], config.currency_vs_ticker)

        TRANSACTIONS_MADE = format_quantity(api_data['n_tx'])
        TRANSACTIONS_COST = format_currency(history_chart_data['TRX Cost'].iloc[-1], config.currency_vs_ticker)

        HASHRATE = format_amount(api_data['hash_rate'] / 1_000)
        DIFFICULTY = format_amount(api_data['difficulty'])
        RETARGET_HEIGHT = format_quantity(api_data['nextretarget'])
    
        # Format values text for user presentation:
        info_blocks = f'Block Height: {BLOCKS_HEIGHT}\n' \
            f'24h Mined: {BLOCKS_MINED} blocks\n' \
            f'24h Size: {BLOCKS_SIZE} MB\n' \
            f'24h Time: {BLOCKS_MINUTES} minutes\n'
        info_coin = f'BTC: {BTC_SUPPLY}\n' \
            f'24h Mined: {BTC_MINED}\n' \
            f'24h Sent: {BTC_SENT}\n' \
            f'24h Price: {BTC_PRICE}\n'
        info_transactions = f'24h TRXs: {TRANSACTIONS_MADE}\n' \
            f'24h TRX Cost: {TRANSACTIONS_COST}\n'
        info_network = f'Hashrate: {HASHRATE} TH/s\n' \
            f'Difficulty: {DIFFICULTY}\n' \
            f'Change Height: {RETARGET_HEIGHT}\n'
        info_update = f'{LAST_UPDATED}\n'

        # Write latest values to Markdown file:
        with open (latest_values_file, 'w') as latest_values:
            latest_values.write(f"```\n{info_blocks}\n{info_coin}\n{info_transactions}\n{info_network}\n{info_update}\n```")