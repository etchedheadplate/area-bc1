import io
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib

from matplotlib import font_manager
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont

sys.path.append('.')
import config
from tools import error_handler_common
from logger import main_logger



'''
Functions related to creation of diagram for Mining Pools database.

Diagram based on chart values.
'''


@error_handler_common
def draw_pools():
    # Draws Pools diagram with properties specified in user configuration.
    
    # User configuration related variables:
    chart = config.charts['pools']
    chart_file_path = chart['file']['path']
    chart_file_name = chart['file']['name']
    chart_file = chart_file_path + chart_file_name
    chart_time_till = datetime.utcfromtimestamp(os.path.getctime(chart_file)).strftime('%Y-%m-%d')
    chart_time_from = (datetime.utcfromtimestamp(os.path.getctime(chart_file)) - timedelta(days=7)).strftime('%Y-%m-%d')

    # Diagram-related variables:
    diagram = config.images['pools']
    diagram_font = font_manager.FontProperties(fname=diagram['font'])
    diagram_colors = diagram['colors']
    diagram_file = diagram['path'] + 'pools.jpg'

    background_path = diagram['backgrounds']['path']
    background_coordinates = diagram['backgrounds']['coordinates']
    background_colors = diagram['backgrounds']['colors']
    
    # Creation of diagram DataFrame and calculation of additional column:
    diagram_df = pd.read_csv(chart_file).sort_values(by='mined', ascending=False)
    
    # Calculation of additional column:
    diagram_df['percent'] = (diagram_df['mined'] / diagram_df['mined'].sum()) * 100

    # Diagram DataFrame modified to top pools slices + other pools slice:
    diagram_slices = 5
    diagram_other = pd.DataFrame({'pool': ['other'], 'mined': [diagram_df['mined'][diagram_slices:].sum()]})
    diagram_df = pd.concat([diagram_df.head(diagram_slices), diagram_other])

    # Creation of diagram figure:
    plt.figure(figsize=(9,9))
    plt.pie(diagram_df['mined'],
            autopct='%1.1f%%',
            startangle=90,
            counterclock=False,
            colors=diagram_colors['slices'],
            textprops={'fontproperties': diagram_font,
                       'size': 20,
                       'color': diagram_colors['percentage'],
                       'ha': 'center'},
                       explode=(0, 0, 0, 0, 0, 0.1))

    # Open memory buffer and save diagram to memory buffer:
    diagram_buffer = io.BytesIO()
    plt.savefig(diagram_buffer, format='png', bbox_inches='tight', transparent=True, dpi=150)
    matplotlib.pyplot.close()

    # Open background image, draw miners and save image to memory buffer:
    miners_image = Image.open(background_path)
    draw = ImageDraw.Draw(miners_image)

    # Miners-related variables:
    miners_font = diagram['font']
    miners_list = [
            [{'text': 'blockchain.com', 'position': background_colors['api'][1], 'font_size': 36, 'text_color': background_colors['api'][0]},
             {'text': 'mining pools hashrate', 'position': background_colors['api'][2], 'font_size': 25, 'text_color': background_colors['api'][0]},
             {'text': f'from: {chart_time_from}', 'position': background_colors['period'][1], 'font_size': 30, 'text_color': background_colors['period'][0]},
             {'text': f'till: {chart_time_till}', 'position': background_colors['period'][2], 'font_size': 30, 'text_color': background_colors['period'][0]}],
            
            [{'text': 'BTC mined:', 'position': (1735, 125), 'font_size': 30, 'text_color': diagram_colors['percentage']},
             {'text': 'mining pool:', 'position': (1960, 125), 'font_size': 30, 'text_color': diagram_colors['percentage']}],

            [{'text': f'{diagram_df["mined"].iloc[0]}', 'position': (1735, 185), 'font_size': 70, 'text_color': diagram_colors['bitcoin']},
            {'text': f'{diagram_df["mined"].iloc[1]}', 'position': (1735, 295), 'font_size': 70, 'text_color': diagram_colors['bitcoin']},
            {'text': f'{diagram_df["mined"].iloc[2]}', 'position': (1735, 405), 'font_size': 70, 'text_color': diagram_colors['bitcoin']},
            {'text': f'{diagram_df["mined"].iloc[3]}', 'position': (1735, 515), 'font_size': 70, 'text_color': diagram_colors['bitcoin']},
            {'text': f'{diagram_df["mined"].iloc[4]}', 'position': (1735, 625), 'font_size': 70, 'text_color': diagram_colors['bitcoin']},
            {'text': f'{diagram_df["mined"].iloc[5]}', 'position': (1735, 735), 'font_size': 70, 'text_color': diagram_colors['bitcoin']}],

            [{'text': diagram_df['pool'].iloc[0], 'position': (1960, 185), 'font_size': 70, 'text_color': diagram_colors['slices'][0]},
            {'text': diagram_df['pool'].iloc[1], 'position': (1960, 295), 'font_size': 70, 'text_color': diagram_colors['slices'][1]},
            {'text': diagram_df['pool'].iloc[2], 'position': (1960, 405), 'font_size': 70, 'text_color': diagram_colors['slices'][2]},
            {'text': diagram_df['pool'].iloc[3], 'position': (1960, 515), 'font_size': 70, 'text_color': diagram_colors['slices'][3]},
            {'text': diagram_df['pool'].iloc[4], 'position': (1960, 625), 'font_size': 70, 'text_color': diagram_colors['slices'][4]},
            {'text': diagram_df['pool'].iloc[5], 'position': (1960, 735), 'font_size': 70, 'text_color': diagram_colors['slices'][5]}]
    ]

    for miner in miners_list:
        for miner_params in miner:
            text = miner_params.get('text')
            position = miner_params.get('position')
            size = miner_params.get('font_size')
            font = ImageFont.truetype(miners_font, size)
            text_color = miner_params.get('text_color')

            draw.text(position, text, font=font, fill=text_color)

    miners_buffer = io.BytesIO()
    miners_image.save(miners_buffer, 'PNG')

    # Overlay diagram buffer with miners buffer and save final image:
    background_image = Image.open(miners_buffer).convert("RGB")
    miners_buffer.seek(0)
    background_overlay = Image.open(diagram_buffer)
    diagram_buffer.seek(0)

    background_image.paste(background_overlay, background_coordinates, mask=background_overlay)
    background_image.save(diagram_file, "JPEG", quality=90, icc_profile=background_image.info.get('icc_profile', ''))
    miners_buffer.close()
    diagram_buffer.close()

    main_logger.info(f'[image] pools diagram drawn')

    return diagram_file




if __name__ == '__main__':

    draw_pools()




