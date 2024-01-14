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
                   format_utc,
                   format_currency,
                   format_percentage)






def select_chart(days):
    # Selects chart based on days period. Used for updating charts, creation of
    # plots and history values. Due to history values being calculated on daily
    # basis additional return is introduced. It skips 90 days chart because of
    # it's 1-hour interval, which makes it useles in history values case.
    
    if isinstance(days, int):
        days = int(days)
        if days <= 1:
            chart = 'market_latest_chart'
            chart_for_history_values = chart
        elif days <= 90:
            chart = 'market_history_chart_days_90'
            chart_for_history_values = 'market_history_chart_days_max'
        else:
            chart = 'market_history_chart_days_max'
            chart_for_history_values = chart
    else:
        chart = 'market_history_chart_days_max'
        chart_for_history_values = chart
    
    return chart, chart_for_history_values






'''
Functions related to fetching market data from CoinGecko API and updating local
database at ./db/{currency_pair}/market/. Due to API rate limits all market data
stored localy as files which are used as source of data for plots and values.
All database files are updated regulary as specified in user configuration.
'''


def get_market_chart(days):
    # Creates chart path if it doesn't exists for selected chart. Creates empty
    # chart file with columns specified in user configuration. Fetches API data
    # from CoinGecko and distributes it to columns using 'Date' column as common
    # denominator. Updates chart with regularity specified in user configuration.

    chart_name = select_chart(days)[0]

    # User configuration related variables:
    chart = config.databases[f'{chart_name}']
    chart_api_base = chart['api']['base']
    chart_api_endpoint = chart['api']['endpoint']
    chart_api_params = chart['api']['params']
    chart_api_subdict = chart['api']['subdict']
    chart_file_path = chart['file']['path']
    chart_file_name = chart['file']['name']
    chart_file_columns = chart['file']['columns']
    chart_file = chart_file_path + chart_file_name
    chart_update_time = chart['update']['time']
    chart_update_interval = chart['update']['interval']

    # Create chart directory if it doesn' exists:
    if not os.path.isdir(chart_file_path):
        os.makedirs(chart_file_path, exist_ok=True)

    # Update chart, history plot and history values:
    while True:

        # Time-related variables formatted as specified in user configuration for correct calculation of update period:
        time_current = datetime.strptime(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
        time_update = datetime.strptime(str(time_current)[:-len(chart_update_time)] + chart_update_time, '%Y-%m-%d %H:%M:%S')

        # Empty DataFrame for later filling with response DataFrame:
        response_columns = pd.DataFrame({'Date': []})

        # Call to API and creation of DataFrame objects based on response data:
        response = get_api_data(
            chart_api_base,
            chart_api_endpoint,
            chart_api_params,
            chart_api_subdict)

        # Response data assigned to columns specified in user configuration
        for column, row in chart_file_columns.items():
            response_data = pd.DataFrame(response[row], columns=['Date', f'{column}'])
            response_columns = response_columns.merge(response_data, on='Date', how='outer')

        response_columns = response_columns.drop_duplicates('Date')
        
        # Filled with response data DataFrame saved to file:
        response_columns.to_csv(chart_file, index=False)
        print(time_current, f'[{chart_name}]', len(response_columns), f'entries added')
        
        # Make chart plot and history values data:
        write_history_values(days)
        print(time_current, f'[{chart_name}] values updated')
        make_plot(days)
        print(time_current, f'[{chart_name}] plot updated')
        
        # Schedule next update time. Check if current time > update time. If is, shift update time
        # by user configuration specified update interval untill update time > current time.
        while time_current > time_update:
            time_update = time_update + timedelta(hours=chart_update_interval)
        else:
            print(time_current, f'[{chart_name}] update planned to {time_update}')

        seconds_untill_upgrade = (time_update - time_current).total_seconds()

        # Update chart, history plot and history values with regularity specified in user configuration:
        time.sleep(seconds_untill_upgrade)


def get_market_latest_raw_values():
    # Fetches raw API data for latest values and saves it to database.
    # Updates JSON file with regularity specified in user configuration.

    latest_raw_values_name = 'market_latest_raw_values'

    # User configuration related variables:
    latest_raw_values = config.databases[f'{latest_raw_values_name}']
    latest_raw_values_api_base = latest_raw_values['api']['base']
    latest_raw_values_api_endpoint = latest_raw_values['api']['endpoint']
    latest_raw_values_api_params = latest_raw_values['api']['params']
    latest_raw_values_api_subdict = latest_raw_values['api']['subdict']
    latest_raw_values_file_path = latest_raw_values['file']['path']
    latest_raw_values_file_name = latest_raw_values['file']['name']
    latest_raw_values_file = latest_raw_values_file_path + latest_raw_values_file_name
    latest_raw_values_update_time = latest_raw_values['update']['time']
    latest_raw_values_update_interval = latest_raw_values['update']['interval']

    # Create directory for raw API data if it doesn' exists:
    if not os.path.isdir(latest_raw_values_file_path):
        os.makedirs(latest_raw_values_file_path, exist_ok=True)

    # Update raw API data for latest values:
    while True:

        # Time-related variables formatted as specified in user configuration for correct calculation of update period:
        time_current = datetime.strptime(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
        time_update = datetime.strptime(str(time_current)[:-len(latest_raw_values_update_time)] + latest_raw_values_update_time, '%Y-%m-%d %H:%M:%S')

        # Call to API and creation JSON file based on response data:
        response = get_api_data(
            latest_raw_values_api_base,
            latest_raw_values_api_endpoint,
            latest_raw_values_api_params,
            latest_raw_values_api_subdict)

        with open(latest_raw_values_file, 'w') as json_file:
            json.dump(response, json_file)
            print(time_current, f'[{latest_raw_values_name}] re-written')
        
        # Make latest values data
        write_latest_values()
        print(time_current, f'[{latest_raw_values_name}] values updated')
        
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
Functions related to creation of plots. Plots are based on interval of chart values
and made for whole number of days. Latest plot based on 5 minutes chunks, history
plots either on 1 hour or 1 day chunks. Plot's background depends on % of price
change in chart interval (positive or negative) as specified in user configuration.
Axies have automatic appropriate scaling to different plot periods.
'''


def calculate_rows_interval(days):
    # Calculates interval between chart rows for correct mapping of values to plot axies.
    
    # One hour and one day chunks corrected with due to overlap between 90 and max days
    # history charts in CoinGecko's API responses:
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


def make_plot(days):
    # Creates plot file with properties specified in user configuration.
    
    chart_name = select_chart(days)[0]

    # User configuration related variables:
    chart = config.databases[f'{chart_name}']
    chart_file_path = chart['file']['path']
    chart_file_name = chart['file']['name']
    chart_file = chart_file_path + chart_file_name

    # Plot-related variables:
    plot = config.plot['market']
    plot_font = font_manager.FontProperties(fname=plot['font'])
    plot_colors = plot['colors']
    plot_background = plot['backgrounds']
    
    if days == 1:
        plot_output = plot['path'] + 'latest/latest_plot.png'
    else:
        plot_output = plot['path'] + f'history/history_plot_days_{days}.png'
    
    # Creation of plot data frame:
    plot_df = pd.read_csv(chart_file)

    if days == 'max':
        days = len(plot_df) - 2

    # Specification of chart data indexes for plot axes:
    chart_interval = calculate_rows_interval(days)
    plot_index_last = len(plot_df) - 1
    plot_index_first = plot_index_last - chart_interval
    if plot_index_first < 1:
        plot_index_first = 1

    # Market data related variables for percentage change calculation:
    plot_key_metric = 'Price'
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
    # is set to min total volume value and 99% of min price value for better scaling
    ax1.set_xlim(axis_date.iloc[0], axis_date.iloc[-1])  
    ax1.set_ylim(min(axis_price) * 0.95, max(axis_price) * 0.95)
    ax2.set_ylim(min(axis_total_volume), max(axis_total_volume))

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
    legend_proxy_market = Line2D([0], [0], label=f'Market: {plot_key_metric_movement_format}')
    legend = ax1.legend(handles=[legend_proxy_price, legend_proxy_volume, legend_proxy_market], loc="upper left", prop=plot_font, handlelength=0)
    
    # Set legend colors
    legend.get_texts()[0].set_color(plot_colors['price'])
    legend.get_texts()[1].set_color(plot_colors['total_volume'])
    legend.get_texts()[2].set_color(plot_colors[f'{plot_key_metric_movement_color}'])
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

    latest_raw_values_name = 'market_latest_raw_values'

    # User configuration related variables:
    latest_raw_values = config.databases[f'{latest_raw_values_name}']
    latest_raw_values_file_path = latest_raw_values['file']['path']
    latest_raw_values_file_name = latest_raw_values['file']['name']
    latest_raw_values_file = latest_raw_values_file_path + latest_raw_values_file_name
    latest_values_file = latest_raw_values_file_path + 'latest_values.md'

    with open (latest_raw_values_file, 'r') as json_file:
        
        api_data = json.load(json_file)

        # Parse raw API data to separate values:
        LAST_UPDATED = format_utc(api_data['last_updated'])

        PRICE_CURRENT = format_currency(api_data['current_price'][f'{config.currency_vs}'], config.currency_vs_ticker)
        PRICE_CHANGE_PERCENTAGE_IN_CURRENCY_24H = format_percentage(api_data['price_change_percentage_24h_in_currency'][f'{config.currency_vs}'])
        PRICE_CHANGE_24H_IN_CURRENCY = format_currency(api_data['price_change_24h_in_currency'][f'{config.currency_vs}'], config.currency_vs_ticker)
        PRICE_HIGH_24H = format_currency(api_data['high_24h'][f'{config.currency_vs}'], config.currency_vs_ticker)
        PRICE_LOW_24H = format_currency(api_data['low_24h'][f'{config.currency_vs}'], config.currency_vs_ticker)
        
        MARKET_CAP = format_amount(api_data['market_cap'][f'{config.currency_vs}'], config.currency_vs_ticker)
        MARKET_CAP_CHANGE_24H_PERCENTAGE = format_percentage(api_data['market_cap_change_percentage_24h_in_currency'][f'{config.currency_vs}'])
        MARKET_CAP_CHANGE_24H = format_amount(api_data['market_cap_change_24h_in_currency'][f'{config.currency_vs}'], config.currency_vs_ticker)
        FULLY_DILUTED_VALUATION = format_amount(api_data['fully_diluted_valuation'][f'{config.currency_vs}'], config.currency_vs_ticker)
        
        ALL_TIME_HIGH_CHANGE_PERCENTAGE = format_percentage(api_data['ath_change_percentage'][f'{config.currency_vs}'])
        ALL_TIME_HIGH = format_currency(api_data['ath'][f'{config.currency_vs}'], config.currency_vs_ticker)
        ALL_TIME_HIGH_DATE = api_data['ath_date'][f'{config.currency_vs}'][:10]    
        
        TOTAL_TOTAL_VOLUMEUME = format_amount(api_data['total_volume'][f'{config.currency_vs}'], config.currency_vs_ticker)
#        SUPPLY_TOTAL = format_amount(api_data['total_supply'], config.currency_crypto_ticker)
        SUPPLY_CIRCULATING = format_amount(api_data['circulating_supply'], config.currency_crypto_ticker)
    
        # Format values text for user presentation:
        info_price = f'Price: {PRICE_CURRENT}\n' \
            f'24h % Change: {PRICE_CHANGE_PERCENTAGE_IN_CURRENCY_24H}\n' \
            f'24h Change: {PRICE_CHANGE_24H_IN_CURRENCY}\n' \
            f'24h High: {PRICE_HIGH_24H}\n' \
            f'24h Low: {PRICE_LOW_24H}\n' \
            f'24h Volume: {TOTAL_TOTAL_VOLUMEUME}\n'
        info_market_cap = f'Market Cap: {MARKET_CAP}\n' \
            f'24h % Change: {MARKET_CAP_CHANGE_24H_PERCENTAGE}\n' \
            f'24h Change: {MARKET_CAP_CHANGE_24H}\n' \
            f'Diluted: {FULLY_DILUTED_VALUATION}\n' \
            f'Supply: {SUPPLY_CIRCULATING}/21M\n'
        info_ath = f'ATH: {ALL_TIME_HIGH}\n' \
            f'% Change: {ALL_TIME_HIGH_CHANGE_PERCENTAGE}\n' \
            f'Date: {ALL_TIME_HIGH_DATE}\n'
        info_update = f'{LAST_UPDATED}\n'

        # Write latest values to Markdown file:
        with open (latest_values_file, 'w') as latest_values:
            latest_values.write(f"```\n{info_price}\n{info_market_cap}\n{info_ath}\n{info_update}\n```")


def write_history_values(days):
    # Parses raw API data and chart to separate values and generates Markdown file with history values.

    history_chart_name = select_chart(days)[1]

    # User configuration related variables:
    history_chart = config.databases[f'{history_chart_name}']
    history_chart_file_path = history_chart['file']['path']
    history_chart_file_name = history_chart['file']['name']
    history_chart_file = history_chart_file_path + history_chart_file_name
    history_chart_data = pd.read_csv(history_chart_file)

    history_values_path = history_chart_file_path
    history_values_file = history_values_path + f'history_values_days_{days}.md'

    if days == 'max':
        days = len(history_chart_data) - 1

    history_chart_data_index_last = len(history_chart_data)
    history_chart_data_index_first = history_chart_data_index_last - days
    if history_chart_data_index_first < 1:
        history_chart_data_index_first = 1

    history_date = history_chart_data['Date'][history_chart_data_index_first : history_chart_data_index_last]
    history_price = history_chart_data['Price'][history_chart_data_index_first : history_chart_data_index_last]
    history_market_cap = history_chart_data['Market Cap'][history_chart_data_index_first : history_chart_data_index_last]
    history_total_volume = history_chart_data['Total Volume'][history_chart_data_index_first : history_chart_data_index_last]

    latest_raw_values_name = 'market_latest_raw_values'
    latest_raw_values = config.databases[f'{latest_raw_values_name}']
    latest_raw_values_file_path = latest_raw_values['file']['path']
    latest_raw_values_file_name = latest_raw_values['file']['name']
    latest_raw_values_file = latest_raw_values_file_path + latest_raw_values_file_name

    with open (latest_raw_values_file, 'r') as json_file:
        
        data_current = json.load(json_file)

        # CoinGecko does not provide Volume information before 2013-12-27:
        if history_chart_data_index_first > 244:

            # Parse raw API data to separate values:
            CURRENT_DATE = format_utc(data_current['last_updated'])[:-9]
            CURRENT_PRICE = data_current['current_price'][f'{config.currency_vs}']
            CURRENT_MARKET_CAP = data_current['market_cap'][f'{config.currency_vs}']
            CURRENT_TOTAL_VOLUME = data_current['total_volume'][f'{config.currency_vs}']

            HISTORY_DATE = convert_timestamp_to_utc(history_date.iloc[0])[:-9]
            HISTORY_PRICE = history_price.iloc[0]
            HISTORY_MARKET_CAP = history_market_cap.iloc[0]
            HISTORY_TOTAL_VOLUME = history_total_volume.iloc[0]

            CHANGE_PRICE = format_currency(CURRENT_PRICE - HISTORY_PRICE, f'{config.currency_vs}', decimal=0)
            CHANGE_MARKET_CAP = format_amount(CURRENT_MARKET_CAP - HISTORY_MARKET_CAP, f'{config.currency_vs}')
            CHANGE_TOTAL_VOLUME = format_amount(CURRENT_TOTAL_VOLUME - HISTORY_TOTAL_VOLUME, f'{config.currency_vs}')

            PERCENTAGE_CHANGE_PRICE = format_percentage(calculate_percentage_change(HISTORY_PRICE, CURRENT_PRICE))
            PERCENTAGE_CHANGE_MARKET_CAP = format_percentage(calculate_percentage_change(HISTORY_MARKET_CAP, CURRENT_MARKET_CAP))
            PERCENTAGE_CHANGE_TOTAL_VOLUME = format_percentage(calculate_percentage_change(HISTORY_TOTAL_VOLUME, CURRENT_TOTAL_VOLUME))

            HIGH_PRICE = format_currency(history_price.max().max(), f'{config.currency_vs}', decimal=0)
            HIGH_MARKET_CAP = format_amount(history_market_cap.max().max(), f'{config.currency_vs}')
            HIGH_TOTAL_VOLUME = format_amount(history_total_volume.max().max(), f'{config.currency_vs}')

            DATE_HIGH_PRICE = convert_timestamp_to_utc(history_date[history_price.idxmax()])[:-9]
            DATE_HIGH_MARKET_CAP = convert_timestamp_to_utc(history_date[history_market_cap.idxmax()])[:-9]
            DATE_HIGH_TOTAL_VOLUME = convert_timestamp_to_utc(history_date[history_total_volume.idxmax()])[:-9]

            LOW_PRICE = format_currency(history_price.min().min(), f'{config.currency_vs}', decimal=0)
            LOW_MARKET_CAP = format_amount(history_market_cap.min().min(), f'{config.currency_vs}')
            LOW_TOTAL_VOLUME = format_amount(history_total_volume.min().min(), f'{config.currency_vs}')

            DATE_LOW_PRICE = convert_timestamp_to_utc(history_date[history_price.idxmin()])[:-9]
            DATE_LOW_MARKET_CAP = convert_timestamp_to_utc(history_date[history_market_cap.idxmin()])[:-9]
            DATE_LOW_TOTAL_VOLUME = convert_timestamp_to_utc(history_date[history_total_volume.idxmin()])[:-9]

            CURRENT_PRICE = format_currency(CURRENT_PRICE, f'{config.currency_vs}', decimal=0)
            CURRENT_MARKET_CAP = format_amount(CURRENT_MARKET_CAP, f'{config.currency_vs}')
            CURRENT_TOTAL_VOLUME = format_amount(CURRENT_TOTAL_VOLUME, f'{config.currency_vs}')

            HISTORY_PRICE = format_currency(HISTORY_PRICE, f'{config.currency_vs}', decimal=0)
            HISTORY_MARKET_CAP = format_amount(HISTORY_MARKET_CAP, f'{config.currency_vs}')
            HISTORY_TOTAL_VOLUME = format_amount(HISTORY_TOTAL_VOLUME, f'{config.currency_vs}')
            
            # Format values text for user presentation:
            info_period = f'{HISTORY_DATE} --> {CURRENT_DATE}\n'
            info_price = f'Price:\n' \
                f'{HISTORY_PRICE} --> {CURRENT_PRICE}\n' \
                f'Change: {PERCENTAGE_CHANGE_PRICE} ({CHANGE_PRICE})\n' \
                f'High: {HIGH_PRICE} ({DATE_HIGH_PRICE})\n' \
                f'Low: {LOW_PRICE} ({DATE_LOW_PRICE})\n'
            info_total_volume = f'Volume:\n' \
                f'{HISTORY_TOTAL_VOLUME} --> {CURRENT_TOTAL_VOLUME}\n' \
                f'Change: {PERCENTAGE_CHANGE_TOTAL_VOLUME} ({CHANGE_TOTAL_VOLUME})\n' \
                f'High: {HIGH_TOTAL_VOLUME} ({DATE_HIGH_TOTAL_VOLUME})\n' \
                f'Low: {LOW_TOTAL_VOLUME} ({DATE_LOW_TOTAL_VOLUME})\n'
            info_market_cap = f'Market Cap:\n' \
                f'{HISTORY_MARKET_CAP} --> {CURRENT_MARKET_CAP}\n' \
                f'Change: {PERCENTAGE_CHANGE_MARKET_CAP} ({CHANGE_MARKET_CAP})\n' \
                f'High: {HIGH_MARKET_CAP} ({DATE_HIGH_MARKET_CAP})\n' \
                f'Low: {LOW_MARKET_CAP} ({DATE_LOW_MARKET_CAP})\n'
            
            # Write latest values to Markdown file:
            with open (history_values_file, 'w') as latest_values:
                latest_values.write(f'```\n{info_period}\n{info_price}\n{info_total_volume}\n{info_market_cap}\n```')

        else:

            # Parse raw API data to separate values:
            CURRENT_DATE = format_utc(data_current['last_updated'])[:-9]
            CURRENT_PRICE = data_current['current_price'][f'{config.currency_vs}']
            CURRENT_MARKET_CAP = data_current['market_cap'][f'{config.currency_vs}']
            CURRENT_TOTAL_VOLUME = data_current['total_volume'][f'{config.currency_vs}']

            HISTORY_DATE = convert_timestamp_to_utc(history_date.iloc[0])[:-9]
            HISTORY_PRICE = history_price.iloc[0]
            HISTORY_MARKET_CAP = history_market_cap.iloc[0]
            HISTORY_TOTAL_VOLUME = 'Unknown'

            CHANGE_PRICE = format_currency(CURRENT_PRICE - HISTORY_PRICE, f'{config.currency_vs}', decimal=0)
            CHANGE_MARKET_CAP = format_amount(CURRENT_MARKET_CAP - HISTORY_MARKET_CAP, f'{config.currency_vs}')

            PERCENTAGE_CHANGE_PRICE = format_percentage(calculate_percentage_change(HISTORY_PRICE, CURRENT_PRICE))
            PERCENTAGE_CHANGE_MARKET_CAP = format_percentage(calculate_percentage_change(HISTORY_MARKET_CAP, CURRENT_MARKET_CAP))

            HIGH_PRICE = format_currency(history_price.max().max(), f'{config.currency_vs}', decimal=0)
            HIGH_MARKET_CAP = format_amount(history_market_cap.max().max(), f'{config.currency_vs}')
            HIGH_TOTAL_VOLUME = format_amount(history_total_volume.max().max(), f'{config.currency_vs}')

            DATE_HIGH_PRICE = convert_timestamp_to_utc(history_date[history_price.idxmax()])[:-9]
            DATE_HIGH_MARKET_CAP = convert_timestamp_to_utc(history_date[history_market_cap.idxmax()])[:-9]
            DATE_HIGH_TOTAL_VOLUME = convert_timestamp_to_utc(history_date[history_total_volume.idxmax()])[:-9]

            LOW_PRICE = format_currency(history_price.min().min(), f'{config.currency_vs}', decimal=0)
            LOW_MARKET_CAP = format_amount(history_market_cap.min().min(), f'{config.currency_vs}')
            LOW_TOTAL_VOLUME = format_amount(history_total_volume.min().min(), f'{config.currency_vs}')

            DATE_LOW_PRICE = convert_timestamp_to_utc(history_date[history_price.idxmin()])[:-9]
            DATE_LOW_MARKET_CAP = convert_timestamp_to_utc(history_date[history_market_cap.idxmin()])[:-9]
            DATE_LOW_TOTAL_VOLUME = convert_timestamp_to_utc(history_date[history_total_volume.idxmin()])[:-9]

            CURRENT_PRICE = format_currency(CURRENT_PRICE, f'{config.currency_vs}', decimal=0)
            CURRENT_MARKET_CAP = format_amount(CURRENT_MARKET_CAP, f'{config.currency_vs}')
            CURRENT_TOTAL_VOLUME = format_amount(CURRENT_TOTAL_VOLUME, f'{config.currency_vs}')

            HISTORY_PRICE = format_currency(HISTORY_PRICE, f'{config.currency_vs}', decimal=0)
            HISTORY_MARKET_CAP = format_amount(HISTORY_MARKET_CAP, f'{config.currency_vs}')
            
            # Format values text for user presentation:
            info_period = f'{HISTORY_DATE} --> {CURRENT_DATE}\n'
            info_price = f'Price:\n' \
                f'{HISTORY_PRICE} --> {CURRENT_PRICE}\n' \
                f'Change: {PERCENTAGE_CHANGE_PRICE} ({CHANGE_PRICE})\n' \
                f'High: {HIGH_PRICE} ({DATE_HIGH_PRICE})\n' \
                f'Low: {LOW_PRICE} ({DATE_LOW_PRICE})\n'
            info_total_volume = f'Volume:\n' \
                f'{HISTORY_TOTAL_VOLUME} --> {CURRENT_TOTAL_VOLUME}\n' \
                f'Change: Unknown\n' \
                f'High: {HIGH_TOTAL_VOLUME} ({DATE_HIGH_TOTAL_VOLUME})\n' \
                f'Low: Unknown\n'
            info_market_cap = f'Market Cap:\n' \
                f'{HISTORY_MARKET_CAP} --> {CURRENT_MARKET_CAP}\n' \
                f'Change: {PERCENTAGE_CHANGE_MARKET_CAP} ({CHANGE_MARKET_CAP})\n' \
                f'High: {HIGH_MARKET_CAP} ({DATE_HIGH_MARKET_CAP})\n' \
                f'Low: {LOW_MARKET_CAP} ({DATE_LOW_MARKET_CAP})\n'
            info_limitations = 'CoinGecko API does not\n' \
                'have Volume information\n'\
                'before 2013-12-27.\n' \

            # Write latest values to Markdown file:
            with open (history_values_file, 'w') as latest_values:
                latest_values.write(f'```\n{info_period}\n{info_price}\n{info_total_volume}\n{info_market_cap}\n{info_limitations}\n```')
