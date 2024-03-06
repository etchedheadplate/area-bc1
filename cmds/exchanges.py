import io
import os
import sys
import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib

from matplotlib import font_manager
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont

sys.path.append('.')
import config
from tools import error_handler_common, format_amount
from logger import main_logger



'''
Functions related to creation of diagram for Exchanges database.

Diagram based on snapshot values.
'''


@error_handler_common
def draw_exchanges():
    # Draws exchanges diagram with properties specified in user configuration.
    
    # User configuration related variables:
    snapshot = config.snapshots['exchanges']
    snapshot_file_path = snapshot['file']['path']
    snapshot_file_name = snapshot['file']['name']
    snapshot_file = snapshot_file_path + snapshot_file_name
    snapshot_time_till = datetime.utcfromtimestamp(os.path.getctime(snapshot_file)).strftime('%Y-%m-%d')
    snapshot_time_from = (datetime.utcfromtimestamp(os.path.getctime(snapshot_file)) - timedelta(days=1)).strftime('%Y-%m-%d')

    # Diagram-related variables:
    diagram = config.images['exchanges']
    diagram_font = font_manager.FontProperties(fname=diagram['font'])
    diagram_colors = diagram['colors']
    diagram_file = diagram['path'] + 'exchanges.jpg'

    background_path = diagram['backgrounds']['path']
    background_coordinates = diagram['backgrounds']['coordinates']
    background_colors = diagram['backgrounds']['colors']
    
    with open (snapshot_file, 'r') as json_file:
        
        snapshot_data = json.load(json_file)

        exchanges_list = []
        for exchange in snapshot_data:
            exchange_name = exchange['name']
            if 'Exchange' in exchange_name:
                exchange_name = exchange_name.replace('Exchange', '')
            exchange_trade = exchange['trade_volume_24h_btc_normalized']
            exchanges_list.append([exchange_name, exchange_trade])

        # Creation of diagram DataFrame and calculation of additional column:
        diagram_df = pd.DataFrame(exchanges_list, columns=['exchange', 'trade'])
        
        # Calculation of additional column:
        diagram_df['percent'] = (diagram_df['trade'] / diagram_df['trade'].sum()) * 100

        # Diagram DataFrame modified to top exchanges slices + other exchanges slice:
        diagram_slices = 5
        diagram_other = pd.DataFrame({'exchange': ['other'], 'trade': [diagram_df['trade'][diagram_slices:].sum()]})
        diagram_df = pd.concat([diagram_df.head(diagram_slices), diagram_other])

        # Creation of diagram figure:
        plt.figure(figsize=(9,9))
        plt.pie(diagram_df['trade'],
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
                [{'text': 'coingecko.com', 'position': background_colors['api'][1], 'font_size': 36, 'text_color': background_colors['api'][0]},
                {'text': 'CEX trading volume', 'position': background_colors['api'][2], 'font_size': 26, 'text_color': background_colors['api'][0]}],
                
                [{'text': f'BTC Traded:', 'position': (1700, 125), 'font_size': 30, 'text_color': diagram_colors['percentage']},
                {'text': 'Exchange:', 'position': (2000, 125), 'font_size': 30, 'text_color': diagram_colors['percentage']},
                {'text': f'from: {snapshot_time_from}', 'position': background_colors['period'][1], 'font_size': 30, 'text_color': background_colors['period'][0]},
                {'text': f'till: {snapshot_time_till}', 'position': background_colors['period'][2], 'font_size': 30, 'text_color': background_colors['period'][0]}],

                [{'text': format_amount(diagram_df["trade"].iloc[0]), 'position': (1700, 185), 'font_size': 70, 'text_color': diagram_colors['bitcoin']},
                {'text': format_amount(diagram_df["trade"].iloc[1]), 'position': (1700, 295), 'font_size': 70, 'text_color': diagram_colors['bitcoin']},
                {'text': format_amount(diagram_df["trade"].iloc[2]), 'position': (1700, 405), 'font_size': 70, 'text_color': diagram_colors['bitcoin']},
                {'text': format_amount(diagram_df["trade"].iloc[3]), 'position': (1700, 515), 'font_size': 70, 'text_color': diagram_colors['bitcoin']},
                {'text': format_amount(diagram_df["trade"].iloc[4]), 'position': (1700, 625), 'font_size': 70, 'text_color': diagram_colors['bitcoin']},
                {'text': format_amount(diagram_df["trade"].iloc[5]), 'position': (1700, 735), 'font_size': 70, 'text_color': diagram_colors['bitcoin']}],

                [{'text': diagram_df['exchange'].iloc[0], 'position': (2000, 185), 'font_size': 70, 'text_color': diagram_colors['slices'][0]},
                {'text': diagram_df['exchange'].iloc[1], 'position': (2000, 295), 'font_size': 70, 'text_color': diagram_colors['slices'][1]},
                {'text': diagram_df['exchange'].iloc[2], 'position': (2000, 405), 'font_size': 70, 'text_color': diagram_colors['slices'][2]},
                {'text': diagram_df['exchange'].iloc[3], 'position': (2000, 515), 'font_size': 70, 'text_color': diagram_colors['slices'][3]},
                {'text': diagram_df['exchange'].iloc[4], 'position': (2000, 625), 'font_size': 70, 'text_color': diagram_colors['slices'][4]},
                {'text': diagram_df['exchange'].iloc[5], 'position': (2000, 735), 'font_size': 70, 'text_color': diagram_colors['slices'][5]}]
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

        main_logger.info(f'{diagram_file} drawn')

        return diagram_file




if __name__ == '__main__':

    draw_exchanges()