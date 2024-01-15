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
                   format_utc,
                   format_currency,
                   format_percentage,
                   format_quantity)






'''
Functions related to fetching lightning data from Mempool Space API and updating
local database at ./db/lightning/. All lightning data stored localy as files which
are used as source of data for plots and values. All database files are updated
regulary as specified in user configuration.
'''


def get_lightning_chart():
    # Creates chart path if it doesn't exists. Fetches API data from Mempool Space
    # and distributes it to columns using 'Date' column as common denominator.
    # Updates chart with regularity specified in user configuration.

    chart_name = 'lightning_history_chart'

    # User configuration related variables:
    chart = config.databases[f'{chart_name}']
    chart_api_base = chart['api']['base']
    chart_api_endpoint = chart['api']['endpoint']
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
        
    # Time-related variables formatted as specified in user configuration for correct calculation of update period:
    time_current = datetime.strptime(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
    time_update = datetime.strptime(str(time_current)[:-len(chart_update_time)] + chart_update_time, '%Y-%m-%d %H:%M:%S')

    # Call to API and creation of DataFrame objects based on response data:
    response = get_api_data(
        chart_api_base,
        chart_api_endpoint)

    # Response data assigned to columns specified in user configuration
    response_data = pd.DataFrame(response).rename(columns={'added': 'Date',
                                                           'channel_count': 'Channel Count',
                                                           'total_capacity': 'Total Capacity',
                                                           'tor_nodes': 'Nodes Tor',
                                                           'clearnet_nodes': 'Nodes Clearnet',
                                                           'unannounced_nodes': 'Nodes Unannounced',
                                                           'clearnet_tor_nodes': 'Nodes Clearnet Tor'})
    response_columns = response_columns.merge(response_data, on='Date', how='outer').dropna().sort_values(by='Date')
    
    # Additional column calculated from response columns values:
    response_columns['Nodes Total'] = (response_columns['Nodes Tor'] +
                                       response_columns['Nodes Clearnet'] +
                                       response_columns['Nodes Unannounced'] +
                                       response_columns['Nodes Clearnet Tor']) 
    
    # DataFrame with response data and additional columns saved to file:
    response_columns.to_csv(chart_file, index=False)
    print(time_current, f'[{chart_name}]', len(response_columns), f'entries added')

    # Write latest values data and make history plot:
    make_plot()
    print(time_current, f'[{chart_name}] plot updated')

    # Schedule next update time. Check if current time > update time. If is, shift update time
    # by user configuration specified update interval untill update time > current time.
    while time_current > time_update:
        time_update = time_update + timedelta(hours=chart_update_interval)
    else:
        print(time_current, f'[{chart_name}] update planned to {time_update}')

    seconds_untill_upgrade = (time_update - time_current).total_seconds()

    # Update chart with regularity specified in user configuration:
    time.sleep(seconds_untill_upgrade)


def get_lightning_latest_raw_values():
    # Fetches raw API data for latest values and saves it to database.
    # Updates JSON file with regularity specified in user configuration.

    latest_raw_values_name = 'lightning_latest_raw_values'

    # User configuration related variables:
    latest_raw_values = config.databases[f'{latest_raw_values_name}']
    latest_raw_values_api_base = latest_raw_values['api']['base']
    latest_raw_values_api_endpoint = latest_raw_values['api']['endpoint']
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
            latest_raw_values_api_endpoint)

        with open(latest_raw_values_file, 'w') as json_file:
            json.dump(response, json_file)
            print(time_current, f'[{latest_raw_values_name}] re-written')
        
        # Write latest values data:
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
Functions related to creation of plot. Plot based on interval of chart values
and made for whole number of days. Plot's background depends on % of cost per
transaction change in chart interval (positive or negative) as specified in user
configuration. Axies have automatic appropriate scaling to different plot periods.
'''


def make_plot():
    # Creates plot file with properties specified in user configuration.
    
    # User configuration related variables:
    chart = config.databases['lightning_history_chart']
    chart_file_path = chart['file']['path']
    chart_file_name = chart['file']['name']
    chart_columns = chart['file']['columns']
    chart_file = chart_file_path + chart_file_name

    # Plot-related variables:
    plot = config.plot['lightning']
    plot_font = font_manager.FontProperties(fname=plot['font'])
    plot_colors = plot['colors']
    plot_background = plot['backgrounds']
    plot_output = plot['path'] + 'history_plot.png'
        
    # Creation of plot data frame:
    plot_df = pd.read_csv(chart_file)

#    # If channel count = 0 whole row dissmissed (anomaly handling):
#    plot_df = plot_df[plot_df['Channel Count'] != 0]
    
    days = len(plot_df)

    # Specification of chart data indexes for plot axes:
    plot_index_last = len(plot_df)
    plot_index_first = 0

    # Market data related variables for percentage change calculation:
    plot_key_metric = 'Total Capacity'
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
    axis_date = plot_df['Date']
    axis_channel_count = plot_df['Channel Count']
    axis_total_capacity = plot_df['Total Capacity']

    # Creation of plot stacked area:
    stacked_nodes = plot_df[['Nodes Unannounced',
                            'Nodes Tor',
                            'Nodes Clearnet Tor',
                            'Nodes Clearnet']]

    # Stacked area normalized for 100%:
    stacked_nodes_percentages = stacked_nodes.divide(stacked_nodes.sum(axis=1), axis=0) * 100
    
    # Creation of plot figure:
    fig, ax1 = plt.subplots(figsize=(12, 7.4))
    fig.patch.set_alpha(0.0)
    fig.patch.set_facecolor('none')
    ax1.grid(True, linestyle="dashed", linewidth=0.5, alpha=0.7)
    ax2 = ax1.twinx()
    ax3 = ax1.twinx()

    # Set axies lines:    
    ax1.plot(axis_date, axis_total_capacity, color=plot_colors['total_capacity'], label="Total Capacity", linewidth=10)
    ax2.plot(axis_date, axis_channel_count, color=plot_colors['channel_count'], label="Channel Count", linewidth=6)

    # Set stacked area colors:
    stacked_nodes_colors = [plot_colors['nodes_unannounced'],
                            plot_colors['nodes_tor'],
                            plot_colors['nodes_clearnet_tor'],
                            plot_colors['nodes_clearnet']]
    ax3.stackplot(axis_date, stacked_nodes_percentages.T, colors=stacked_nodes_colors)

    # Set axies borders for better scaling:
    ax1.set_xlim(axis_date.iloc[0], axis_date.iloc[-1])  
    ax1.set_ylim(min(axis_total_capacity) * 0.995, max(axis_total_capacity) * 1.005)
    ax2.set_ylim(min(axis_channel_count) * 0.995, max(axis_channel_count) * 1.005)

    # Set axies text format:
    ax1.xaxis.set_major_formatter(FuncFormatter(lambda x, _: format_time_axis(x, days)))
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, _: format_amount(x / 100_000_000)))
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, _: format_amount(x)))
    
    # Set date axis ticks and text properties:
    axis_date_ticks_positions = np.linspace(axis_date.iloc[0], axis_date.iloc[-1], num=7) 
    ax1.set_xticks(axis_date_ticks_positions)
    plt.setp(ax1.get_xticklabels(), rotation=10, ha='center')

    # Set axies ticks text color and font:
    ax1.tick_params(axis="x", labelcolor=plot_colors['date'])
    ax1.tick_params(axis="y", labelcolor=plot_colors['total_capacity'])
    ax2.tick_params(axis="y", labelcolor=plot_colors['channel_count'])

    # Set axies ticks text size:
    for label in ax1.get_xticklabels() + ax1.get_yticklabels() + ax2.get_yticklabels():
        label.set_fontproperties(plot_font)
        label.set_fontsize(14)

    # Set axies order (higher value puts layer to the front):
    ax1.set_zorder(3)
    ax2.set_zorder(2)
    ax3.set_zorder(1)

    # Set plot and stacked area legend proxies:
    plot_legend_proxy_channel_count = Line2D([0], [0], label='Channels')
    plot_legend_proxy_total_capacity = Line2D([0], [0], label=f'Capacity, {config.currency_crypto_ticker}')
    plot_legend_proxy_key_metric_movement = Line2D([0], [0], label=f'Capacity {plot_key_metric_movement_format}')
    
    stacked_legend_proxy_nodes_unannounced = Line2D([0], [0], label='Clearnet')
    stacked_legend_proxy_nodes_tor = Line2D([0], [0], label='Clear/Darknet')
    stacked_legend_proxy_nodes_clearnet_tor = Line2D([0], [0], label='Darknet')
    stacked_legend_proxy_nodes_clearnet = Line2D([0], [0], label='Unannounced')
    
    # Set actual plot and stacked area legend:
    plot_legend = ax1.legend(handles=[plot_legend_proxy_channel_count,
                                 plot_legend_proxy_total_capacity,
                                 plot_legend_proxy_key_metric_movement],
                                 loc="upper left", prop=plot_font, handlelength=0)
    
    stacked_legend = ax3.legend(handles=[stacked_legend_proxy_nodes_unannounced,
                                 stacked_legend_proxy_nodes_tor,
                                 stacked_legend_proxy_nodes_clearnet_tor,
                                 stacked_legend_proxy_nodes_clearnet],
                                 loc="lower left", prop=plot_font, handlelength=0)

    # Set plot and stacked area legend colors:
    plot_legend.get_texts()[0].set_color(plot_colors['channel_count'])
    plot_legend.get_texts()[1].set_color(plot_colors['total_capacity'])
    plot_legend.get_texts()[2].set_color(plot_colors[f'{plot_key_metric_movement_color}'])
    plot_legend.get_frame().set_facecolor(plot_colors['frame'])
    plot_legend.get_frame().set_alpha(0.95)

    stacked_legend.get_texts()[0].set_color(plot_colors['nodes_clearnet'])
    stacked_legend.get_texts()[1].set_color(plot_colors['nodes_clearnet_tor'])
    stacked_legend.get_texts()[2].set_color(plot_colors['nodes_tor'])
    stacked_legend.get_texts()[3].set_color(plot_colors['nodes_unannounced'])
    stacked_legend.get_frame().set_facecolor(plot_colors['frame_nodes'])
    stacked_legend.get_frame().set_alpha(0.5)

    # Set plot and stacked area legend text size:
    for text in plot_legend.get_texts():
        text.set_fontsize(12)

    for text in stacked_legend.get_texts():
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

    latest_raw_values_name = 'lightning_latest_raw_values'

    # User configuration related variables:
    latest_raw_values = config.databases[f'{latest_raw_values_name}']
    latest_raw_values_file_path = latest_raw_values['file']['path']
    latest_raw_values_file_name = latest_raw_values['file']['name']
    latest_raw_values_file = latest_raw_values_file_path + latest_raw_values_file_name
    latest_values_file = latest_raw_values_file_path + 'latest_values.md'

    with open (latest_raw_values_file, 'r') as json_file:
        
        api_data = json.load(json_file)

        latest_data = api_data['latest']
        previous_data = api_data['previous']

        # Parse raw API data to separate values:
        LAST_UPDATED = format_utc(latest_data['added'])

# network
        CHANNEL_COUNT = format_quantity(latest_data['channel_count'])
        CHANNEL_CHANGE_1W = format_quantity(latest_data['channel_count'] - previous_data['channel_count'])
        CHANNEL_CHANGE_PERCENTAGE_1W = format_percentage(calculate_percentage_change(previous_data['channel_count'], latest_data['channel_count']))
        
        CAPACITY_COUNT = format_currency(latest_data['total_capacity'] / 100_000_000, config.currency_crypto_ticker)
        CAPACITY_CHANGE_1W = format_currency((latest_data['total_capacity'] - previous_data['total_capacity']) / 100_000_000, config.currency_crypto_ticker)
        CAPACITY_CHANGE_PERCENTAGE_1W = format_percentage(calculate_percentage_change(previous_data['total_capacity'], latest_data['total_capacity']))
        
        CAPACITY_AVG_COUNT = format_currency(latest_data['avg_capacity'] / 100_000_000, config.currency_crypto_ticker, 4)
        CAPACITY_AVG_CHANGE_1W = format_currency((latest_data['avg_capacity'] - previous_data['avg_capacity']) / 100_000_000, config.currency_crypto_ticker, 4)
        CAPACITY_AVG_CHANGE_PERCENTAGE_1W = format_percentage(calculate_percentage_change(previous_data['avg_capacity'], latest_data['avg_capacity']))
        

        

# nodes

        NODE_COUNT = format_quantity(latest_data['node_count'])
        NODE_CHANGE_1W = format_quantity(latest_data['node_count'] - previous_data['node_count'])
        NODE_CHANGE_PERCENTAGE_1W = format_percentage(calculate_percentage_change(previous_data['node_count'], latest_data['node_count']))

        NODE_CLEARNET_COUNT = format_quantity(latest_data['clearnet_nodes'])
        NODE_CLEARNET_1W = format_quantity(latest_data['clearnet_nodes'] - previous_data['clearnet_nodes'])
        NODE_CLEARNET_PERCENTAGE_1W = format_percentage(calculate_percentage_change(previous_data['clearnet_nodes'], latest_data['clearnet_nodes']))

        NODE_CLEARDARKNET_COUNT = format_quantity(latest_data['clearnet_tor_nodes'])
        NODE_CLEARDARKNET_CHANGE_1W = format_quantity(latest_data['clearnet_tor_nodes'] - previous_data['clearnet_tor_nodes'])
        NODE_CLEARDARKNET_CHANGE_PERCENTAGE_1W = format_percentage(calculate_percentage_change(previous_data['clearnet_tor_nodes'], latest_data['clearnet_tor_nodes']))

        NODE_DARKNET_COUNT = format_quantity(latest_data['tor_nodes'])
        NODE_DARKNET_CHANGE_1W = format_quantity(latest_data['tor_nodes'] - previous_data['tor_nodes'])
        NODE_DARKNET_CHANGE_PERCENTAGE_1W = format_percentage(calculate_percentage_change(previous_data['tor_nodes'], latest_data['tor_nodes']))

        NODE_UNANNOUNCED_COUNT = format_quantity(latest_data['unannounced_nodes'])
        NODE_UNANNOUNCED_CHANGE_1W = format_quantity(latest_data['unannounced_nodes'] - previous_data['unannounced_nodes'])
        NODE_UNANNOUNCED_CHANGE_PERCENTAGE_1W = format_percentage(calculate_percentage_change(previous_data['unannounced_nodes'], latest_data['unannounced_nodes']))
    
#fees
        FEE_AVG_RATE_COUNT = format_currency(latest_data['avg_fee_rate'], '', 0)
        FEE_AVG_RATE_CHANGE_1W = format_currency(latest_data['avg_fee_rate'] - previous_data['avg_fee_rate'], '', 0)
        FEE_AVG_RATE_CHANGE_PERCENTAGE_1W = format_percentage(calculate_percentage_change(previous_data['avg_fee_rate'], latest_data['avg_fee_rate']))

        FEE_BASE_AVG_RATE_COUNT = format_currency(latest_data['avg_base_fee_mtokens'], '', 0)
        FEE_BASE_AVG_RATE_CHANGE_1W = format_currency(latest_data['avg_base_fee_mtokens'] - previous_data['avg_base_fee_mtokens'], '', 0)
        FEE_BASE_AVG_RATE_CHANGE_PERCENTAGE_1W = format_percentage(calculate_percentage_change(previous_data['avg_base_fee_mtokens'], latest_data['avg_base_fee_mtokens']))

        # Format values text for user presentation:
        info_network = f'[Network]\n' \
            f'Channels: {CHANNEL_COUNT}\n' \
            f'1w: {CHANNEL_CHANGE_PERCENTAGE_1W} ({CHANNEL_CHANGE_1W})\n' \
            f'Capacity: {CAPACITY_COUNT}\n' \
            f'1w: {CAPACITY_CHANGE_PERCENTAGE_1W} ({CAPACITY_CHANGE_1W})\n' \
            f'Avg Cp/Ch: {CAPACITY_AVG_COUNT}\n' \
            f'1w: {CAPACITY_AVG_CHANGE_PERCENTAGE_1W} ({CAPACITY_AVG_CHANGE_1W})\n' 
        info_node = f'[Nodes]\n' \
            f'Total: {NODE_COUNT}\n' \
            f'1w: {NODE_CHANGE_PERCENTAGE_1W} ({NODE_CHANGE_1W})\n' \
            f'Clearnet: {NODE_CLEARNET_COUNT}\n' \
            f'1w: {NODE_CLEARNET_PERCENTAGE_1W} ({NODE_CLEARNET_1W})\n' \
            f'Clr/Drknt: {NODE_CLEARDARKNET_COUNT}\n' \
            f'1w: {NODE_CLEARDARKNET_CHANGE_PERCENTAGE_1W} ({NODE_CLEARDARKNET_CHANGE_1W})\n' \
            f'Darknet: {NODE_DARKNET_COUNT}\n' \
            f'1w: {NODE_DARKNET_CHANGE_PERCENTAGE_1W} ({NODE_DARKNET_CHANGE_1W})\n' \
            f'Unannounced: {NODE_UNANNOUNCED_COUNT}\n' \
            f'1w: {NODE_UNANNOUNCED_CHANGE_PERCENTAGE_1W} ({NODE_UNANNOUNCED_CHANGE_1W})\n'
        info_fees = f'[Fees]\n' \
            f'Avg Rate: {FEE_AVG_RATE_COUNT} sats\n' \
            f'1w: {FEE_AVG_RATE_CHANGE_PERCENTAGE_1W} ({FEE_AVG_RATE_CHANGE_1W} sats)\n' \
            f'Avg Base: {FEE_BASE_AVG_RATE_COUNT} sats\n' \
            f'1w: {FEE_BASE_AVG_RATE_CHANGE_PERCENTAGE_1W} ({FEE_BASE_AVG_RATE_CHANGE_1W} sats)\n'
        info_update = f'{LAST_UPDATED}\n'

        # Write latest values to Markdown file:
        with open (latest_values_file, 'w') as latest_values:
            latest_values.write(f"```md\n{info_network}\n{info_node}\n{info_fees}\n{info_update}\n```")






if __name__ == '__main__':
    get_lightning_chart()
#    get_lightning_latest_raw_values()

