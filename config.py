'''
Variables used for API calls and data display. Can be adjusted manually
within this module or/and via user interface in bot. All paths are relative.
'''


# Currency related variables
currency_crypto = 'bitcoin'
currency_vs = 'usd'
currency_crypto_ticker = 'BTC'
currency_vs_ticker = currency_vs.upper()
currency_pair = currency_crypto_ticker + currency_vs_ticker



# Database related variables
databases = {
    'blockchain_latest_raw_values': {
        'api': {
            'base': 'https://api.blockchain.info/',
            'endpoint': ('stats'),
            'params': {
                ''
                },
            'subdict': ''
        },
        'file': {
            'path': 'db/blockchain/',
            'name': 'latest_raw_values.json',
            'columns': False
        },
        'update': {
            'time': '00:00',
            'interval': 0.25
        }
    },
    'blockchain_history_chart': {
        'api': {
            'base': 'https://api.blockchain.info/',
            'endpoint': ('charts/market-price', 'charts/hash-rate', 'charts/cost-per-transaction', 'charts/transaction-fees-usd'),
            'params': {
                    'timespan': '1months',
                    'start': '',
                    'format': 'json',
                    'sampled': 'true'
                },
            'subdict': 'values'
        },
        'file': {
            'path': 'db/blockchain/',
            'name': 'history_chart.csv',
            'columns': ('Price', 'Hashrate', 'TRX Cost', 'Total Transaction Fees')
        },
        'update': {
            'time': '00:05',
            'interval': 1
        }
    },
    'market_latest_raw_values': {
        'api': {
            'base': 'https://api.coingecko.com/api/v3/',
            'endpoint': (f'coins/{currency_crypto}'),
            'params': {
                    'localization': 'false',
                    'tickers': 'false',
                    'market_data': 'true',
                    'community_data': 'false',
                    'developer_data': 'false'
                },
            'subdict': 'market_data'
        },
        'file': {
            'path': f'db/market/{currency_pair}/latest/',
            'name': 'latest_raw_values.json',
            'columns': False
        },
        'update': {
            'time': '00:30',
            'interval': 0.25
        }
    },
    'market_latest_chart': {
        'api': {
            'base': 'https://api.coingecko.com/api/v3/',
            'endpoint': (f'coins/{currency_crypto}/market_chart'),
            'params': {
                    'vs_currency': f'{currency_vs}',
                    'days': '1',
                    'interval': '',
                    'precision': '2'
                },
            'subdict': False
        },
        'file': {
            'path': f'db/market/{currency_pair}/latest/',
            'name': 'market_latest_chart.csv',
            'columns': {
                'Price': 'prices',
                'Market Cap': 'market_caps',
                'Total Volume': 'total_volumes'
            }
        },
        'update': {
            'time': '50:30',
            'interval': 0.25
        }
    },
    'market_history_chart_days_90': {
        'api': {
            'base': 'https://api.coingecko.com/api/v3/',
            'endpoint': (f'coins/{currency_crypto}/market_chart'),
            'params': {
                    'vs_currency': f'{currency_vs}',
                    'days': '90',
                    'interval': '',
                    'precision': '2'
                },
            'subdict': False
        },
        'file': {
            'path': f'db/market/{currency_pair}/history/',
            'name': 'market_history_chart_days_90.csv',
            'columns': {
                'Price': 'prices',
                'Market Cap': 'market_caps',
                'Total Volume': 'total_volumes'
            }
        },
        'update': {
            'time': '10:30',
            'interval': 1
        }
    },
    'market_history_chart_days_max': {
        'api': {
            'base': 'https://api.coingecko.com/api/v3/',
            'endpoint': (f'coins/{currency_crypto}/market_chart'),
            'params': {
                    'vs_currency': f'{currency_vs}',
                    'days': 'max',
                    'interval': '',
                    'precision': '2'
                },
            'subdict': False
        },
        'file': {
            'path': f'db/market/{currency_pair}/history/',
            'name': 'market_history_chart_days_max.csv',
            'columns': {
                'Price': 'prices',
                'Market Cap': 'market_caps',
                'Total Volume': 'total_volumes'
            }
        },
        'update': {
            'time': '00:55:30',
            'interval': 24
        }
    }
}


# Market plot related variables
plot = {
    'blockchain': {
        'path': 'db/blockchain/',
        'font': 'src/font/font.ttf',
        'colors': {
            'date': '#B9B9B9',
            'price': '#F7931A',
            'hashrate': '#686868',
            'trx_cost': '#F9F9F9',
            'frame': 'black',
            'trx_cost_down': '#2BD713',
            'trx_cost_up': '#CB2B1B',
        },
        'backgrounds': {
            'trx_cost_down': {
                    'path': 'src/image/plot/backgrounds/trx_cost_down.png',
                    'range': (-float('inf'), 0),
                    'coordinates': (795, 5)
            },
            'trx_cost_up': {
                    'path': 'src/image/plot/backgrounds/trx_cost_up.png',
                    'range': (0, float('inf')),
                    'coordinates': (795, 5)
            }
        }
    },
    'market': {
        'path': f'db/market/{currency_pair}/',
        'font': 'src/font/font.ttf',
        'colors': {
            'date': '#B9B9B9',
            'price': '#F7931A',
            'total_volume': '#17E2E8',
            'frame': 'black',
            'price_down': '#CB2B1B',
            'price_up': '#2BD713'
        },
        'backgrounds': {
            'price_down': {
                    'path': 'src/image/plot/backgrounds/price_down.png',
                    'range': (-float('inf'), 0),
                    'coordinates': (25, 5)
            },
            'price_up': {
                    'path': 'src/image/plot/backgrounds/price_up.png',
                    'range': (0, float('inf')),
                    'coordinates': (25, 5)
            }
        }
    }
}
