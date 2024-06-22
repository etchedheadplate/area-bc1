from api.dune import TOKEN as dune_api_token


# Main bot settings:
bot_name = '@area_bc1_bot'
bot_log_file = f'log/{bot_name[1:]}.log'
bot_log_age = 30


# Currency related variables:
currency_crypto = 'bitcoin'
currency_vs = 'usd'
currency_crypto_ticker = 'BTC'
currency_vs_ticker = currency_vs.upper()
currency_pair = currency_crypto_ticker + currency_vs_ticker


# Dictionaries for managing databases:
charts = {
    'etfs': {
        'api': {
            'base': 'https://api.dune.com/api/v1/',
            'endpoints': ['query/3400598/results/csv'],
            'extention': 'csv',
            'params': {
                'api_key': f'{dune_api_token}'
                },
           'parsed': False,
            'subdict': False
        },
        'file': {
            'path': 'db/etfs/',
            'name': 'etfs.csv',
            'columns': False
        }
    },
    'lightning': {
        'api': {
            'base': 'https://mempool.space/api/v1/',
            'endpoints': ['lightning/statistics/6y'],
            'extention': 'json',
            'params': False,
            'parsed': 'dict',
            'subdict': False
        },
        'file': {
            'path': f'db/lightning/',
            'name': 'lightning.csv',
            'columns': {
                'lightning/statistics/6y': {
                    'added': 'date',
                    'channel_count': 'channels',
                    'total_capacity': 'capacity',
                    'tor_nodes': 'nodes_darknet',
                    'clearnet_nodes': 'nodes_clearnet',
                    'unannounced_nodes': 'nodes_unknown',
                    'clearnet_tor_nodes': 'nodes_greynet'
                }
            }
        }
    },
    'market': {
        'api': {
            'base': 'https://api.coingecko.com/api/v3/',
            'endpoints': [f'coins/{currency_crypto}/market_chart'],
            'extention': 'json',
            'params': {
                    'vs_currency': f'{currency_vs}',
                    'days': '1',
                    'interval': '',
                    'precision': '2'
                },
            'parsed': 'list',
            'subdict': False
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
        }
    },
    'market_days_90': {
        'api': {
            'base': 'https://api.coingecko.com/api/v3/',
            'endpoints': [f'coins/{currency_crypto}/market_chart'],
            'extention': 'json',
            'params': {
                    'vs_currency': f'{currency_vs}',
                    'days': '90',
                    'interval': '',
                    'precision': '2'
                },
            'parsed': 'list',
            'subdict': False
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
        }
    },
    'market_days_max': {
        'api': {
            'base': 'https://api.blockchain.info/',
            'endpoints': [
                'charts/market-price',
                'charts/trade-volume',
#                'charts/market-cap'
                ],
            'extention': 'json',
            'params': {
                'timespan': '6years',
                'rollingAverage': '1days',
                'start': '',
                'format': 'json'
                },
            'parsed': 'dict',
            'subdict': 'values'
        },
        'file': {
            'path': f'db/market/{currency_pair}/',
            'name': 'market_days_max.csv',
            'columns': {
                'charts/market-price': {
                    'x': 'date',
                    'y': 'price'
                },
                'charts/trade-volume': {
                    'x': 'date',
                    'y': 'total_volume'
                },
#                'charts/market-cap': {
#                    'x': 'date',
#                    'y': 'market_cap'
#                }
            }
        }
    },
    'network': {
        'api': {
            'base': 'https://api.blockchain.info/',
            'endpoints': [
                'charts/market-price',
                'charts/hash-rate',
                'charts/n-transactions-per-block',
                'charts/blocks-size'
                ],
            'extention': 'json',
            'params': {
                'timespan': '6years',
                'rollingAverage': '1days',
                'start': '',
                'format': 'json',
                'sampled': 'true'
                },
            'parsed': 'dict',
            'subdict': 'values'
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
                    'charts/blocks-size': {
                    'x': 'date',
                    'y': 'blocks-size'
                }
            }
        }
    },
    'pools': {
        'api': {
            'base': 'https://api.blockchain.info/',
            'endpoints': ['pools'],
            'extention': 'json',
            'params': {
                'timespan': '7days'
                },
            'parsed': 'dict',
            'subdict': False
        },
        'file': {
            'path': 'db/pools/',
            'name': 'pools.csv',
            'columns': ['pool', 'mined']
        }
    },
    'seized': {
        'api': {
            'base': 'https://api.dune.com/api/v1/',
            'endpoints': ['query/2220209/results/csv'],
            'extention': 'csv',
            'params': {
                'api_key': f'{dune_api_token}'
                },
            'parsed': False,
            'subdict': False
        },
        'file': {
            'path': 'db/seized/',
            'name': 'seized.csv',
            'columns': False
        }
    }
}

