import os
import json
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

import config
from tools import format_currency


def draw_info():
    # Draws Recomended Fees image with properties specified in user configuration.
    
    # User configuration related variables:
    snapshot = config.databases['snapshots']['fees']
    snapshot_file_path = snapshot['file']['path']
    snapshot_file_name = snapshot['file']['name']
    snapshot_file = snapshot_file_path + snapshot_file_name

    # Image-related variables:
    info = config.images['fees']
    info_font = info['font']
    info_colors = info['colors']
    info_background = info['backgrounds']['path']
    info_background_colors = info['backgrounds']['colors']
    info_output = info['path'] + 'fees.jpg'
    info_datetime = datetime.fromtimestamp(os.path.getctime(snapshot_file)).strftime('%Y-%m-%d %H:%M')

    # Get current price from Market snapshot:
    market = config.databases['snapshots']['market']
    market_file_path = market['file']['path']
    market_file_name = market['file']['name']
    market_file = market_file_path + market_file_name

    # Draw recommended fees with data from Fees and Market snapshots:
    with open (snapshot_file, 'r') as file:
        fees = json.load(file)

        # Get recommended fees from Fees snapshot:
        fees_satvb_fastest = fees['fastestFee']
        fees_satvb_half_hour = fees['halfHourFee']
        fees_satvb_hour = fees['hourFee']
        fees_satvb_economy = fees['economyFee']
        fees_satvb_minimum = fees['minimumFee']

        # Calculate and format currency fees from virtual bytes and current price:
        if os.path.exists(market_file):
            with open (market_file, 'r') as file:
                market_data = json.load(file)
                market_price = market_data['current_price'][f'{config.currency_vs}']

            # Transaction size assumed to be 140vB (average native SegWit):
            fees_currency_fastest = format_currency(((fees_satvb_fastest * 140) * (market_price/ 100_000_000)), config.currency_vs_ticker)
            fees_currency_half_hour = format_currency(((fees_satvb_half_hour * 140) * (market_price/ 100_000_000)), config.currency_vs_ticker)
            fees_currency_hour = format_currency(((fees_satvb_hour * 140) * (market_price/ 100_000_000)), config.currency_vs_ticker)
            fees_currency_economy = format_currency(((fees_satvb_economy * 140) * (market_price/ 100_000_000)), config.currency_vs_ticker)
            fees_currency_minimum = format_currency(((fees_satvb_minimum * 140) * (market_price/ 100_000_000)), config.currency_vs_ticker)

            market_currency_pair = config.currency_pair
            market_price = format_currency(market_price, config.currency_vs_ticker, decimal=0)
        else:
            fees_currency_fastest = ''
            fees_currency_half_hour = ''
            fees_currency_hour = ''
            fees_currency_economy = ''
            fees_currency_minimum = ''

            market_currency_pair = ''
            market_price = ''

        # Set text, position, size and color parameters:
        info_list = [
            [{'text': 'mempool.space', 'position': info_background_colors['api'][1], 'font_size': 30, 'text_color': info_background_colors['api'][0]},
            {'text': 'recommended fees by', 'position': info_background_colors['api'][2], 'font_size': 21, 'text_color': info_background_colors['api'][0]},
            {'text': f'{market_currency_pair}: {market_price}', 'position': info_background_colors['metric'][1], 'font_size': 26, 'text_color': info_background_colors['metric'][0]},
            {'text': f'{info_datetime}', 'position': info_background_colors['metric'][2], 'font_size': 26, 'text_color': info_background_colors['metric'][0]}],
              
            [{'text': 'Next block:', 'position': (100, 210), 'font_size': 50, 'text_color': info_colors['blocks']},
            {'text': '1-2 blocks:', 'position': (100, 360), 'font_size': 50, 'text_color': info_colors['blocks']},
            {'text': '2-3 blocks:', 'position': (100, 510), 'font_size': 50, 'text_color': info_colors['blocks']},
            {'text': 'Economy:', 'position': (100, 660), 'font_size': 50, 'text_color': info_colors['blocks']},
            {'text': 'Minimal:', 'position': (100, 810), 'font_size': 50, 'text_color': info_colors['blocks']}],

            [{'text': '~10 minutes', 'position': (100, 265), 'font_size': 30, 'text_color': info_colors['subblocks']},
            {'text': '~30 minutes', 'position': (100, 415), 'font_size': 30, 'text_color': info_colors['subblocks']},
            {'text': '~60 minutes', 'position': (100, 565), 'font_size': 30, 'text_color': info_colors['subblocks']},
            {'text': 'Whatever', 'position': (100, 715), 'font_size': 30, 'text_color': info_colors['subblocks']},
            {'text': 'God only knows', 'position': (100, 865), 'font_size': 30, 'text_color': info_colors['subblocks']}],

            [{'text': f'{fees_satvb_fastest} sat/vB', 'position': (550, 210), 'font_size': 110, 'text_color': info_colors['fees_satvb_fastest']},
            {'text': f'{fees_satvb_half_hour} sat/vB', 'position': (550, 360), 'font_size': 110, 'text_color': info_colors['fees_satvb_half_hour']},
            {'text': f'{fees_satvb_hour} sat/vB', 'position': (550, 510), 'font_size': 110, 'text_color': info_colors['fees_satvb_hour']},
            {'text': f'{fees_satvb_economy} sat/vB', 'position': (550, 660), 'font_size': 110, 'text_color': info_colors['fees_satvb_economy']},
            {'text': f'{fees_satvb_minimum} sat/vB', 'position': (550, 810), 'font_size': 110, 'text_color': info_colors['fees_satvb_minimum']}],

            [{'text': f'{fees_currency_fastest}', 'position': (1275, 210), 'font_size': 110, 'text_color': info_colors['fees_currency_fastest']},
            {'text': f'{fees_currency_half_hour}', 'position': (1275, 360), 'font_size': 110, 'text_color': info_colors['fees_currency_half_hour']},
            {'text': f'{fees_currency_hour}', 'position': (1275, 510), 'font_size': 110, 'text_color': info_colors['fees_currency_hour']},
            {'text': f'{fees_currency_economy}', 'position': (1275, 660), 'font_size': 110, 'text_color': info_colors['fees_currency_economy']},
            {'text': f'{fees_currency_minimum}', 'position': (1275, 810), 'font_size': 110, 'text_color': info_colors['fees_currency_minimum']}],
        ]

        # Open background, draw text with set parameters and save final image:
        image = Image.open(info_background)
        draw = ImageDraw.Draw(image)

        for info in info_list:
            for params in info:
                text = params.get('text')
                position = params.get('position')
                size = params.get('font_size')
                font = ImageFont.truetype(info_font, size)
                text_color = params.get('text_color')

                draw.text(position, text, font=font, fill=text_color)

        image.save(info_output)



draw_info()