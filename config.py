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
    'charts' :{
        'lightning': {
        'api': {
            'base': 'https://mempool.space/api/v1/',
            'endpoints': ['lightning/statistics/1m'],
            'params': False,
            'subdict': False,
            'response_type': dict
        },
        'file': {
            'path': f'db/lightning/',
            'name': 'lightning.csv',
            'columns': {
                'lightning/statistics/1m': {
                    'added': 'date',
                    'channel_count': 'channels',
                    'total_capacity': 'capacity',
                    'tor_nodes': 'nodes_darknet',
                    'clearnet_nodes': 'nodes_clearnet',
                    'unannounced_nodes': 'nodes_unknown',
                    'clearnet_tor_nodes': 'nodes_greynet'
                }
            }
        },
        'update': {
            'interval': 1,
            'seconds': ':00'
        }
    },
        'market': {
            'api': {
                'base': 'https://api.coingecko.com/api/v3/',
                'endpoints': [f'coins/{currency_crypto}/market_chart'],
                'params': {
                        'vs_currency': f'{currency_vs}',
                        'days': '1',
                        'interval': '',
                        'precision': '2'
                    },
                'subdict': False,
                'response_type': list
            },
            'file': {
                'path': f'db/market/{currency_pair}/',
                'name': 'market.csv',
                'columns': {
                    f'coins/{currency_crypto}/market_chart': {
                        'prices': 'price',
                        'market_caps': 'market_cap',
                        'total_volumes': 'total_volume'
                    }
                }
            },
            'update': {
                'interval': 1,
                'seconds': ':00'
            }
        },
        'market_days_90': {
            'api': {
                'base': 'https://api.coingecko.com/api/v3/',
                'endpoints': [f'coins/{currency_crypto}/market_chart'],
                'params': {
                        'vs_currency': f'{currency_vs}',
                        'days': '90',
                        'interval': '',
                        'precision': '2'
                    },
                'subdict': False,
                'response_type': list
            },
            'file': {
                'path': f'db/market/{currency_pair}/',
                'name': 'market_days_90.csv',
                'columns': {
                    f'coins/{currency_crypto}/market_chart': {
                        'prices': 'price',
                        'market_caps': 'market_cap',
                        'total_volumes': 'total_volume'
                    }
                }
            },
            'update': {
                'interval': 1,
                'seconds': ':30'
            }
        },
        'market_days_max': {
            'api': {
                'base': 'https://api.coingecko.com/api/v3/',
                'endpoints': [f'coins/{currency_crypto}/market_chart'],
                'params': {
                        'vs_currency': f'{currency_vs}',
                        'days': 'max',
                        'interval': '',
                        'precision': '2'
                    },
                'subdict': False,
                'response_type': list
            },
            'file': {
                'path': f'db/market/{currency_pair}/',
                'name': 'market_days_max.csv',
                'columns': {
                    f'coins/{currency_crypto}/market_chart': {
                        'prices': 'price',
                        'market_caps': 'market_cap',
                        'total_volumes': 'total_volume'
                    }
                }
            },
            'update': {
                'interval': 1,
                'seconds': ':45'
            }
        },
        'network': {
            'api': {
                'base': 'https://api.blockchain.info/',
                'endpoints': [
                    'charts/market-price',
                    'charts/hash-rate',
                    'charts/n-transactions-per-block',
                    'charts/cost-per-transaction'
                    ],
                'params': {
                    'timespan': '1months',
                    'rollingAverage': '2days',
                    'start': '',
                    'format': 'json',
                    'sampled': 'true'
                    },
                'subdict': 'values',
                'response_type': dict
            },
            'file': {
                'path': 'db/network/',
                'name': 'network.csv',
                'columns': {
                    'charts/market-price': {
                        'x': 'date',
                        'y': 'price'
                    },
                        'charts/hash-rate': {
                        'x': 'date',
                        'y': 'hashrate'
                    },
                        'charts/n-transactions-per-block': {
                        'x': 'date',
                        'y': 'trx_per_block'
                    },
                        'charts/cost-per-transaction': {
                        'x': 'date',
                        'y': 'trx_cost'
                    }
                }
            },
            'update': {
                'interval': 1,
                'seconds': ':00'
            }
        }
    },
    'snapshots': {
        'fees': {
            'api': {
                'base': 'https://mempool.space/api/v1/',
                'endpoints': ('fees/recommended'),
                'params': False,
                'subdict': False
            },
            'file': {
                'path': 'db/fees/',
                'name': 'fees.json',
            },
            'update': {
                'interval': 1,
                'seconds': ':30'
            }
        },
        'lightning': {
            'api': {
                'base': 'https://mempool.space/api/v1/',
                'endpoints': ('lightning/statistics/latest'),
                'params': False,
                'subdict': False
            },
            'file': {
                'path': 'db/lightning/',
                'name': 'lightning.json',
            },
            'update': {
                'interval': 1,
                'seconds': ':15'
            }
        },
        'market': {
            'api': {
                'base': 'https://api.coingecko.com/api/v3/',
                'endpoints': (f'coins/{currency_crypto}'),
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
                'path': f'db/market/{currency_pair}/',
                'name': 'market.json',
            },
            'update': {
                'interval': 1,
                'seconds': ':15'
            }
        },
        'network': {
            'api': {
                'base': 'https://api.blockchain.info/',
                'endpoints': ('stats'),
                'params': False,
                'subdict': ''
            },
            'file': {
                'path': 'db/network/',
                'name': 'network.json',
            },
            'update': {
                'interval': 1,
                'seconds': ':15'
            }
        }
    }
}


