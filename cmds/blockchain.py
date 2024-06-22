import os
import sys
import json
import time
import pandas as pd

from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

sys.path.append('.')
import config
from logger import main_logger
from tools import (error_handler_common,
                   get_api_data,
                   format_quantity,
                   convert_timestamp_to_utc,
                   format_currency)



'''
Functions related to creation of image and markdown files for Blockhain data.

Image and markdown files based on API response data.
'''


@error_handler_common
def explore_address(address):
    
    address_base = 'https://blockchain.info/'
    address_endpoint = f'rawaddr/{address}'
    address_response = get_api_data(address_base, address_endpoint).json()
    address_path = 'db/blockchain/address/'
    address_markdown_file = address_path + f'address_{address}.md'

    if 'error' in address_response.keys():
        return False
    
    if not os.path.isdir(address_path):
        os.makedirs(address_path, exist_ok=True)
    
    # Get current price from Market snapshot:
    market_current = config.snapshots['market']
    market_current_file_path = market_current['file']['path']
    market_current_file_name = market_current['file']['name']
    market_current_file = market_current_file_path + market_current_file_name

    # Creation of key address variables:
    ADDRESS_DATE_CURRENT = datetime.utcnow().strftime("%Y-%m-%d %H:%M")

    if os.path.exists(market_current_file):
        with open (market_current_file, 'r') as file:
            market_current_data = json.load(file)
            market_current_price = market_current_data['current_price'][f'{config.currency_vs}']
        ADDRESS_FIAT_CURRENT_PRICE = format_currency(market_current_price, config.currency_vs_ticker, decimal=2)
        ADDRESS_FIAT_BALANCE = format_currency(market_current_price / 100_000_000 * address_response['final_balance'], config.currency_vs_ticker, decimal=2)
    else:
        ADDRESS_FIAT_CURRENT_PRICE = 'COULDNT LOAD'
        ADDRESS_FIAT_BALANCE = 'COULDNT LOAD'

    address_transactions_limit = 5
    address_transactions_list = []
    for address_transaction in address_response['txs']:
        ADDRESS_TRANSACTION_HASH = address_transaction['hash']
        ADDRESS_TRANSACTION_DATE = convert_timestamp_to_utc(address_transaction['time'])
        address_result = address_transaction['result']
        if address_result < 0:
            ADDRESS_TRANSACTION_CRYPTO_AMOUNT = f'- {format_currency(abs(address_result) / 100_000_000, config.currency_crypto_ticker, decimal=8)}'
        else:
            ADDRESS_TRANSACTION_CRYPTO_AMOUNT = f'+ {format_currency(abs(address_result) / 100_000_000, config.currency_crypto_ticker, decimal=8)}'
        address_transactions_list.append([ADDRESS_TRANSACTION_HASH, ADDRESS_TRANSACTION_DATE, ADDRESS_TRANSACTION_CRYPTO_AMOUNT])
    ADDRESS_TRANSACTIONS_COUNT = len(address_transactions_list) if len(address_transactions_list) < 100 else '99+'
    ADDRESS_TRANSACTIONS_MORE = len(address_transactions_list) - address_transactions_limit if len(address_transactions_list) - address_transactions_limit < 95 else '95+'

    ADDRESS_UTXO = address_response['n_unredeemed']
    ADDRESS_HASH160 = address_response['hash160']
    ADDRESS_CRYPTO_RECIEVED = format_currency(address_response['total_received'] / 100_000_000, decimal=8)
    ADDRESS_CRYPTO_SENT = format_currency(address_response['total_sent'] / 100_000_000, decimal=8)
    ADDRESS_CRYPTO_BALANCE = format_currency(address_response['final_balance'] / 100_000_000, decimal=8)
    if address[0] == '1':
        ADDRESS_TYPE = 'P2PKH'
    elif address[0] == '3':
        ADDRESS_TYPE = 'P2SH'
    elif address[0:3] == 'bc1':
        ADDRESS_TYPE = 'Bech32'
    else:
        ADDRESS_TYPE = 'Unknown'
    
    # Address image variables:
    address_image = config.images['address']
    address_image_font = address_image['font']
    address_image_colors = address_image['colors']
    address_image_background_path = address_image['backgrounds']['path']
    address_image_background_colors = address_image['backgrounds']['colors']
    address_image_file = address_image['path'] + f'address_{address}.jpg'

    # Set text, position, size and color address parameters:
    address_title_list = [
        [{'text': 'blockchain.com', 'position': address_image_background_colors['api'][1], 'font_size': 36, 'text_color': address_image_background_colors['api'][0]},
        {'text': f'address information', 'position': address_image_background_colors['api'][2], 'font_size': 27, 'text_color': address_image_background_colors['api'][0]},
        {'text': f'{config.currency_crypto_ticker} Price: {ADDRESS_FIAT_CURRENT_PRICE}', 'position': address_image_background_colors['metric'][1], 'font_size': 31, 'text_color': address_image_background_colors['metric'][0]},
        {'text': f'UTC {ADDRESS_DATE_CURRENT}', 'position': address_image_background_colors['metric'][2], 'font_size': 31, 'text_color': address_image_background_colors['metric'][0]}],
            
        [{'text': f'{ADDRESS_CRYPTO_BALANCE}', 'position': (950, 245), 'font_size': 130, 'text_color': address_image_colors['titles_crypto']},
        {'text': f'Current {config.currency_crypto_ticker} Balance', 'position': (950, 370), 'font_size': 30, 'text_color': address_image_colors['titles']}],

        [{'text': f'{ADDRESS_FIAT_BALANCE}', 'position': (950, 500), 'font_size': 50, 'text_color': address_image_colors['titles_fiat']},
        {'text': f'Current {config.currency_vs_ticker} Balance', 'position': (950, 555), 'font_size': 30, 'text_color': address_image_colors['titles']},
        {'text': f'{ADDRESS_CRYPTO_RECIEVED}', 'position': (950, 650), 'font_size': 50, 'text_color': address_image_colors['titles_crypto']},
        {'text': f'{config.currency_crypto_ticker} Recieved', 'position': (950, 705), 'font_size': 30, 'text_color': address_image_colors['titles']},
        {'text': f'{ADDRESS_CRYPTO_SENT}', 'position': (950, 800), 'font_size': 50, 'text_color': address_image_colors['titles_crypto']},
        {'text': f'{config.currency_crypto_ticker} Sent', 'position': (950, 855), 'font_size': 30, 'text_color': address_image_colors['titles']}],

        [{'text': f'{ADDRESS_UTXO}', 'position': (1650, 500), 'font_size': 50, 'text_color': address_image_colors['titles_other']},
        {'text': 'UTXO', 'position': (1650, 555), 'font_size': 30, 'text_color': address_image_colors['titles']},
        {'text': f'{ADDRESS_TRANSACTIONS_COUNT}', 'position': (1650, 650), 'font_size': 50, 'text_color': address_image_colors['titles_other']},
        {'text': 'Transactions', 'position': (1650, 705), 'font_size': 30, 'text_color': address_image_colors['titles']},
        {'text': f'{ADDRESS_TYPE}', 'position': (1650, 800), 'font_size': 50, 'text_color': address_image_colors['titles_other']},
        {'text': 'Type', 'position': (1650, 855), 'font_size': 30, 'text_color': address_image_colors['titles']}]
    ]

    # Open background, draw text with set parameters and save final address image:
    address_image = Image.open(address_image_background_path)
    address_draw = ImageDraw.Draw(address_image)
    for address_title in address_title_list:
        for address_params in address_title:
            address_text = address_params.get('text')
            address_position = address_params.get('position')
            address_size = address_params.get('font_size')
            address_font = ImageFont.truetype(address_image_font, address_size)
            address_text_color = address_params.get('text_color')
            address_draw.text(address_position, address_text, font=address_font, fill=address_text_color)
    address_image.save(address_image_file)
    main_logger.info(f'{address_image_file} drawn')

    # Creation of address markdown file:
    with open (address_markdown_file, 'w') as address_markdown:
        address_text = f'Address: {address}\n' \
        f'Hash160: {ADDRESS_HASH160}\n'
        address_transactions = f'[{ADDRESS_TRANSACTIONS_COUNT} Transactions]\n'
        for ADDRESS_TRANSACTION_HASH, ADDRESS_TRANSACTION_DATE, ADDRESS_TRANSACTION_CRYPTO_AMOUNT in address_transactions_list[:5]:
            address_transactions += f'UTC {ADDRESS_TRANSACTION_DATE} --> {ADDRESS_TRANSACTION_CRYPTO_AMOUNT}\n'
            address_transactions += f'{ADDRESS_TRANSACTION_HASH}\n'
        if len(address_transactions_list) > address_transactions_limit:
            address_transactions += f'...and {ADDRESS_TRANSACTIONS_MORE} more transactions\n'
        address_explorers = f'[blockstream.info](https://blockstream.info/address/{address})\n' \
            f'[blockchain.com](https://www.blockchain.com/explorer/addresses/btc/{address})\n' \
            f'[mempool.space](https://mempool.space/address/{address})'
        address_markdown.write(f'```Address\n{address_text}\n{address_transactions}```{address_explorers}')
        main_logger.info(f'{address_markdown_file} written')

    return address_image_file, address_markdown_file