snapshots = {
    'exchanges': {
        'api': {
            'base': 'https://api.coingecko.com/api/v3/',
            'endpoints': ('exchanges'),
            'extention': 'json',
            'params': False,
            'subdict': False
        },
        'file': {
            'path': f'db/exchanges/',
            'name': 'exchanges.json',
        }
    },
    'fees': {
        'api': {
            'base': 'https://mempool.space/api/v1/',
            'endpoints': ('fees/recommended'),
            'extention': 'json',
            'params': False,
            'subdict': False
        },
        'file': {
            'path': 'db/fees/',
            'name': 'fees.json',
        }
    },
    'lightning': {
        'api': {
            'base': 'https://mempool.space/api/v1/',
            'endpoints': ('lightning/statistics/latest'),
            'extention': 'json',
            'params': False,
            'subdict': False
        },
        'file': {
            'path': 'db/lightning/',
            'name': 'lightning.json',
        }
    },
    'market': {
        'api': {
            'base': 'https://api.coingecko.com/api/v3/',
            'endpoints': (f'coins/{currency_crypto}'),
            'extention': 'json',
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
        }
    },
    'network': {
        'api': {
            'base': 'https://api.blockchain.info/',
            'extention': 'json',
            'endpoints': ('stats'),
            'params': False,
            'subdict': ''
        },
        'file': {
            'path': 'db/network/',
            'name': 'network.json',
        }
    }
}

delay = 15

updates = {
    # Most of the numbers are primes to minimize chance of rate limit risk between diffirent databases with
    # same API. Charts and snapshots within same database updated with {delay} for the this reason also.

    # Databases are updated every {minutes} at :{seconds}, if current time is 13:12:00, {minutes} = 179 and
    # {seconds} = 11, then update will be at 16:11:11, 19:10:11, 22:09:11, 01:08:11, etc.

    # {seconds} -> chart -> + {delay} seconds -> snapshot -> + {delay} seconds -> image -> markdown.
    # Overal scheme should not exceed 59 seconds, {seconds} should be set accordingly.

    # API mempool.space:
    'fees': { # snapshot + image
        'minutes': 7,
        'seconds': 31
    },
    'lightning': { # chart + snapshot + image + markdown
        'minutes': 113,
        'seconds': 5
    },
    # API CoinGecko:
    'exchanges': { # snapshot + image
        'minutes': 11,
        'seconds': 13
    },
    'market': { # chart + snapshot + image + markdown
        'minutes': 7,
        'seconds': 2
    },
    'market_days_90': { # chart
        'minutes': 13,
        'seconds': 29
    },
    'market_days_max': { # chart
        'minutes': 599,
        'seconds': 43
    },
    # API Blockchain.com:
    'network': { # chart + snapshot + image + markdown
        'minutes': 113,
        'seconds': 11
    },
    'pools': { # chart + image 
        'minutes': 179,
        'seconds': 37
    },
    # API Dune.com:
    'etfs': { # chart + image + markdown
        'minutes': 1439,
        'seconds': 29
    },
    'seized': { # chart + image + markdown
        'minutes': 4297,
        'seconds': 3
    }
}


