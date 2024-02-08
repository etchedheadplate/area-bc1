import os

import config
from tools import get_api_data, format_quantity, convert_timestamp_to_utc, format_currency


def write_address(address):
    
    base = 'https://blockchain.info/'
    endpoint = f'rawaddr/{address}'
    response = get_api_data(base, endpoint)
    path = 'db/blockchain/addresses/'
    file = path + f'{address}.md'
    
    if not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)
    
    with open (file, 'w') as markdown:

        UTXO = response['n_unredeemed']
        RECIEVED = format_currency(response['total_received'] / 100_000_000, config.currency_crypto_ticker, decimal=8)
        SENT = format_currency(response['total_sent'] / 100_000_000, config.currency_crypto_ticker, decimal=8)
        BALANCE = format_currency(response['final_balance'] / 100_000_000, config.currency_crypto_ticker, decimal=8)

        transactions_list = []
        for transaction in response['txs']:
            HASH = transaction['hash']
            DATE = convert_timestamp_to_utc(transaction['time'])
            result = transaction['result']
            if result < 0:
                AMOUNT = f'- {format_currency(abs(result) / 100_000_000, config.currency_crypto_ticker, decimal=8)}'
            else:
                AMOUNT = f'+ {format_currency(abs(result) / 100_000_000, config.currency_crypto_ticker, decimal=8)}'
            transactions_list.append([HASH, DATE, AMOUNT])

        transactions_limit = 5
        TRANSACTIONS_COUNT = len(transactions_list) if len(transactions_list) < 100 else '99+'
        TRANSACTIONS_MORE = len(transactions_list) - transactions_limit if len(transactions_list) - transactions_limit < 95 else '95+'

        info_address = f'[Address]\n' \
            f'Balance: {BALANCE}\n' \
            f'Recieved: {RECIEVED}\n' \
            f'Sent: {SENT}\n' \
            f'UTXO: {UTXO}\n'
        
        info_transactions = f'[{TRANSACTIONS_COUNT} Transactions]\n'
        for HASH, DATE, AMOUNT in transactions_list[:5]:
            info_transactions += f'UTC {DATE} --> {AMOUNT}\n'
            info_transactions += f'{HASH}\n'
        if len(transactions_list) > transactions_limit:
            info_transactions += f'...and {TRANSACTIONS_MORE} more transactions\n'

        info_explorers = f'[blockstream.info](https://blockstream.info/address/{address})\n' \
            f'[blockchain.com](https://www.blockchain.com/explorer/addresses/btc/{address})\n' \
            f'[mempool.space](https://mempool.space/address/{address})\n'
        
        markdown.write(f'```\n{info_address}\n{info_transactions}\n```\n{info_explorers}')


def write_block(block):
    
    base = 'https://blockchain.info/'
    endpoint = f'block-height/{block}'
    response = get_api_data(base, endpoint)
    path = 'db/blockchain/blocks/'
    file = path + f'{block}.md'
    
    if not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)
    
    with open (file, 'w') as markdown:

        response = response['blocks'][0]
        
        HASH = response['hash']
        MERKLE = response['mrkl_root']
        DATE = convert_timestamp_to_utc(response['time'])
        BITS = response['bits']
        FEE = format_currency(response['fee'] / 100_000_000, config.currency_crypto_ticker, decimal=8)
        NOUNCE = response['nonce']
        TRANSACTIONS = format_quantity(response['n_tx'])
        SIZE = format_quantity(response['size'])
        WIEGHT_WU = format_quantity(response['weight'])
        WEIGHT_VB = format_quantity(round(response['weight'] / 4))

        info_block = f'[Block {block}]\n' \
            f'Bits: {BITS}\n' \
            f'Nounce: {NOUNCE}\n' \
            f'Transactions: {TRANSACTIONS}\n' \
            f'Weight, WU: {WIEGHT_WU}\n' \
            f'Weight, vB: {WEIGHT_VB}\n' \
            f'Size: {SIZE} bytes\n' \
            f'Fee: {FEE}\n' \
            f'UTC: {DATE}\n' \
            f'Hash: {HASH}\n' \
            f'Merkle: {MERKLE}\n'
        
        info_explorers = f'[blockstream.info](https://blockstream.info/block/{HASH})\n' \
            f'[blockchain.com](https://www.blockchain.com/explorer/blocks/btc/{block})\n' \
            f'[mempool.space](https://mempool.space/block/{HASH})\n'
        
        markdown.write(f'```\n{info_block}```\n{info_explorers}')

    