@error_handler_common
def explore_block(block):
    
    block_base = 'https://blockchain.info/'
    block_endpoint = f'block-height/{block}'
    block_response = get_api_data(block_base, block_endpoint).json()
    block_path = 'db/blockchain/block/'
    block_markdown_file = block_path + f'block_{block}.md'
    
    if 'error' in block_response.keys():
        return False
    
    block_response = block_response['blocks'][0]

    if not os.path.isdir(block_path):
        os.makedirs(block_path, exist_ok=True)
    
    # Creation of key block variables:
    BLOCK = format_quantity(int(block))
    BLOCK_HASH = block_response['hash']
    BLOCK_MERKLE = block_response['mrkl_root']
    BLOCK_BITS = block_response['bits']
    BLOCK_NONCE = block_response['nonce']
    BLOCK_TRANSACTIONS_COUNT = format_quantity(block_response['n_tx'])
    BLOCK_SIZE = format_quantity(block_response['size'])
    BLOCK_WEIGHT = format_quantity(block_response['weight'])
    BLOCK_LATEST = get_api_data(block_base, 'latestblock').json()['height']
    BLOCK_DEPTH = format_quantity(BLOCK_LATEST - int(block))

    BLOCK_DATE_CURRENT = datetime.utcnow().timestamp()
    BLOCK_DATE_MINED = convert_timestamp_to_utc(block_response['time'])
    BLOCK_DATE_AGE = (datetime.utcfromtimestamp(BLOCK_DATE_CURRENT) - datetime.utcfromtimestamp(block_response['time'])).days
    
    BLOCK_CRYPTO_FEE = format_currency(block_response['fee'])
    BLOCK_CRYPTO_AMOUNT = 0
    for block_transaction in block_response['tx']:
        for block_output in block_transaction['out']:
            BLOCK_CRYPTO_AMOUNT = BLOCK_CRYPTO_AMOUNT + block_output['value']
    BLOCK_CRYPTO_AMOUNT = format_currency(BLOCK_CRYPTO_AMOUNT / 100_000_000)

    # Block image variables:
    block_image = config.images['block']
    block_image_font = block_image['font']
    block_image_colors = block_image['colors']
    block_image_background_path = block_image['backgrounds']['path']
    block_image_background_colors = block_image['backgrounds']['colors']
    block_image_file = block_image['path'] + f'block_{block}.jpg'

    # Set text, position, size and color block parameters:
    block_title_list = [
        [{'text': 'blockchain.com', 'position': block_image_background_colors['api'][1], 'font_size': 36, 'text_color': block_image_background_colors['api'][0]},
        {'text': f'block status details', 'position': block_image_background_colors['api'][2], 'font_size': 26, 'text_color': block_image_background_colors['api'][0]},
        {'text': f'Height {BLOCK}', 'position': block_image_background_colors['metric'][1], 'font_size': 31, 'text_color': block_image_background_colors['metric'][0]},
        {'text': f'Mined {BLOCK_DATE_AGE} days ago', 'position': block_image_background_colors['metric'][2], 'font_size': 31, 'text_color': block_image_background_colors['metric'][0]}],
            
        [{'text': f'{BLOCK_CRYPTO_AMOUNT}', 'position': (950, 245), 'font_size': 130, 'text_color': block_image_colors['titles_crypto']},
        {'text': f'{config.currency_crypto_ticker} Moved', 'position': (950, 370), 'font_size': 30, 'text_color': block_image_colors['titles']}],

        [{'text': f'{BLOCK_CRYPTO_FEE}', 'position': (950, 500), 'font_size': 50, 'text_color': block_image_colors['titles_crypto']},
        {'text': f'Fees, sats', 'position': (950, 555), 'font_size': 30, 'text_color': block_image_colors['titles']},
        {'text': f'{BLOCK_WEIGHT}', 'position': (950, 650), 'font_size': 50, 'text_color': block_image_colors['titles_other']},
        {'text': f'Weight, WU', 'position': (950, 705), 'font_size': 30, 'text_color': block_image_colors['titles']},
        {'text': f'{BLOCK_SIZE}', 'position': (950, 800), 'font_size': 50, 'text_color': block_image_colors['titles_other']},
        {'text': f'Size, bytes', 'position': (950, 855), 'font_size': 30, 'text_color': block_image_colors['titles']}],

        [{'text': f'{BLOCK_DEPTH}', 'position': (1650, 500), 'font_size': 50, 'text_color': block_image_colors['titles_other']},
        {'text': 'Depth', 'position': (1650, 555), 'font_size': 30, 'text_color': block_image_colors['titles']},
        {'text': f'{BLOCK_TRANSACTIONS_COUNT}', 'position': (1650, 650), 'font_size': 50, 'text_color': block_image_colors['titles_other']},
        {'text': 'Transactions', 'position': (1650, 705), 'font_size': 30, 'text_color': block_image_colors['titles']},
        {'text': f'{BLOCK_DATE_MINED}', 'position': (1650, 800), 'font_size': 50, 'text_color': block_image_colors['titles_other']},
        {'text': 'Mined at, UTC', 'position': (1650, 855), 'font_size': 30, 'text_color': block_image_colors['titles']}]
    ]

    # Open background, draw text with set parameters and save final block image:
    block_image = Image.open(block_image_background_path)
    block_draw = ImageDraw.Draw(block_image)
    for block_title in block_title_list:
        for block_params in block_title:
            block_text = block_params.get('text')
            block_position = block_params.get('position')
            block_size = block_params.get('font_size')
            block_font = ImageFont.truetype(block_image_font, block_size)
            block_text_color = block_params.get('text_color')
            block_draw.text(block_position, block_text, font=block_font, fill=block_text_color)
    block_image.save(block_image_file)
    main_logger.info(f'{block_image_file} drawn')

    # Creation of block markdown file:
    with open (block_markdown_file, 'w') as block_markdown:
        block_text = f'Height: {BLOCK}\n' \
            f'Bits: {BLOCK_BITS}\n' \
            f'Nonce: {BLOCK_NONCE}\n' \
            f'\nHash: {BLOCK_HASH}\n' \
            f'\nMerkle: {BLOCK_MERKLE}\n'
        block_explorers = f'[blockstream.info](https://blockstream.info/block/{BLOCK_HASH})\n' \
            f'[blockchain.com](https://www.blockchain.com/explorer/blocks/btc/{block})\n' \
            f'[mempool.space](https://mempool.space/block/{BLOCK_HASH})'
        block_markdown.write(f'```Block\n{block_text}```{block_explorers}')
        main_logger.info(f'{block_markdown_file} written')
    
    return block_image_file, block_markdown_file


