# Currency related variables:
currency_crypto = 'bitcoin'
currency_vs = 'usd'
currency_crypto_ticker = 'BTC'
currency_vs_ticker = currency_vs.upper()
currency_pair = currency_crypto_ticker + currency_vs_ticker


# Dictionaries for managing databases:
charts = {
    'lightning': {
        'api': {
            'base': 'https://mempool.space/api/v1/',
            'endpoints': ['lightning/statistics/6y'],
            'params': False,
            'subdict': False,
            'parsed': 'dict'
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
            'params': {
                    'vs_currency': f'{currency_vs}',
                    'days': '1',
                    'interval': '',
                    'precision': '2'
                },
            'subdict': False,
            'parsed': 'list'
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
            'params': {
                    'vs_currency': f'{currency_vs}',
                    'days': '90',
                    'interval': '',
                    'precision': '2'
                },
            'subdict': False,
            'parsed': 'list'
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
            'base': 'https://api.coingecko.com/api/v3/',
            'endpoints': [f'coins/{currency_crypto}/market_chart'],
            'params': {
                    'vs_currency': f'{currency_vs}',
                    'days': 'max',
                    'interval': '',
                    'precision': '2'
                },
            'subdict': False,
            'parsed': 'list'
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
                'timespan': '6years',
                'rollingAverage': '1days',
                'start': '',
                'format': 'json',
                'sampled': 'true'
                },
            'subdict': 'values',
            'parsed': 'dict'
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
        }
    },
    'pools': {
        'api': {
            'base': 'https://api.blockchain.info/',
            'endpoints': ['pools'],
            'params': {
                'timespan': '7days'
                },
            'subdict': False,
            'parsed': 'dict'
        },
        'file': {
            'path': 'db/pools/',
            'name': 'pools.csv',
            'columns': ['pool', 'mined']
        }
    }
}

snapshots = {
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
        }
    }
}

delay = 15

updates = {
    # All numbers are primes to minimize chance of rate limit risk between diffirent databases with same API.
    # Charts and snapshots within same database updated with {delay} for the this reason also.

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
                'api': ('#F9F9F9', (950, 65), (950, 105)),
                'metric': ('#CACACA', (1315, 65), (1315, 105))
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
                'api': ('#F9F9F9', (950, 65), (950, 105)),
                'metric': ('#CACACA', (1315, 65), (1315, 105))
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
            'date': '#F9F9F9',
            'channels': '#e8086d',
            'capacity': '#F7931A',
            'nodes_clearnet': '#8b065a',
            'nodes_greynet': '#6f055a',
            'nodes_darknet': '#54055a',
            'nodes_unknown': '#38055a',
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
                    'api': ('#bc3a51', (100, 65), (100, 105)),
                    'metric': ('#e5383b', (100, 155), (100, 195))
                }
            },
            'key_metric_up': {
                'path': 'src/image/backgrounds/lightning_up.png',
                'range': (0, float('inf')),
                'coordinates': (795, 5),
                'colors': {
                    'api': ('#bc3a51', (100, 805), (100, 845)),
                    'metric': ('#2BD713', (100, 895), (100, 935))
                }
            }
        }
    },
    'market': {
        'path': f'db/market/{currency_pair}/',
        'font': 'src/font/font.ttf',
        'colors': {
            'date': '#F9F9F9',
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
                    'api': ('#ffd60a', (1900, 65), (1900, 105)),
                    'metric': ('#e5383b', (1900, 155), (1900, 195))
                }
            },
            'key_metric_up': {
                'path': 'src/image/backgrounds/market_up.png',
                'range': (0, float('inf')),
                'coordinates': (25, 5),
                'colors': {
                    'api': ('#ffd60a', (1900, 805), (1900, 845)),
                    'metric': ('#2BD713', (1900, 895), (1900, 935))
                    
                }
            }
        }
    },
    'network': {
        'path': 'db/network/',
        'font': 'src/font/font.ttf',
        'colors': {
            'date': '#F9F9F9',
            'price': '#F7931A',
            'hashrate': '#2a9d8f',
            'trx_per_block': '#e71d36',
            'frame': '#191716',
        },
        'backgrounds': {
            'key_metric_down': {
                'path': 'src/image/backgrounds/network_down.png',
                'range': (-float('inf'), 0),
                'coordinates': (795, 5),
                'colors': {
                    'api': ('#CACACA', (100, 805), (100, 845)),
                    'metric': ('#e5383b', (100, 895), (100, 935))
                }
            },
            'key_metric_up': {
                'path': 'src/image/backgrounds/network_up.png',
                'range': (0, float('inf')),
                'coordinates': (795, 5),
                'colors': {
                    'api': ('#CACACA', (100, 65), (100, 105)),
                    'metric': ('#2BD713', (100, 155), (100, 195))
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
            'date': '#F9F9F9',
            'usd': '#2b9348',
            'btc': '#F7931A',
            'price': '#F9F9F9',
            'frame': '#191716'
        },
        'backgrounds': {
            'path': 'src/image/backgrounds/seized.png',
            'coordinates': (725, 25),
            'colors': {
                'api': ('#F1603F', (180, 65), (180, 105)),
                'metric': ('#F7931A', (455, 65), (455, 100))
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
                    'api': ('#F9F9F9', (100, 65), (100, 105)),
                    'metric': ('#e5383b', (465, 65), (465, 105))
                }
            },
            'key_metric_up': {
                'path': 'src/image/backgrounds/transaction_up.png',
                'colors': {
                    'api': ('#F9F9F9', (100, 65), (100, 105)),
                    'metric': ('#2BD713', (465, 65), (465, 105))
                }
            }
        }
    },
}