def write_transaction(transaction_hash):
    
    base = 'https://blockchain.info/'
    endpoint = f'rawtx/{transaction_hash}'
    response = get_api_data(base, endpoint)
    path = 'db/blockchain/transactions/'
    file = path + f'{transaction_hash}.md'
    
    if not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)
    
    with open (file, 'w') as markdown:

        VERSION = '1 (Legacy)' if response['ver'] == 1 else '2 (SegWit)'
        SIZE = format_quantity(response['size'])
        WIEGHT_WU = format_quantity(response['weight'])
        WEIGHT_VB = format_quantity(round(response['weight'] / 4))
        FEE = format_currency(response['fee'] / 100_000_000, config.currency_crypto_ticker, decimal=8)
        IP = response['relayed_by']
        RELAY = 'Unknown' if IP == '0.0.0.0' else IP
        INDEX = response['tx_index']
        DOUBLE_SPEND = response['double_spend']
        DATE = convert_timestamp_to_utc(response['time'])
        HEIGHT = 'Unconfirmed' if response['block_height'] == None else response['block_height']
        AMOUNT = 0

        inputs_list = []
        for input in response['inputs']:
            INPUT_ADDRESS = input['prev_out']['addr']
            INPUT_AMOUNT = format_currency(input['prev_out']['value'] / 100_000_000, config.currency_crypto_ticker, decimal=8)
            inputs_list.append([INPUT_ADDRESS, INPUT_AMOUNT])

        outputs_list = []
        for output in response['out']:
            OUTPUT_ADDRESS = output['addr']
            OUTPUT_AMOUNT = format_currency(output['value'] / 100_000_000, config.currency_crypto_ticker, decimal=8)
            AMOUNT = AMOUNT + output['value']
            outputs_list.append([OUTPUT_ADDRESS, OUTPUT_AMOUNT])
        
        AMOUNT = format_currency(AMOUNT / 100_000_000, config.currency_crypto_ticker, decimal=8)
        
        inputs_limit = 5
        INPUTS_COUNT = len(inputs_list) if len(inputs_list) < 100 else '99+'
        INPUTS_MORE = len(inputs_list) - inputs_limit if len(inputs_list) - inputs_limit < 95 else '95+'
        outputs_limit = 5
        OUTPUTS_COUNT = len(outputs_list) if len(outputs_list) < 100 else '99+'
        OUTPUTS_MORE = len(outputs_list) - outputs_limit if len(outputs_list) - outputs_limit < 95 else '95+'

        info_transaction = f'[Transaction]\n' \
            f'Height: {HEIGHT}\n' \
            f'Amount: {AMOUNT}\n' \
            f'Weight: {WIEGHT_WU}WU / {WEIGHT_VB}vB\n' \
            f'Size: {SIZE} bytes\n' \
            f'Fee: {FEE}\n' \
            f'Relay: {RELAY}\n' \
            f'Version: {VERSION}\n' \
            f'Double Spend: {DOUBLE_SPEND}\n' \
            f'Index: {INDEX}\n' \
            f'UTC: {DATE}\n'
        
        info_inputs = f'[{INPUTS_COUNT} Inputs]\n'
        for INPUT_ADDRESS, INPUT_AMOUNT in inputs_list[:5]:
            info_inputs += f'{INPUT_ADDRESS} --> {INPUT_AMOUNT}\n'
        if len(inputs_list) > 5:
            info_inputs += f'...and {INPUTS_MORE} more inputs\n'

        info_outputs = f'[{OUTPUTS_COUNT} Outputs]\n'
        for OUTPUT_ADDRESS, OUTPUT_AMOUNT in outputs_list[:5]:
            info_outputs += f'{OUTPUT_AMOUNT} --> {OUTPUT_ADDRESS}\n'
        if len(outputs_list) > 5:
            info_outputs += f'...and {OUTPUTS_MORE} more inputs\n'

        info_explorers = f'[blockstream.info](https://blockstream.info/tx/{transaction_hash})\n' \
            f'[blockchain.com](https://www.blockchain.com/explorer/transactions/btc/{transaction_hash})\n' \
            f'[mempool.space](https://mempool.space/tx/{transaction_hash})\n'
        
        markdown.write(f'```\n{info_transaction}\n{info_inputs}\n{info_outputs}\n```\n{info_explorers}')




if __name__ == '__main__':

    test_trx = ['a8f082969ba092ce7cc5887186f7878e4f9637fb1efddf07c89d83c077215475',
                '9b3bc730036b996c6b51ef0e2924f55e7c236fad33fed487362ade2c1a57a18e',
                'd7e7af6a06c16ab16653879ba5a299dae8fa4e95e91fcb0bf94f03e1b3b64149',
                'eb08b6cf217908e3af67b19205a41f8e7b29ae1f0f7a45347221249710de70fe']
    for trx in test_trx:
        write_transaction(trx)

    test_add = ['bc1qxm4akgtq3laygjljn9nj0xelx86tr808yqtj5y',
                 'bc1qm34lsc65zpw79lxes69zkqmk6ee3ewf0j77s3h']
    for add in test_add:
        write_address(add)

    test_blk = ['828282',
                '113355',
                '265']
    for blk in test_blk:
        write_block(blk)