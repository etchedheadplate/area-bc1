import json
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
    info_background = info['background']
    info_coordinates = info['coordinates']
    info_output = info['path'] + 'fees.jpg'

    price = 41234.56

    with open (snapshot_file, 'r') as file:
        fees = json.load(file)

        fees_satvb_fastest = fees['fastestFee']
        fees_satvb_half_hour = fees['halfHourFee']
        fees_satvb_hour = fees['hourFee']
        fees_satvb_economy = fees['economyFee']
        fees_satvb_minimum = fees['minimumFee']

        fees_currency_fastest = format_currency(price / 100_000_000 * fees_satvb_fastest, config.currency_vs_ticker)
        fees_currency_half_hour = format_currency(price / 100_000_000 * fees_satvb_half_hour, config.currency_vs_ticker)
        fees_currency_hour = format_currency(price / 100_000_000 * fees_satvb_hour, config.currency_vs_ticker)
        fees_currency_economy = format_currency(price / 100_000_000 * fees_satvb_economy, config.currency_vs_ticker)
        fees_currency_minimum = format_currency(price / 100_000_000 * fees_satvb_minimum, config.currency_vs_ticker)
      
        info_list = [
            [{'text': 'Next block:', 'position': (100, 110), 'font_size': 50, 'text_color': info_colors['text']},
            {'text': 'In 1-2 blocks:', 'position': (100, 285), 'font_size': 50, 'text_color': info_colors['text']},
            {'text': 'In 2-3 blocks:', 'position': (100, 460), 'font_size': 50, 'text_color': info_colors['text']},
            {'text': 'Whatever:', 'position': (100, 635), 'font_size': 50, 'text_color': info_colors['text']},
            {'text': 'Minimal:', 'position': (100, 810), 'font_size': 50, 'text_color': info_colors['text']}],
            [{'text': '~10 minutes', 'position': (100, 165), 'font_size': 40, 'text_color': info_colors['text']},
            {'text': '~30 minutes', 'position': (100, 340), 'font_size': 40, 'text_color': info_colors['text']},
            {'text': '~60 minutes', 'position': (100, 515), 'font_size': 40, 'text_color': info_colors['text']},
            {'text': 'Few hours', 'position': (100, 690), 'font_size': 40, 'text_color': info_colors['text']},
            {'text': 'God only knows', 'position': (100, 865), 'font_size': 40, 'text_color': info_colors['text']}],
            [{'text': f'{fees_satvb_fastest} sat/vB', 'position': (550, 110), 'font_size': 100, 'text_color': info_colors['fees_satvb_fastest']},
            {'text': f'{fees_satvb_half_hour} sat/vB', 'position': (550, 285), 'font_size': 100, 'text_color': info_colors['fees_satvb_half_hour']},
            {'text': f'{fees_satvb_hour} sat/vB', 'position': (550, 460), 'font_size': 100, 'text_color': info_colors['fees_satvb_hour']},
            {'text': f'{fees_satvb_economy} sat/vB', 'position': (550, 635), 'font_size': 100, 'text_color': info_colors['fees_satvb_economy']},
            {'text': f'{fees_satvb_minimum} sat/vB', 'position': (550, 810), 'font_size': 100, 'text_color': info_colors['fees_satvb_minimum']}],
            [{'text': f'~{fees_currency_fastest}', 'position': (1200, 110), 'font_size': 100, 'text_color': info_colors['fees_satvb_fastest']},
            {'text': f'~{fees_currency_half_hour}', 'position': (1200, 285), 'font_size': 100, 'text_color': info_colors['fees_satvb_half_hour']},
            {'text': f'~{fees_currency_hour}', 'position': (1200, 460), 'font_size': 100, 'text_color': info_colors['fees_satvb_hour']},
            {'text': f'~{fees_currency_economy}', 'position': (1200, 635), 'font_size': 100, 'text_color': info_colors['fees_satvb_economy']},
            {'text': f'~{fees_currency_minimum}', 'position': (1200, 810), 'font_size': 100, 'text_color': info_colors['fees_satvb_minimum']}],
        ]

        image = Image.open(info_background)

        # Создаем объект для рисования
        draw = ImageDraw.Draw(image)



        for info in info_list:
            for info_params in info:
                text = info_params.get('text')
                position = info_params.get('position')
                size = info_params.get('font_size')
                font = ImageFont.truetype(info_font, size)
                text_color = info_params.get('text_color')

                # Наносим текст на изображение
                draw.text(position, text, font=font, fill=text_color)

        # Сохраняем результат
        image.save(info_output)

draw_info()