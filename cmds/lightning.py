import io
import os
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
from tools import (error_handler_common,
                   define_key_metric_movement,
                   calculate_percentage_change,
                   convert_timestamp_to_utc,
                   format_time_axis,
                   format_amount,
                   format_utc,
                   format_currency,
                   format_percentage,
                   format_quantity)



'''
Functions related to creation of plot and markdown files for Lightning database.

Plot based on chart values and made for whole number of days. Dates period based
on API endpoint specified in user configuration. Background image depends on % of
channels BTC capacity change (positive or negative). Axes have automatic appropriate
scaling to different dates periods.

Markdown based on snapshot and chart values and formatted for user presentation.
'''


@error_handler_common
def draw_lightning(days=config.days['lightning']):
    # Draws Lightning plot with properties specified in user configuration.
    
    # User configuration related variables:
    chart = config.charts['lightning']
    chart_file_path = chart['file']['path']
    chart_file_name = chart['file']['name']
    chart_file = chart_file_path + chart_file_name

    # Plot-related variables:
    plot = config.images['lightning']
    plot_font = font_manager.FontProperties(fname=plot['font'])
    plot_colors = plot['colors']
    plot_background = plot['backgrounds']
        
    # Create plot DataFrame:
    plot_df = pd.read_csv(chart_file)
    
    # Set days value limits and image file name:
    if isinstance(days, int):
        days = 2 if days < 2 else days
        days = len(plot_df) - 1 if days > len(plot_df) - 1 else days
        plot_file = plot['path'] + f'lightning_days_{days}.jpg'
    else:
        days = len(plot_df) - 1
        plot_file = plot['path'] + f'lightning_days_max.jpg'

    plot_time_till = datetime.utcfromtimestamp(os.path.getctime(chart_file)).strftime('%Y-%m-%d')
    plot_time_from = (datetime.utcfromtimestamp(os.path.getctime(chart_file)) - timedelta(days=days)).strftime('%Y-%m-%d')

    # Specification of chart indexes for plot axes:
    plot_index_last = len(plot_df)
    plot_index_first = len(plot_df) - days
    if plot_index_first < 1:
        plot_index_first = 1

    # Key metric related variables for percentage change calculation:
    plot_key_metric = 'capacity'
    plot_key_metric_new = plot_df[plot_key_metric][plot_index_last - 1]
    plot_key_metric_old = plot_df[plot_key_metric][plot_index_first]
    plot_key_metric_movement = calculate_percentage_change(plot_key_metric_old, plot_key_metric_new)
    plot_key_metric_movement_format = format_percentage(plot_key_metric_movement)

    # Background-related variables:
    background = define_key_metric_movement(plot, plot_key_metric_movement)
    background_path = plot_background[f'{background}']['path']
    background_coordinates = plot_background[f'{background}']['coordinates']
    background_colors = plot_background[f'{background}']['colors']

    # Set rolling avearge to 10% of plot interval:
    rolling_average = math.ceil(days * 0.1)

    # Creation of plot axes:
    axis_date = plot_df['date'][plot_index_first:plot_index_last]
    axis_channels = plot_df['channels'].rolling(window=rolling_average).mean()[plot_index_first:plot_index_last]
    axis_capacity = plot_df['capacity'].rolling(window=rolling_average).mean()[plot_index_first:plot_index_last]

    # Creation of plot stacked area:
    stacked_nodes = plot_df[['nodes_unknown',
                            'nodes_darknet',
                            'nodes_greynet',
                            'nodes_clearnet']][plot_index_first:plot_index_last]

    # Stacked area normalized for 100%:
    stacked_nodes_percentages = stacked_nodes.divide(stacked_nodes.sum(axis=1), axis=0) * 100

    stacked_nodes_clearnet = format_percentage(stacked_nodes_percentages['nodes_clearnet'][plot_index_last - 1])[1:]
    stacked_nodes_greynet = format_percentage(stacked_nodes_percentages['nodes_greynet'][plot_index_last - 1])[1:]
    stacked_nodes_darknet = format_percentage(stacked_nodes_percentages['nodes_darknet'][plot_index_last - 1])[1:]
    stacked_nodes_unknown = format_percentage(stacked_nodes_percentages['nodes_unknown'][plot_index_last - 1])[1:]

    # Creation of plot figure:
    fig, ax1 = plt.subplots(figsize=(12, 7.4))
    fig.patch.set_alpha(0.0)
    fig.patch.set_facecolor('none')
    ax1.grid(True, axis = 'both', linestyle="dashed", linewidth=0.5, alpha=0.7)
    ax2 = ax1.twinx()
    ax3 = ax1.twinx()

    # Set axes lines to change width depending on days period:
    linewidth_capacity = 14 - days * 0.01
    if linewidth_capacity < 10:
        linewidth_capacity = 10
    linewidth_channels = 8 - days * 0.01
    if linewidth_channels < 6:
        linewidth_channels = 6
      
    ax1.plot(axis_date, axis_capacity, color=plot_colors['capacity'], label="capacity", linewidth=linewidth_capacity)
    ax2.plot(axis_date, axis_channels, color=plot_colors['channels'], label="channels", linewidth=linewidth_channels)

    # Set stacked area colors:
    stacked_nodes_colors = [plot_colors['nodes_unknown'],
                            plot_colors['nodes_darknet'],
                            plot_colors['nodes_greynet'],
                            plot_colors['nodes_clearnet']]
    ax3.stackplot(axis_date, stacked_nodes_percentages.T, colors=stacked_nodes_colors)

    # Set axes borders for better scaling:
    ax1.set_xlim(axis_date.iloc[0], axis_date.iloc[-1])  
    ax3.set_ylim(0, 100)

    # Set axes text format:
    ax1.xaxis.set_major_formatter(FuncFormatter(lambda x, _: format_time_axis(x, days)))
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, _: format_amount(x / 100_000_000)))
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, _: format_amount(x)))
    
    # Set date axis ticks and text properties:
    axis_date_ticks_positions = np.linspace(axis_date.iloc[0], axis_date.iloc[-1], num=7)
    ax1.set_xticks(axis_date_ticks_positions)
    plt.setp(ax1.get_xticklabels(), rotation=10, ha='center')

    # Set axes ticks text color, font and size:
    ax1.tick_params(axis="x", labelcolor=plot_colors['date'])
    ax1.tick_params(axis="y", labelcolor=plot_colors['capacity'])
    ax2.tick_params(axis="y", labelcolor=plot_colors['channels'])
    ax3.tick_params(axis="y", labelcolor=plot_colors['nodes_greynet'])

    for label in ax1.get_xticklabels():
        label.set_fontproperties(plot_font)
        label.set_fontsize(12)

    for label in ax1.get_yticklabels() + ax2.get_yticklabels():
        label.set_fontproperties(plot_font)
        label.set_fontsize(18)

    for label in ax3.get_yticklabels():
        label.set_fontproperties(plot_font)
        label.set_fontsize(1)

    # Set axes order (higher value puts layer to the front):
    ax1.set_zorder(3)
    ax2.set_zorder(2)
    ax3.set_zorder(1)

    # Set plot and stacked area legend proxies:
    plot_legend_proxy_capacity = Line2D([0], [0], label=f'Capacity, {config.currency_crypto_ticker}')
    plot_legend_proxy_channels = Line2D([0], [0], label='Channels')
    plot_legend_nodes_clearnet = Line2D([0], [0], label=f'{stacked_nodes_clearnet} Clearnet')
    plot_legend_nodes_greynet = Line2D([0], [0], label=f'{stacked_nodes_greynet} Greynet')
    plot_legend_nodes_darknet = Line2D([0], [0], label=f'{stacked_nodes_darknet} Darknet')
    plot_legend_nodes_unknown = Line2D([0], [0], label=f'{stacked_nodes_unknown} Unknown')
    
    # Set actual plot and stacked area legend:
    plot_legend = ax1.legend(handles=[plot_legend_proxy_capacity,
                                 plot_legend_proxy_channels,
                                 plot_legend_nodes_clearnet,
                                 plot_legend_nodes_greynet,
                                 plot_legend_nodes_darknet,
                                 plot_legend_nodes_unknown],
                                 loc="upper left", prop=plot_font, handlelength=0)

    # Set plot and stacked area legend colors:
    plot_legend.get_texts()[0].set_color(plot_colors['capacity'])
    plot_legend.get_texts()[1].set_color(plot_colors['channels'])
    plot_legend.get_texts()[2].set_color(plot_colors['nodes_clearnet'])
    plot_legend.get_texts()[3].set_color(plot_colors['nodes_greynet'])
    plot_legend.get_texts()[4].set_color(plot_colors['nodes_darknet'])
    plot_legend.get_texts()[5].set_color(plot_colors['nodes_unknown'])
    plot_legend.get_frame().set_facecolor(plot_colors['frame'])
    plot_legend.get_frame().set_alpha(0.95)

    # Set plot and stacked area legend text size:
    for text in plot_legend.get_texts():
        text.set_fontsize(16)

    # Open memory buffer and save plot to memory buffer:
    plot_buffer = io.BytesIO()
    plt.savefig(plot_buffer, format='png', bbox_inches='tight', transparent=True, dpi=150)
    matplotlib.pyplot.close()

    # Open background image, draw Lightning title and save image to memory buffer:
    title_image = Image.open(background_path)
    draw = ImageDraw.Draw(title_image)

    # Lightning title related variables:
    title_font = plot['font']
    title_list = [
            [{'text': 'mempool.space', 'position': background_colors['api'][1], 'font_size': 36, 'text_color': background_colors['api'][0]},
            {'text': 'lightning statistics', 'position': background_colors['api'][2], 'font_size': 25, 'text_color': background_colors['api'][0]}],

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

    # Overlay plot buffer with Lightning title buffer and save final image:
    background_image = Image.open(title_buffer).convert("RGB")
    title_buffer.seek(0)
    background_overlay = Image.open(plot_buffer)
    plot_buffer.seek(0)

    background_image.paste(background_overlay, background_coordinates, mask=background_overlay)
    background_image.save(plot_file, "JPEG", quality=90, icc_profile=background_image.info.get('icc_profile', ''))
    title_buffer.close()
    plot_buffer.close()
    
    main_logger.info(f'{plot_file} drawn')

    return plot_file


@error_handler_common
def write_lightning(days=1):
    # Writes Lightning markdown with properties specified in user configuration.

    # User configuration related variables:
    snapshot = config.snapshots['lightning']
    snapshot_file_path = snapshot['file']['path']
    snapshot_file_name = snapshot['file']['name']
    snapshot_file = snapshot_file_path + snapshot_file_name
    
    chart = config.charts['lightning']
    chart_file_path = chart['file']['path']
    chart_file_name = chart['file']['name']
    chart_file = chart_file_path + chart_file_name

    chart_data = pd.read_csv(chart_file)
    chart_data['nodes'] = chart_data['nodes_darknet'] + chart_data['nodes_clearnet'] + chart_data['nodes_unknown'] + chart_data['nodes_greynet']
    chart_date = chart_data['date']
    chart_channels = chart_data['channels']
    chart_capacity = chart_data['capacity']
    chart_nodes = chart_data['nodes']

    # Set time period:
    now = len(chart_data) - 1
    if isinstance(days, int):
        days = 1 if days < 1 else days
        days = len(chart_data) - 1 if days > len(chart_data) - 1 else days
    else:
        days = len(chart_data) - 1
    past = len(chart_data) - days
    markdown_file = chart_file_path + f'lightning_days_{days}.md'

    with open (snapshot_file, 'r') as json_file:
        
        snapshot_data = json.load(json_file)

        latest_data = snapshot_data['latest']
#        previous_data = snapshot_data['previous']

        # Parse snapshot to separate values:
        LAST_UPDATED = format_utc(latest_data['added'])

        TIME_NOW = convert_timestamp_to_utc(chart_date[now])[:10]
        TIME_PAST = convert_timestamp_to_utc(chart_date[past])[:10]

        CHANNELS_CURRENT = format_quantity(latest_data['channel_count'])
#        CHANNEL_CHANGE_1W = format_quantity(latest_data['channels'] - previous_data['channels'])
#        CHANNEL_CHANGE_PERCENTAGE_1W = format_percentage(calculate_percentage_change(previous_data['channels'], latest_data['channels']))
        
        CAPACITY_CURRENT = format_currency(latest_data['total_capacity'] / 100_000_000, config.currency_crypto_ticker, decimal=2)
#        CAPACITY_CHANGE_1W = format_currency((latest_data['capacity'] - previous_data['capacity']) / 100_000_000, config.currency_crypto_ticker)
#        CAPACITY_CHANGE_PERCENTAGE_1W = format_percentage(calculate_percentage_change(previous_data['capacity'], latest_data['capacity']))
        
        CAPACITY_AVG_CURRENT = format_currency(latest_data['avg_capacity'] / 100_000_000, config.currency_crypto_ticker, decimal=4)
#        CAPACITY_AVG_CHANGE_1W = format_currency((latest_data['avg_capacity'] - previous_data['avg_capacity']) / 100_000_000, config.currency_crypto_ticker, decimal=4)
#        CAPACITY_AVG_CHANGE_PERCENTAGE_1W = format_percentage(calculate_percentage_change(previous_data['avg_capacity'], latest_data['avg_capacity']))
        
        NODE_CURRENT = format_quantity(latest_data['node_count'])
#        NODE_CHANGE_1W = format_quantity(latest_data['node_count'] - previous_data['node_count'])
#        NODE_CHANGE_PERCENTAGE_1W = format_percentage(calculate_percentage_change(previous_data['node_count'], latest_data['node_count']))

#        NODE_CLEARNET_COUNT = format_quantity(latest_data['clearnet_nodes'])
#        NODE_CLEARNET_PERCENTAGE = f"{round(latest_data['clearnet_nodes'] / (latest_data['node_count'] / 100), 2)}%"
#        NODE_CLEARNET_1W = format_quantity(latest_data['clearnet_nodes'] - previous_data['clearnet_nodes'])
#        NODE_CLEARNET_PERCENTAGE_1W = format_percentage(calculate_percentage_change(previous_data['clearnet_nodes'], latest_data['clearnet_nodes']))

#        NODE_CLEARDARKNET_COUNT = format_quantity(latest_data['clearnet_tor_nodes'])
#        NODE_CLEARDARKNET_PERCENTAGE = f"{round(latest_data['clearnet_tor_nodes'] / (latest_data['node_count'] / 100), 2)}%"
#        NODE_CLEARDARKNET_CHANGE_1W = format_quantity(latest_data['clearnet_tor_nodes'] - previous_data['clearnet_tor_nodes'])
#        NODE_CLEARDARKNET_CHANGE_PERCENTAGE_1W = format_percentage(calculate_percentage_change(previous_data['clearnet_tor_nodes'], latest_data['clearnet_tor_nodes']))

#        NODE_DARKNET_COUNT = format_quantity(latest_data['tor_nodes'])
#        NODE_DARKNET_PERCENTAGE = f"{round(latest_data['tor_nodes'] / (latest_data['node_count'] / 100), 2)}%"
#        NODE_DARKNET_CHANGE_1W = format_quantity(latest_data['tor_nodes'] - previous_data['tor_nodes'])
#        NODE_DARKNET_CHANGE_PERCENTAGE_1W = format_percentage(calculate_percentage_change(previous_data['tor_nodes'], latest_data['tor_nodes']))

#        NODE_UNKNOWN_COUNT = format_quantity(latest_data['unannounced_nodes'])
#        NODE_UNKNOWN_PERCENTAGE = f"{round(latest_data['unannounced_nodes'] / (latest_data['node_count'] / 100), 2)}%"
#        NODE_UNKNOWN_CHANGE_1W = format_quantity(latest_data['unknown_nodes'] - previous_data['unknown_nodes'])
#        NODE_UNKNOWN_CHANGE_PERCENTAGE_1W = format_percentage(calculate_percentage_change(previous_data['unknown_nodes'], latest_data['unknown_nodes']))
    
        FEE_AVG_RATE_COUNT = format_currency(latest_data['avg_fee_rate'], '', decimal=0)
#        FEE_AVG_RATE_CHANGE_1W = format_currency(latest_data['avg_fee_rate'] - previous_data['avg_fee_rate'], '', decimal=0)
#        FEE_AVG_RATE_CHANGE_PERCENTAGE_1W = format_percentage(calculate_percentage_change(previous_data['avg_fee_rate'], latest_data['avg_fee_rate']))

        FEE_BASE_AVG_RATE_COUNT = format_currency(latest_data['avg_base_fee_mtokens'], '', decimal=0)
#        FEE_BASE_AVG_RATE_CHANGE_1W = format_currency(latest_data['avg_base_fee_mtokens'] - previous_data['avg_base_fee_mtokens'], '', decimal=0)
#        FEE_BASE_AVG_RATE_CHANGE_PERCENTAGE_1W = format_percentage(calculate_percentage_change(previous_data['avg_base_fee_mtokens'], latest_data['avg_base_fee_mtokens']))

        CHANNELS_NOW = format_amount(chart_channels[now])
        CHANNELS_PAST = format_amount(chart_channels[past])
        CHANNELS_PAST_CHANGE = format_amount(chart_channels[now] - chart_channels[past])
        CHANNELS_PAST_CHANGE_PERCENTAGE = format_percentage(calculate_percentage_change(chart_channels[past], chart_channels[now]))

        CAPACITY_NOW = format_amount(chart_capacity[now] / 100_000_000)
        CAPACITY_PAST = format_amount(chart_capacity[past] / 100_000_000)
        CAPACITY_PAST_CHANGE = format_amount((chart_capacity[now] - chart_capacity[past]) / 100_000_000)
        CAPACITY_PAST_CHANGE_PERCENTAGE = format_percentage(calculate_percentage_change(chart_capacity[past], chart_capacity[now]))

        NODES_NOW = format_amount(chart_nodes[now])
        NODES_PAST = format_amount(chart_nodes[past])
        NODES_PAST_CHANGE = format_amount(chart_nodes[now] - chart_nodes[past])
        NODES_PAST_CHANGE_PERCENTAGE = format_percentage(calculate_percentage_change(chart_nodes[past], chart_nodes[now]))

        # Format text for user presentation:
        if days == 1:
            info_network = \
                f'Channels: {CHANNELS_CURRENT}\n' \
                f'Capacity: {CAPACITY_CURRENT}\n' \
                f'Nodes: {NODE_CURRENT}\n'
            info_avgs = \
                f'Avg Fee Rate: {FEE_AVG_RATE_COUNT} sats\n' \
                f'Avg Fee Base: {FEE_BASE_AVG_RATE_COUNT} sats\n' \
                f'Avg {CAPACITY_AVG_CURRENT} per channel\n'
            info_update = f'UTC {LAST_UPDATED}\n'

            # Write text to Markdown file:
            with open (markdown_file, 'w') as markdown:
                markdown.write(f'```Lightning\n{info_network}\n{info_avgs}\n{info_update}```')
        else:
            info_period = f'{TIME_PAST} --> {TIME_NOW}\n'
            info_channels = \
                f'Channels: {CHANNELS_PAST} --> {CHANNELS_NOW}\n' \
                f'{days}d: {CHANNELS_PAST_CHANGE_PERCENTAGE} ({CHANNELS_PAST_CHANGE})\n'
            info_capacity = \
                f'Capacity: {CAPACITY_PAST} --> {CAPACITY_NOW}\n' \
                f'{days}d: {CAPACITY_PAST_CHANGE_PERCENTAGE} ({CAPACITY_PAST_CHANGE})\n'
            info_nodes = \
                f'Nodes: {NODES_PAST} --> {NODES_NOW}\n' \
                f'{days}d: {NODES_PAST_CHANGE_PERCENTAGE} ({NODES_PAST_CHANGE})\n'
            
            # Write text to Markdown file:
            with open (markdown_file, 'w') as markdown:
                markdown.write(f'```Lightning\n{info_period}\n{info_channels}\n{info_capacity}\n{info_nodes}```')

        main_logger.info(f'{markdown_file} written')

        return markdown_file




if __name__ == '__main__':

    days = [-1, 0, 1, 2, 14, 30, 90, 180, 400, 'max']
    for day in days:
        draw_lightning(day)
        write_lightning(day)
  
    from tools import convert_date_to_days
    dates = ['2022-03-01', '2012-03-01']
    for date in dates:
        day = convert_date_to_days(date)
        draw_lightning(day)
        write_lightning(day)