# Dictionary for creation of images:
images = {
    'address': {
        'path': 'db/blockchain/address/',
        'font': 'src/font/font.ttf',
        'colors': {
            'titles': '#c1c0c0',
            'titles_fiat': '#2b9348',
            'titles_crypto': '#F7931A',
            'titles_other': '#F9F9F9'
        },
        'backgrounds': {
            'path': 'src/image/backgrounds/address.png',
            'colors': {
                'api': ('#F9F9F9', (950, 65), (950, 106)),
                'metric': ('#CACACA', (1315, 65), (1315, 103))
            }
        }
    },
    'block': {
        'path': 'db/blockchain/block/',
        'font': 'src/font/font.ttf',
        'colors': {
            'titles': '#c1c0c0',
            'titles_crypto': '#F7931A',
            'titles_other': '#F9F9F9'
        },
        'backgrounds': {
            'path': 'src/image/backgrounds/block.png',
            'colors': {
                'api': ('#F9F9F9', (950, 65), (950, 106)),
                'metric': ('#CACACA', (1315, 65), (1315, 103))
            }
        }
    },
    'etfs': {
        'path': 'db/etfs/',
        'font': 'src/font/font.ttf',
        'colors': {
            'date': '#CACACA',
            'frame': '#191716',
            'usd': '#2b9348',
            'btc': '#F7931A',
            'percentage': '#c1c0c0',
            'bitcoin': '#F7931A',
            'areas': ['#22577A', '#2D7D90', '#38A3A5', '#57CC99', '#80ED99', '#C7F9CC']
        },
        'backgrounds': {
            'key_metric_down': {
                'path': 'src/image/backgrounds/etfs_down.png',
                'range': (-float('inf'), 0),
                'coordinates': (750, 5),
                'colors': {
                    'api': ('#F1603F', (200, 65), (200, 105)),
                    'metric': ('#e5383b', (240, 165), (240, 205))
                }
            },
            'key_metric_up': {
                'path': 'src/image/backgrounds/etfs_up.png',
                'range': (0, float('inf')),
                'coordinates': (750, 5),
                'colors': {
                    'api': ('#F1603F', (200, 65), (200, 105)),
                    'metric': ('#2BD713', (240, 165), (240, 205))
                }
            }
        }
    },
    'exchanges': {
        'path': 'db/exchanges/',
        'font': 'src/font/font.ttf',
        'colors': {
            'percentage': '#fdfffc',
            'bitcoin': '#F7931A',
            'slices': ['#6a4c93', '#1982c4', '#2ec4b6', '#8ac926', '#fdc500', '#ff595e']
        },
        'backgrounds': {
            'path': 'src/image/backgrounds/exchanges.png',
            'coordinates': (680, -15),
            'colors': {
                'api': ('#ffd60a', (100, 65), (100, 105)),
                'period': ('#2ec4b6', (455, 65), (455, 100))
            }
        }
    },
    'fees': {
        'path': 'db/fees/',
        'font': 'src/font/font.ttf',
        'colors': {
            'blocks': '#F9F9F9',
            'subblocks': '#c1c0c0',
            'fees_satvb_fastest': '#f48e1d',
            'fees_satvb_half_hour': '#e87c28',
            'fees_satvb_hour': '#db6934',
            'fees_satvb_economy': '#cf5640',
            'fees_satvb_minimum': '#c2434b',
            'fees_currency_fastest': '#ee8523',
            'fees_currency_half_hour': '#e1722e',
            'fees_currency_hour': '#d55f3a',
            'fees_currency_economy': '#c84c46',
            'fees_currency_minimum': '#bc3a51'
        },
        'backgrounds': {
            'path': 'src/image/backgrounds/fees.png',
            'colors': {
                'api': ('#bc3a51', (100, 65), (100, 105)),
                'metric': ('#F7931A', (455, 65), (455, 100))
            }
        }
    },
    'lightning': {
        'path': 'db/lightning/',
        'font': 'src/font/font.ttf',
        'colors': {
            'date': '#CACACA',
            'channels': '#00a5cf',
            'capacity': '#F7931A',
            'nodes_clearnet': '#FF00A1',
            'nodes_greynet': '#B40090',
            'nodes_darknet': '#790082',
            'nodes_unknown': '#5D009A',
            'frame': '#191716',
            'frame_nodes': '#FFFFFF',
            'outline': '#FFFFFF'
        },
        'backgrounds': {
            'key_metric_down': {
                'path': 'src/image/backgrounds/lightning_down.png',
                'range': (-float('inf'), 0),
                'coordinates': (795, 5),
                'colors': {
                    'api': ('#bc3a51', (240, 65), (240, 105)),
                    'metric': ('#e5383b', (240, 155), (240, 195))
                }
            },
            'key_metric_up': {
                'path': 'src/image/backgrounds/lightning_up.png',
                'range': (0, float('inf')),
                'coordinates': (795, 5),
                'colors': {
                    'api': ('#bc3a51', (240, 65), (240, 105)),
                    'metric': ('#2BD713', (240, 155), (240, 195))
                }
            }
        }
    },
    'market': {
        'path': f'db/market/{currency_pair}/',
        'font': 'src/font/font.ttf',
        'colors': {
            'date': '#CACACA',
            'price': '#F7931A',
            'total_volume': '#00a5cf',
            'frame': '#191716',
        },
        'backgrounds': {
            'key_metric_down': {
                'path': 'src/image/backgrounds/market_down.png',
                'range': (-float('inf'), 0),
                'coordinates': (25, 5),
                'colors': {
                    'api_day': ('#ffd60a', (1900, 65), (1900, 105)),
                    'api_history': ('#CACACA', (1900, 65), (1900, 105)),
                    'metric': ('#e5383b', (1900, 155), (1900, 195))
                }
            },
            'key_metric_up': {
                'path': 'src/image/backgrounds/market_up.png',
                'range': (0, float('inf')),
                'coordinates': (25, 5),
                'colors': {
                    'api_day': ('#ffd60a', (1900, 805), (1900, 845)),
                    'api_history': ('#CACACA', (1900, 805), (1900, 845)),
                    'metric': ('#2BD713', (1900, 895), (1900, 935))
                    
                }
            }
        }
    },
    'network': {
        'path': 'db/network/',
        'font': 'src/font/font.ttf',
        'colors': {
            'date': '#CACACA',
            'price': '#F7931A',
            'hashrate': '#2a9d8f',
            'trx_per_block': '#97DB4F',
            'frame': '#191716',
        },
        'backgrounds': {
            'key_metric_down': {
                'path': 'src/image/backgrounds/network_down.png',
                'range': (-float('inf'), 0),
                'coordinates': (795, 5),
                'colors': {
                    'api': ('#CACACA', (220, 805), (220, 845)),
                    'metric': ('#e5383b', (220, 895), (220, 935))
                }
            },
            'key_metric_up': {
                'path': 'src/image/backgrounds/network_up.png',
                'range': (0, float('inf')),
                'coordinates': (795, 5),
                'colors': {
                    'api': ('#CACACA', (220, 65), (220, 105)),
                    'metric': ('#2BD713', (220, 155), (220, 195))
                }
            }
        }
    },
    'pools': {
        'path': 'db/pools/',
        'font': 'src/font/font.ttf',
        'colors': {
            'percentage': '#c1c0c0',
            'bitcoin': '#F7931A',
            'slices': ['#E8086D', '#60079B', '#430EBE', '#183EE9', '#2385E7', '#00a5cf']
        },
        'backgrounds': {
            'path': 'src/image/backgrounds/pools.png',
            'coordinates': (680, -15),
            'colors': {
                'api': ('#CACACA', (100, 65), (100, 105)),
                'period': ('#00a5cf', (455, 65), (455, 100))
            }
        }
    },
    'seized': {
        'path': 'db/seized/',
        'font': 'src/font/font.ttf',
        'colors': {
            'date': '#CACACA',
            'usd': '#2b9348',
            'btc': '#0C67BB',
            'price': '#F7931A',
            'frame': '#191716'
        },
        'backgrounds': {
            'key_metric_down': {
                'path': 'src/image/backgrounds/seized_down.png',
                'range': (-float('inf'), 0),
                'coordinates': (785, 25),
                'colors': {
                    'api': ('#F1603F', (65, 65), (65, 105)),
                    'metric': ('#2BD713', (440, 65), (440, 105))
                }
            },
            'key_metric_up': {
                'path': 'src/image/backgrounds/seized_up.png',
                'range': (0, float('inf')),
                'coordinates': (785, 25),
                'colors': {
                    'api': ('#F1603F', (65, 65), (65, 105)),
                    'metric': ('#e5383b', (440, 65), (440, 105))
                }
            }
        }
    },
    'transaction': {
        'path': 'db/blockchain/transaction/',
        'font': 'src/font/font.ttf',
        'colors': {
            'titles': '#c1c0c0',
            'titles_fiat': '#2b9348',
            'titles_crypto': '#F7931A',
            'titles_other': '#F9F9F9'
        },
        'backgrounds': {
            'key_metric_down': {
                'path': 'src/image/backgrounds/transaction_down.png',
                'colors': {
                    'api': ('#F9F9F9', (100, 65), (100, 107)),
                    'metric': ('#e5383b', (465, 65), (465, 103))
                }
            },
            'key_metric_up': {
                'path': 'src/image/backgrounds/transaction_up.png',
                'colors': {
                    'api': ('#F9F9F9', (100, 65), (100, 107)),
                    'metric': ('#2BD713', (465, 65), (465, 103))
                }
            }
        }
    },
}

# Dictionary with default period of days for plots:
days = {
    'etfs': 90,
    'lightning': 30,
    'market': 1,
    'network': 30,
    'seized': 365
}

# Dictionary for connecting user messgaes with bot commands:
keyboard = {
    'blockchain': {
        'Address': 'address',
        'Block': 'block',
        'Transaction': 'transaction'
    },
    'history': {
        'Market': 'market',
        'Network': 'network',
        'Lightning': 'lightning',
        'ETFs': 'etfs',
        'Seized': 'seized'
    },
    'notifications': {
        'Market': 'market',
        'Network': 'network',
        'Lightning': 'lightning',
        'ETFs': 'etfs',
        'Seized': 'seized',
        'CEX': 'exchanges',
        'Pools': 'pools',
        'Fees': 'fees',
        'News': 'news'
    }
}
