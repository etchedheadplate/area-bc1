import os
import json
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

import config
from logger import main_logger
from tools import format_currency


def draw_fees():
    # Draws Recomended Fees image with properties specified in user configuration.
    
    # User configuration related variables:
    snapshot = config.snapshots['fees']
    snapshot_file_path = snapshot['file']['path']
    snapshot_file_name = snapshot['file']['name']
    snapshot_file = snapshot_file_path + snapshot_file_name

    # Image-related variables:
    fees_image = config.images['fees']
    fees_font = fees_image['font']
    fees_colors = fees_image['colors']
    fees_background = fees_image['backgrounds']['path']
    fees_background_colors = fees_image['backgrounds']['colors']
    fees_file = fees_image['path'] + 'fees.jpg'
    fees_datetime = f'UTC {datetime.utcfromtimestamp(os.path.getctime(snapshot_file)).strftime("%Y-%m-%d %H:%M")}'

    # Get current price from Market snapshot:
    market = config.snapshots['market']
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
            fees_currency_fastest = format_currency(((fees_satvb_fastest * 140) * (market_price/ 100_000_000)), config.currency_vs_ticker, decimal=2)
            fees_currency_half_hour = format_currency(((fees_satvb_half_hour * 140) * (market_price/ 100_000_000)), config.currency_vs_ticker, decimal=2)
            fees_currency_hour = format_currency(((fees_satvb_hour * 140) * (market_price/ 100_000_000)), config.currency_vs_ticker, decimal=2)
            fees_currency_economy = format_currency(((fees_satvb_economy * 140) * (market_price/ 100_000_000)), config.currency_vs_ticker, decimal=2)
            fees_currency_minimum = format_currency(((fees_satvb_minimum * 140) * (market_price/ 100_000_000)), config.currency_vs_ticker, decimal=2)

            market_price = format_currency(market_price, config.currency_vs_ticker, decimal=2)
        else:
            fees_currency_fastest = ''
            fees_currency_half_hour = ''
            fees_currency_hour = ''
            fees_currency_economy = ''
            fees_currency_minimum = ''

            market_price = 'COULDNT LOAD'

        # Set text, position, size and color parameters:
        fees_list = [
            [{'text': 'mempool.space', 'position': fees_background_colors['api'][1], 'font_size': 36, 'text_color': fees_background_colors['api'][0]},
            {'text': f'recommended {config.currency_crypto_ticker} fees', 'position': fees_background_colors['api'][2], 'font_size': 24, 'text_color': fees_background_colors['api'][0]},
            {'text': f'{config.currency_crypto_ticker} Price: {market_price}', 'position': fees_background_colors['metric'][1], 'font_size': 30, 'text_color': fees_background_colors['metric'][0]},
            {'text': f'{fees_datetime}', 'position': fees_background_colors['metric'][2], 'font_size': 30, 'text_color': fees_background_colors['metric'][0]}],
              
            [{'text': 'Next block:', 'position': (100, 210), 'font_size': 50, 'text_color': fees_colors['blocks']},
            {'text': '1-2 blocks:', 'position': (100, 360), 'font_size': 50, 'text_color': fees_colors['blocks']},
            {'text': '2-3 blocks:', 'position': (100, 510), 'font_size': 50, 'text_color': fees_colors['blocks']},
            {'text': 'Economy:', 'position': (100, 660), 'font_size': 50, 'text_color': fees_colors['blocks']},
            {'text': 'Minimal:', 'position': (100, 810), 'font_size': 50, 'text_color': fees_colors['blocks']}],

            [{'text': '~10 minutes', 'position': (100, 265), 'font_size': 30, 'text_color': fees_colors['subblocks']},
            {'text': '~30 minutes', 'position': (100, 415), 'font_size': 30, 'text_color': fees_colors['subblocks']},
            {'text': '~60 minutes', 'position': (100, 565), 'font_size': 30, 'text_color': fees_colors['subblocks']},
            {'text': 'Whatever', 'position': (100, 715), 'font_size': 30, 'text_color': fees_colors['subblocks']},
            {'text': 'God only knows', 'position': (100, 865), 'font_size': 30, 'text_color': fees_colors['subblocks']}],

            [{'text': f'{fees_satvb_fastest} sat/vB', 'position': (550, 210), 'font_size': 110, 'text_color': fees_colors['fees_satvb_fastest']},
            {'text': f'{fees_satvb_half_hour} sat/vB', 'position': (550, 360), 'font_size': 110, 'text_color': fees_colors['fees_satvb_half_hour']},
            {'text': f'{fees_satvb_hour} sat/vB', 'position': (550, 510), 'font_size': 110, 'text_color': fees_colors['fees_satvb_hour']},
            {'text': f'{fees_satvb_economy} sat/vB', 'position': (550, 660), 'font_size': 110, 'text_color': fees_colors['fees_satvb_economy']},
            {'text': f'{fees_satvb_minimum} sat/vB', 'position': (550, 810), 'font_size': 110, 'text_color': fees_colors['fees_satvb_minimum']}],

            [{'text': f'{fees_currency_fastest}', 'position': (1275, 210), 'font_size': 110, 'text_color': fees_colors['fees_currency_fastest']},
            {'text': f'{fees_currency_half_hour}', 'position': (1275, 360), 'font_size': 110, 'text_color': fees_colors['fees_currency_half_hour']},
            {'text': f'{fees_currency_hour}', 'position': (1275, 510), 'font_size': 110, 'text_color': fees_colors['fees_currency_hour']},
            {'text': f'{fees_currency_economy}', 'position': (1275, 660), 'font_size': 110, 'text_color': fees_colors['fees_currency_economy']},
            {'text': f'{fees_currency_minimum}', 'position': (1275, 810), 'font_size': 110, 'text_color': fees_colors['fees_currency_minimum']}],
        ]

        # Open background, draw text with set parameters and save final image:
        image = Image.open(fees_background)
        draw = ImageDraw.Draw(image)

        for fees in fees_list:
            for params in fees:
                text = params.get('text')
                position = params.get('position')
                size = params.get('font_size')
                font = ImageFont.truetype(fees_font, size)
                text_color = params.get('text_color')

                draw.text(position, text, font=font, fill=text_color)

        image.save(fees_file)
        
        main_logger.info(f'[image] recommended fees drawn')

        return fees_file




if __name__ == '__main__':

    draw_fees()