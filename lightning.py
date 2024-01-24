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
channels BTC capacity change (positive or negative). Axies have automatic appropriate
scaling to different dates periods.

Markdown based on snapshot and chart values and formatted for user presentation.
'''

def draw_plot():
    # Draws Lightning plot with properties specified in user configuration.
    
    # User configuration related variables:
    chart = config.databases['charts']['lightning']
    chart_file_path = chart['file']['path']
    chart_file_name = chart['file']['name']
    chart_file = chart_file_path + chart_file_name

    # Plot-related variables:
    plot = config.plot['lightning']
    plot_font = font_manager.FontProperties(fname=plot['font'])
    plot_colors = plot['colors']
    plot_background = plot['backgrounds']
    plot_output = plot['path'] + 'lightning.jpg'
        
    # Creation of plot DataFrame:
    plot_df = pd.read_csv(chart_file)
    
    days = len(plot_df)

    # Specification of chart indexes for plot axies:
    plot_index_last = len(plot_df)
    plot_index_first = 0

    # Key metric related variables for percentage change calculation:
    plot_key_metric = 'capacity'
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
    axis_date = plot_df['date']
    axis_channels = plot_df['channels']
    axis_capacity = plot_df['capacity']

    # Creation of plot stacked area:
    stacked_nodes = plot_df[['nodes_unknown',
                            'nodes_darknet',
                            'nodes_greynet',
                            'nodes_clearnet']]

    # Stacked area normalized for 100%:
    stacked_nodes_percentages = stacked_nodes.divide(stacked_nodes.sum(axis=1), axis=0) * 100
    
    # Creation of plot figure:
    fig, ax1 = plt.subplots(figsize=(12, 7.4))
    fig.patch.set_alpha(0.0)
    fig.patch.set_facecolor('none')
    ax1.grid(True, axis = 'both', linestyle="dashed", linewidth=0.5, alpha=0.7)
    ax2 = ax1.twinx()
    ax3 = ax1.twinx()

    # Set axies lines:    
    ax1.plot(axis_date, axis_capacity, color=plot_colors['capacity'], label="capacity", linewidth=10)
    ax2.plot(axis_date, axis_channels, color=plot_colors['channels'], label="channels", linewidth=6)

    # Set stacked area colors:
    stacked_nodes_colors = [plot_colors['nodes_unknown'],
                            plot_colors['nodes_darknet'],
                            plot_colors['nodes_greynet'],
                            plot_colors['nodes_clearnet']]
    ax3.stackplot(axis_date, stacked_nodes_percentages.T, colors=stacked_nodes_colors)

    # Set axies borders for better scaling:
    ax1.set_xlim(axis_date.iloc[0], axis_date.iloc[-1])  
    ax1.set_ylim(min(axis_capacity) * 0.995, max(axis_capacity) * 1.005)
    ax2.set_ylim(min(axis_channels) * 0.995, max(axis_channels) * 1.005)
    ax3.set_ylim(0, 100)

     # Set axies text format:
    ax1.xaxis.set_major_formatter(FuncFormatter(lambda x, _: format_time_axis(x, days)))
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, _: format_amount(x / 100_000_000)))
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, _: format_amount(x)))
    
    # Set date axis ticks and text properties:
    axis_date_ticks_positions = np.linspace(axis_date.iloc[0], axis_date.iloc[-1], num=7)
    ax1.set_xticks(axis_date_ticks_positions)
    plt.setp(ax1.get_xticklabels(), rotation=10, ha='center')

    # Set axies ticks text color, font and size:
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

    # Set axies order (higher value puts layer to the front):
    ax1.set_zorder(3)
    ax2.set_zorder(2)
    ax3.set_zorder(1)

    # Set plot and stacked area legend proxies:
    legend_period = list(chart['file']['columns'].keys())[0][-2:]

    plot_legend_proxy_capacity = Line2D([0], [0], label=f'Capacity, {config.currency_crypto_ticker}')
    plot_legend_proxy_channels = Line2D([0], [0], label='Channels Count')
    plot_legend_proxy_key_metric_movement = Line2D([0], [0], label=f'{legend_period} Capacity {plot_key_metric_movement_format}')
    
    stacked_legend_proxy_nodes_unknown = Line2D([0], [0], label='Clearnet')
    stacked_legend_proxy_nodes_darknet = Line2D([0], [0], label='Greynet')
    stacked_legend_proxy_nodes_greynet = Line2D([0], [0], label='Darknet')
    stacked_legend_proxy_nodes_clearnet = Line2D([0], [0], label='Unknown')
    
    # Set actual plot and stacked area legend:
    plot_legend = ax1.legend(handles=[plot_legend_proxy_capacity,
                                 plot_legend_proxy_channels,
                                 plot_legend_proxy_key_metric_movement],
                                 loc="upper left", prop=plot_font, handlelength=0)
    
    stacked_legend = ax3.legend(handles=[stacked_legend_proxy_nodes_unknown,
                                 stacked_legend_proxy_nodes_darknet,
                                 stacked_legend_proxy_nodes_greynet,
                                 stacked_legend_proxy_nodes_clearnet],
                                 loc="lower left", prop=plot_font, handlelength=0)

    # Set plot and stacked area legend colors:
    plot_legend.get_texts()[0].set_color(plot_colors['capacity'])
    plot_legend.get_texts()[1].set_color(plot_colors['channels'])
    plot_legend.get_texts()[2].set_color(plot_colors[f'{plot_key_metric_movement_color}'])
    plot_legend.get_frame().set_facecolor(plot_colors['frame'])
    plot_legend.get_frame().set_alpha(0.95)

    stacked_legend.get_texts()[0].set_color(plot_colors['nodes_clearnet'])
    stacked_legend.get_texts()[1].set_color(plot_colors['nodes_greynet'])
    stacked_legend.get_texts()[2].set_color(plot_colors['nodes_darknet'])
    stacked_legend.get_texts()[3].set_color(plot_colors['nodes_unknown'])
    stacked_legend.get_frame().set_facecolor(plot_colors['frame_nodes'])
    stacked_legend.get_frame().set_alpha(0.5)

    # Set plot and stacked area legend text size:
    for text in plot_legend.get_texts():
        text.set_fontsize(16)

    for text in stacked_legend.get_texts():
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
    # Writes Lightning markdown with properties specified in user configuration.

    # User configuration related variables:
    snapshot = config.databases['snapshots']['lightning']
    snapshot_file_path = snapshot['file']['path']
    snapshot_file_name = snapshot['file']['name']
    snapshot_file = snapshot_file_path + snapshot_file_name
    
    markdown_file = snapshot_file_path + 'lightning.md'

    with open (snapshot_file, 'r') as json_file:
        
        snapshot_data = json.load(json_file)

        latest_data = snapshot_data['latest']
#        previous_data = snapshot_data['previous']

        # Parse snapshot to separate values:
        LAST_UPDATED = format_utc(latest_data['added'])

        CHANNELS = format_quantity(latest_data['channel_count'])
#        CHANNEL_CHANGE_1W = format_quantity(latest_data['channels'] - previous_data['channels'])
#        CHANNEL_CHANGE_PERCENTAGE_1W = format_percentage(calculate_percentage_change(previous_data['channels'], latest_data['channels']))
        
        CAPACITY_COUNT = format_currency(latest_data['total_capacity'] / 100_000_000, config.currency_crypto_ticker)
#        CAPACITY_CHANGE_1W = format_currency((latest_data['capacity'] - previous_data['capacity']) / 100_000_000, config.currency_crypto_ticker)
#        CAPACITY_CHANGE_PERCENTAGE_1W = format_percentage(calculate_percentage_change(previous_data['capacity'], latest_data['capacity']))
        
        CAPACITY_AVG_COUNT = format_currency(latest_data['avg_capacity'] / 100_000_000, config.currency_crypto_ticker, 4)
#        CAPACITY_AVG_CHANGE_1W = format_currency((latest_data['avg_capacity'] - previous_data['avg_capacity']) / 100_000_000, config.currency_crypto_ticker, decimal=4)
#        CAPACITY_AVG_CHANGE_PERCENTAGE_1W = format_percentage(calculate_percentage_change(previous_data['avg_capacity'], latest_data['avg_capacity']))
        
        NODE_COUNT = format_quantity(latest_data['node_count'])
#        NODE_CHANGE_1W = format_quantity(latest_data['node_count'] - previous_data['node_count'])
#        NODE_CHANGE_PERCENTAGE_1W = format_percentage(calculate_percentage_change(previous_data['node_count'], latest_data['node_count']))

        NODE_CLEARNET_COUNT = format_quantity(latest_data['clearnet_nodes'])
        NODE_CLEARNET_PERCENTAGE = f"{round(latest_data['clearnet_nodes'] / (latest_data['node_count'] / 100), 2)}%"
#        NODE_CLEARNET_1W = format_quantity(latest_data['clearnet_nodes'] - previous_data['clearnet_nodes'])
#        NODE_CLEARNET_PERCENTAGE_1W = format_percentage(calculate_percentage_change(previous_data['clearnet_nodes'], latest_data['clearnet_nodes']))

        NODE_CLEARDARKNET_COUNT = format_quantity(latest_data['clearnet_tor_nodes'])
        NODE_CLEARDARKNET_PERCENTAGE = f"{round(latest_data['clearnet_tor_nodes'] / (latest_data['node_count'] / 100), 2)}%"
#        NODE_CLEARDARKNET_CHANGE_1W = format_quantity(latest_data['clearnet_tor_nodes'] - previous_data['clearnet_tor_nodes'])
#        NODE_CLEARDARKNET_CHANGE_PERCENTAGE_1W = format_percentage(calculate_percentage_change(previous_data['clearnet_tor_nodes'], latest_data['clearnet_tor_nodes']))

        NODE_DARKNET_COUNT = format_quantity(latest_data['tor_nodes'])
        NODE_DARKNET_PERCENTAGE = f"{round(latest_data['tor_nodes'] / (latest_data['node_count'] / 100), 2)}%"
#        NODE_DARKNET_CHANGE_1W = format_quantity(latest_data['tor_nodes'] - previous_data['tor_nodes'])
#        NODE_DARKNET_CHANGE_PERCENTAGE_1W = format_percentage(calculate_percentage_change(previous_data['tor_nodes'], latest_data['tor_nodes']))

        NODE_UNKNOWN_COUNT = format_quantity(latest_data['unannounced_nodes'])
        NODE_UNKNOWN_PERCENTAGE = f"{round(latest_data['unannounced_nodes'] / (latest_data['node_count'] / 100), 2)}%"
#        NODE_UNKNOWN_CHANGE_1W = format_quantity(latest_data['unknown_nodes'] - previous_data['unknown_nodes'])
#        NODE_UNKNOWN_CHANGE_PERCENTAGE_1W = format_percentage(calculate_percentage_change(previous_data['unknown_nodes'], latest_data['unknown_nodes']))
    
        FEE_AVG_RATE_COUNT = format_currency(latest_data['avg_fee_rate'], '', decimal=0)
#        FEE_AVG_RATE_CHANGE_1W = format_currency(latest_data['avg_fee_rate'] - previous_data['avg_fee_rate'], '', decimal=0)
#        FEE_AVG_RATE_CHANGE_PERCENTAGE_1W = format_percentage(calculate_percentage_change(previous_data['avg_fee_rate'], latest_data['avg_fee_rate']))

        FEE_BASE_AVG_RATE_COUNT = format_currency(latest_data['avg_base_fee_mtokens'], '', decimal=0)
#        FEE_BASE_AVG_RATE_CHANGE_1W = format_currency(latest_data['avg_base_fee_mtokens'] - previous_data['avg_base_fee_mtokens'], '', decimal=0)
#        FEE_BASE_AVG_RATE_CHANGE_PERCENTAGE_1W = format_percentage(calculate_percentage_change(previous_data['avg_base_fee_mtokens'], latest_data['avg_base_fee_mtokens']))

        # Format text for user presentation:
        info_network = f'[Volume]\n' \
            f'Channels: {CHANNELS}\n' \
            f'Capacity: {CAPACITY_COUNT}\n' \
            f'Avg: {CAPACITY_AVG_COUNT}/channel\n'
        info_node = f'[Nodes]\n' \
            f'Overall: {NODE_COUNT}\n' \
            f'Clearnet: {NODE_CLEARNET_PERCENTAGE} ({NODE_CLEARNET_COUNT})\n' \
            f'Greynet: {NODE_CLEARDARKNET_PERCENTAGE} ({NODE_CLEARDARKNET_COUNT})\n' \
            f'Darknet: {NODE_DARKNET_PERCENTAGE} ({NODE_DARKNET_COUNT})\n' \
            f'Unknown: {NODE_UNKNOWN_PERCENTAGE} ({NODE_UNKNOWN_COUNT})\n'
        info_fees = f'[Fees]\n' \
            f'Avg Rate: {FEE_AVG_RATE_COUNT} sats\n' \
            f'Avg Base: {FEE_BASE_AVG_RATE_COUNT} sats\n'
        info_update = f'UTC {LAST_UPDATED}\n'

        # Write text to Markdown file:
        with open (markdown_file, 'w') as markdown:
            markdown.write(f"```Lightning\n{info_network}\n{info_node}\n{info_fees}\n{info_update}```")




if __name__ == '__main__':
    
    draw_plot()
    write_markdown()