@error_handler_common    
def explore_transaction(transaction_hash):
    
    transaction_base = 'https://blockchain.info/'
    transaction_endpoint = f'rawtx/{transaction_hash}'
    transaction_response = get_api_data(transaction_base, transaction_endpoint).json()
    transaction_path = 'db/blockchain/transaction/'
    transaction_markdown_file = transaction_path + f'transaction_{transaction_hash}.md'

    if 'error' in transaction_response.keys():
        return False
    
    if not os.path.isdir(transaction_path):
        os.makedirs(transaction_path, exist_ok=True)

    # Get current price from Market Max Days chart:
    market_days_max = config.charts['market_days_max']
    market_days_max_file_path = market_days_max['file']['path']
    market_days_max_file_name = market_days_max['file']['name']
    market_days_max_file = market_days_max_file_path + market_days_max_file_name

    # Creation of key transaction variables:
    TRANSACTION_BLOCK_LATEST = get_api_data(transaction_base, 'latestblock').json()['height']

    TRANSACTION_DATE_CURRENT = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
    TRANSACTION_DATE_TIME = convert_timestamp_to_utc(transaction_response['time'])[:16]
    TRANSACTION_DAY = transaction_response['time'] * 1_000

    TRANSACTION_VERSION = transaction_response['ver']
    if TRANSACTION_VERSION == 1:
        TRANSACTION_VERSION = '1 (Legacy)'
    elif TRANSACTION_VERSION == 2:
        TRANSACTION_VERSION = '2 (SegWit)'
    else:
        TRANSACTION_VERSION = TRANSACTION_VERSION

    TRANSACTION_INDEX = transaction_response['tx_index']
    TRANSACTION_SIZE = format_quantity(transaction_response['size'])
    TRANSACTION_WEIGHT = format_quantity(transaction_response['weight'])
    TRANSACTION_DOUBLE_SPEND = 'Not Detected' if transaction_response['double_spend'] == False else 'Detected'
    TRANSACTION_HEIGHT = 'Unconfirmed' if transaction_response['block_height'] == None else format_quantity(transaction_response['block_height'])
    TRANSACTION_CONFIRMATIONS = 'Unconfirmed' if transaction_response['block_height'] == None else f'{format_quantity(TRANSACTION_BLOCK_LATEST - transaction_response["block_height"] + 1)} Confirmations'
    
    TRANSACTION_CRYPTO_FEE = format_currency(transaction_response['fee'])
    TRANSACTION_CRYPTO_AMOUNT = 0
    transaction_inputs_list = []
    for transaction_input in transaction_response['inputs']:
        TRANSACTION_INPUT_ADDRESS = transaction_input['prev_out']['addr']
        TRANSACTION_INPUT_CRYPTO_AMOUNT = format_currency(transaction_input['prev_out']['value'] / 100_000_000, config.currency_crypto_ticker, decimal=8)
        transaction_inputs_list.append([TRANSACTION_INPUT_ADDRESS, TRANSACTION_INPUT_CRYPTO_AMOUNT])
    transaction_outputs_list = []
    for transaction_output in transaction_response['out']:
        if 'addr' in transaction_output.keys():
            TRANSACTION_OUTPUT_ADDRESS = transaction_output['addr']
            TRANSACTION_OUTPUT_CRYPTO_AMOUNT = format_currency(transaction_output['value'] / 100_000_000, config.currency_crypto_ticker, decimal=8)
            TRANSACTION_CRYPTO_AMOUNT = TRANSACTION_CRYPTO_AMOUNT + transaction_output['value']
            transaction_outputs_list.append([TRANSACTION_OUTPUT_ADDRESS, TRANSACTION_OUTPUT_CRYPTO_AMOUNT])
        else:
            pass
    if os.path.exists(market_days_max_file):
        market_days_max_df = pd.read_csv(market_days_max_file)
        if TRANSACTION_DAY < market_days_max_df['date'][0]:
            TRANSACTION_FIAT_AMOUNT = 'COULDNT LOAD'
            TRANSACTION_FIAT_FEE = 'COULDNT LOAD'
        else:
            market_transaction_nearest_day = market_days_max_df.iloc[(market_days_max_df['date'] - TRANSACTION_DAY).abs().argsort()[:1]]['date'].values[0]
            market_transaction_nearest_price = market_days_max_df.loc[market_days_max_df['date'] == market_transaction_nearest_day, 'price'].values[0]
            TRANSACTION_FIAT_AMOUNT = format_currency(TRANSACTION_CRYPTO_AMOUNT * market_transaction_nearest_price / 100_000_000, config.currency_vs_ticker, decimal=2)
            TRANSACTION_FIAT_FEE = format_currency(transaction_response['fee'] * market_transaction_nearest_price / 100_000_000, config.currency_vs_ticker, decimal=2)
    else:
        TRANSACTION_FIAT_AMOUNT = 'COULDNT LOAD'
        TRANSACTION_FIAT_FEE = 'COULDNT LOAD'
    TRANSACTION_CRYPTO_AMOUNT = format_currency(TRANSACTION_CRYPTO_AMOUNT / 100_000_000)

    transaction_inputs_limit = 5
    TRANSACTION_INPUTS_COUNT = len(transaction_inputs_list) if len(transaction_inputs_list) < 100 else '99+'
    TRANSACTION_INPUTS_MORE = len(transaction_inputs_list) - transaction_inputs_limit if len(transaction_inputs_list) - transaction_inputs_limit < 95 else '95+'
    transaction_outputs_limit = 5
    TRANSACTION_OUTPUTS_COUNT = len(transaction_outputs_list) if len(transaction_outputs_list) < 100 else '99+'
    TRANSACTION_OUTPUTS_MORE = len(transaction_outputs_list) - transaction_outputs_limit if len(transaction_outputs_list) - transaction_outputs_limit < 95 else '95+'

    # Transaction image variables:
    transaction_image = config.images['transaction']
    transaction_image_font = transaction_image['font']
    transaction_image_colors = transaction_image['colors']
    transaction_image_background = transaction_image['backgrounds']['key_metric_down'] if transaction_response['block_height'] == None else transaction_image['backgrounds']['key_metric_up']
    transaction_image_double_spend = transaction_image['backgrounds']['key_metric_down']['colors'] if TRANSACTION_DOUBLE_SPEND == 'Detected' else transaction_image['backgrounds']['key_metric_up']['colors']
    transaction_image_background_path = transaction_image_background['path']
    transaction_image_background_colors = transaction_image_background['colors']
    transaction_image_file = transaction_image['path'] + f'transaction_{transaction_hash}.jpg'

    # Set text, position, size and color transaction parameters:
    transaction_title_list = [
        [{'text': 'blockchain.com', 'position': transaction_image_background_colors['api'][1], 'font_size': 36, 'text_color': transaction_image_background_colors['api'][0]},
        {'text': f'transaction overview', 'position': transaction_image_background_colors['api'][2], 'font_size': 26, 'text_color': transaction_image_background_colors['api'][0]},
        {'text': f'{TRANSACTION_CONFIRMATIONS}', 'position': transaction_image_background_colors['metric'][1], 'font_size': 31, 'text_color': transaction_image_background_colors['metric'][0]},
        {'text': f'UTC {TRANSACTION_DATE_CURRENT}', 'position': transaction_image_background_colors['metric'][2], 'font_size': 31, 'text_color': transaction_image_background_colors['metric'][0]}],
            
        [{'text': f'{TRANSACTION_CRYPTO_AMOUNT}', 'position': (100, 245), 'font_size': 130, 'text_color': transaction_image_colors['titles_crypto']},
        {'text': f'{config.currency_crypto_ticker} transfered', 'position': (100, 360), 'font_size': 30, 'text_color': transaction_image_colors['titles']}],

        [{'text': f'{TRANSACTION_CRYPTO_FEE}', 'position': (100, 500), 'font_size': 50, 'text_color': transaction_image_colors['titles_crypto']},
        {'text': f'Fee, sats', 'position': (100, 555), 'font_size': 30, 'text_color': transaction_image_colors['titles']},
        {'text': f'{TRANSACTION_FIAT_AMOUNT}', 'position': (100, 650), 'font_size': 50, 'text_color': transaction_image_colors['titles_fiat']},
        {'text': f'{config.currency_vs_ticker} transfered', 'position': (100, 705), 'font_size': 30, 'text_color': transaction_image_colors['titles']},
        {'text': f'{TRANSACTION_FIAT_FEE}', 'position': (100, 800), 'font_size': 50, 'text_color': transaction_image_colors['titles_fiat']},
        {'text': f'Fee, {config.currency_vs_ticker}', 'position': (100, 855), 'font_size': 30, 'text_color': transaction_image_colors['titles']}],

        [{'text': f'{TRANSACTION_HEIGHT}', 'position': (575, 500), 'font_size': 50, 'text_color': transaction_image_colors['titles_other']},
        {'text': f'Height', 'position': (575, 555), 'font_size': 30, 'text_color': transaction_image_colors['titles']},
        {'text': f'{TRANSACTION_WEIGHT}', 'position': (575, 650), 'font_size': 50, 'text_color': transaction_image_colors['titles_other']},
        {'text': f'Weight, WU', 'position': (575, 705), 'font_size': 30, 'text_color': transaction_image_colors['titles']},
        {'text': f'{TRANSACTION_SIZE}', 'position': (575, 800), 'font_size': 50, 'text_color': transaction_image_colors['titles_other']},
        {'text': f'Size, bytes', 'position': (575, 855), 'font_size': 30, 'text_color': transaction_image_colors['titles']}],

        [{'text': f'{TRANSACTION_VERSION}', 'position': (1050, 500), 'font_size': 50, 'text_color': transaction_image_colors['titles_other']},
        {'text': 'Version', 'position': (1050, 555), 'font_size': 30, 'text_color': transaction_image_colors['titles']},
        {'text': f'{TRANSACTION_DOUBLE_SPEND}', 'position': (1050, 650), 'font_size': 50, 'text_color': transaction_image_double_spend['metric'][0]},
        {'text': 'Double Spend', 'position': (1050, 705), 'font_size': 30, 'text_color': transaction_image_colors['titles']},
        {'text': f'{TRANSACTION_DATE_TIME}', 'position': (1050, 800), 'font_size': 50, 'text_color': transaction_image_colors['titles_other']},
        {'text': 'Broadcasted at, UTC', 'position': (1050, 855), 'font_size': 30, 'text_color': transaction_image_colors['titles']}]
    ]

    # Open background, draw text with set parameters and save final transaction image:
    transaction_image = Image.open(transaction_image_background_path)
    transaction_draw = ImageDraw.Draw(transaction_image)

    for transaction_title in transaction_title_list:
        for transaction_params in transaction_title:
            transaction_text = transaction_params.get('text')
            transaction_position = transaction_params.get('position')
            transaction_size = transaction_params.get('font_size')
            transaction_font = ImageFont.truetype(transaction_image_font, transaction_size)
            transaction_text_color = transaction_params.get('text_color')
            transaction_draw.text(transaction_position, transaction_text, font=transaction_font, fill=transaction_text_color)
    transaction_image.save(transaction_image_file)
    main_logger.info(f'{transaction_image_file} drawn')

    # Creation of transaction markdown file:
    with open (transaction_markdown_file, 'w') as transaction_markdown:
        transaction_text = f'Transaction: {transaction_hash}\n' \
            f'Index: {TRANSACTION_INDEX}\n'
        transaction_inputs = f'[{TRANSACTION_INPUTS_COUNT} Inputs]\n'
        for TRANSACTION_INPUT_ADDRESS, TRANSACTION_INPUT_CRYPTO_AMOUNT in transaction_inputs_list[:5]:
            transaction_inputs += f'{TRANSACTION_INPUT_ADDRESS} --> {TRANSACTION_INPUT_CRYPTO_AMOUNT}\n'
        if len(transaction_inputs_list) > 5:
            transaction_inputs += f'...and {TRANSACTION_INPUTS_MORE} more inputs\n'
        transaction_outputs = f'[{TRANSACTION_OUTPUTS_COUNT} Outputs]\n'
        for TRANSACTION_OUTPUT_ADDRESS, TRANSACTION_OUTPUT_CRYPTO_AMOUNT in transaction_outputs_list[:5]:
            transaction_outputs += f'{TRANSACTION_OUTPUT_CRYPTO_AMOUNT} --> {TRANSACTION_OUTPUT_ADDRESS}\n'
        if len(transaction_outputs_list) > 5:
            transaction_outputs += f'...and {TRANSACTION_OUTPUTS_MORE} more inputs\n'
        transaction_explorers = f'[blockstream.info](https://blockstream.info/tx/{transaction_hash})\n' \
            f'[blockchain.com](https://www.blockchain.com/explorer/transactions/btc/{transaction_hash})\n' \
            f'[mempool.space](https://mempool.space/tx/{transaction_hash})'
        transaction_markdown.write(f'```Transaction\n{transaction_text}\n{transaction_inputs}\n{transaction_outputs}```{transaction_explorers}')
        main_logger.info(f'{transaction_markdown_file} written')
    
    return transaction_image_file, transaction_markdown_file




