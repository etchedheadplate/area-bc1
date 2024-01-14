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
    'lightning_latest_raw_values': {
        'api': {
            'base': 'https://mempool.space/api/v1/',
            'endpoint': ('lightning/statistics/latest'),
            'params': False,
            'subdict': False
        },
        'file': {
            'path': 'db/lightning/',
            'name': 'lightning_latest_raw_values.json',
            'columns': False
        },
        'update': {
            'time': '00:05',
            'interval': 24
        }
    },
    'lightning_history_chart': {
        'api': {
            'base': 'https://mempool.space/api/v1/',
            'endpoint': ('lightning/statistics/1y'),
            'params': False,
            'subdict': False
        },
        'file': {
            'path': f'db/lightning/',
            'name': 'lightning_history_chart.csv',
            'columns': {
                'added': 'Date',
                'channel_count': 'Channel Count',
                'total_capacity': 'Total Capacity',
                'tor_nodes': 'Nodes Tor',
                'clearnet_nodes': 'Nodes Clearnet',
                'unannounced_nodes': 'Nodes Unannounced',
                'clearnet_tor_nodes': 'Nodes Clearnet Tor'
            }
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
    },
    'network_latest_raw_values': {
        'api': {
            'base': 'https://api.blockchain.info/',
            'endpoint': ('stats'),
            'params': {
                ''
                },
            'subdict': ''
        },
        'file': {
            'path': 'db/network/',
            'name': 'network_latest_raw_values.json',
            'columns': False
        },
        'update': {
            'time': '00:00',
            'interval': 0.25
        }
    },
    'network_history_chart': {
        'api': {
            'base': 'https://api.blockchain.info/',
            'endpoint': ('charts/market-price', 'charts/hash-rate', 'charts/n-transactions-per-block', 'charts/cost-per-transaction'),
            'params': {
                    'timespan': '1years',
                    'rollingAverage': '7days',
                    'start': '',
                    'format': 'json',
                    'sampled': 'true'
                },
            'subdict': 'values'
        },
        'file': {
            'path': 'db/network/',
            'name': 'network_history_chart.csv',
            'columns': ('Price', 'Hashrate', 'TRX Per Block', 'TRX Cost')
        },
        'update': {
            'time': '00:05',
            'interval': 1
        }
    }
}


# Market plot related variables
plot = {
    'lightning': {
        'path': 'db/lightning/',
        'font': 'src/font/font.ttf',
        'colors': {
            'date': '#F9F9F9',
            'channel_count': '#B93554',
            'total_capacity': '#F7931A',
            'nodes_clearnet': '#6a6866',
            'nodes_clearnet_tor': '#4e4e4c',
            'nodes_tor': '#343331',
            'nodes_unannounced': '#191716',
            'frame': '#191716',
            'frame_nodes': '#FFFFFF',
            'total_capacity_down': '#CB2B1B',
            'total_capacity_up': '#2BD713',
        },
        'backgrounds': {
            'total_capacity_down': {
                    'path': 'src/image/plot/backgrounds/lightning_total_capacity_down.png',
                    'range': (-float('inf'), 0),
                    'coordinates': (795, 5)
            },
            'total_capacity_up': {
                    'path': 'src/image/plot/backgrounds/lightning_total_capacity_up.png',
                    'range': (0, float('inf')),
                    'coordinates': (795, 5)
            }
        }
    },
    'market': {
        'path': f'db/market/{currency_pair}/',
        'font': 'src/font/font.ttf',
        'colors': {
            'date': '#F9F9F9',
            'price': '#F7931A',
            'total_volume': '#17E2E8',
            'frame': '#191716',
            'price_down': '#CB2B1B',
            'price_up': '#2BD713'
        },
        'backgrounds': {
            'price_down': {
                    'path': 'src/image/plot/backgrounds/market_price_down.png',
                    'range': (-float('inf'), 0),
                    'coordinates': (25, 5)
            },
            'price_up': {
                    'path': 'src/image/plot/backgrounds/market_price_up.png',
                    'range': (0, float('inf')),
                    'coordinates': (25, 5)
            }
        }
    },
    'network': {
        'path': 'db/network/',
        'font': 'src/font/font.ttf',
        'colors': {
            'date': '#F9F9F9',
            'price': '#F7931A',
            'hashrate': '#26A530',
            'trx_per_block': '#F9F9F9',
            'frame': '#191716'
        },
        'background': {
            'path': 'src/image/plot/backgrounds/network.png',
            'range': (-float('inf'), float('inf')),
            'coordinates': (25, 5)
        }
    }
}