# Market plot related variables
images = {
    'fees': {
        'path': 'db/fees/',
        'font': 'src/font/font.ttf',
        'colors': {
            'date': '#F9F9F9',
            'text': '#F9F9F9',
            'subtext': '#191716',
            'fees_satvb_fastest': '#B93554',
            'fees_satvb_half_hour': '#F7931A',
            'fees_satvb_hour': '#6A6866',
            'fees_satvb_economy': '#4E4E4C',
            'fees_satvb_minimum': '#343331'
        },
        'background': 'src/image/backgrounds/fees.png',
        'coordinates': (795, 5)
    },
    'lightning': {
        'path': 'db/lightning/',
        'font': 'src/font/font.ttf',
        'colors': {
            'date': '#F9F9F9',
            'channels': '#B93554',
            'capacity': '#F7931A',
            'nodes_clearnet': '#6A6866',
            'nodes_greynet': '#4E4E4C',
            'nodes_darknet': '#343331',
            'nodes_unknown': '#191716',
            'frame': '#191716',
            'frame_nodes': '#FFFFFF',
            'capacity_down': '#CB2B1B',
            'capacity_up': '#2BD713',
        },
        'backgrounds': {
            'capacity_down': {
                    'path': 'src/image/backgrounds/lightning_capacity_down.png',
                    'range': (-float('inf'), 0),
                    'coordinates': (795, 5)
            },
            'capacity_up': {
                    'path': 'src/image/backgrounds/lightning_capacity_up.png',
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
                    'path': 'src/image/backgrounds/market_price_down.png',
                    'range': (-float('inf'), 0),
                    'coordinates': (25, 5)
            },
            'price_up': {
                    'path': 'src/image/backgrounds/market_price_up.png',
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
            'hashrate': '#CACACA',
            'trx_per_block': '#717171',
            'frame': '#191716',
            'hashrate_down': '#CB2B1B',
            'hashrate_up': '#2BD713'
        },
        'backgrounds': {
            'hashrate_down': {
                    'path': 'src/image/backgrounds/network_hashrate_down.png',
                    'range': (-float('inf'), 0),
                    'coordinates': (795, 5)
            },
            'hashrate_up': {
                    'path': 'src/image/backgrounds/network_hashrate_up.png',
                    'range': (0, float('inf')),
                    'coordinates': (795, 5)
            }
        }
    }
}