if __name__ == '__main__':

    test_add = ['1P5ZEDWTKTFGxQjZphgWPQUpe554WKDfHQ', # P2PKH
                 '36EEHh9ME3kU7AZ3rUxBCyKR5FhR3RbqVo', # P2SH
                 'bc1q28x9udhvjp8jzwmmpsv7ehzw8za60c7g62xauh'] # Bech32
#    for add in test_add:
#        explore_address(add)
#        time.sleep(10)

    test_blk = ['828282',
                '481824',
                '1']
#    for blk in test_blk:
#        explore_block(blk)
#        time.sleep(10)
    
    test_trx = ['a1075db55d416d3ca199f55b6084e2115b9345e16c5cf302fc80e9d5fbf5d48d',
                'd7e7af6a06c16ab16653879ba5a299dae8fa4e95e91fcb0bf94f03e1b3b64149',
                'eb08b6cf217908e3af67b19205a41f8e7b29ae1f0f7a45347221249710de70fe']
#    for trx in test_trx:
#        explore_transaction(trx)
#        time.sleep(10)

    explore_address('bc1qgdjqv0av3q56jvd82tkdjpy7gdp9ut8tlqmgrpmv24sq90ecnvqqjwvw97')
    time.sleep(10)
    explore_block(828384)
    time.sleep(10)
    explore_transaction('edbf6be7177cd2db48aa0fc99840f53c757b8589099ea6c4361b1c6977db9a4b')