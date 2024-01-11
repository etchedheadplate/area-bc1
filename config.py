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

blockchain_chart = 'transactions-per-second'


# API related variables
api = {
    'coingecko': {
        'base': 'https://api.coingecko.com/api/v3/',
        'endpoint' : {
            'chart': {
                'name': f'coins/{currency_crypto}/market_chart',
                'type': 'json',
                'params': {
                    'vs_currency': f'{currency_vs}',
                    'days': '',
                    'interval': '',
                    'precision': '2'
                },
                'subdict': False,
                'columns': {
                    'Price': 'prices',
                    'Market Cap': 'market_caps',
                    'Total Volume': 'total_volumes'
                }
            },
            'values': {
                'name': f'coins/{currency_crypto}',
                'type': 'json',
                'params': {
                    'localization': 'false',
                    'tickers': 'false',
                    'market_data': 'true',
                    'community_data': 'false',
                    'developer_data': 'false'
                },
                'subdict': 'market_data',
            }
        },
        'error': { # Dictionary of API error codes specific to CoinGecko API
            400: "Bad Request",
            403: "Forbidden",
            404: "Something is wrong, check syntaxis",
            401: "Unauthorised",
            429: "Too many requests",
            500: "Internal Server Error",
            503: "Service Unavailable",
            1020: "Acces Denied",
            10002: "API Key Missing",
            10005: "Request limited to PRO API"
        }
    },
    'blockchain.com': {
        'base': 'https://api.blockchain.info/',
        'endpoint': {
            'chart': {
                'name': f'{blockchain_chart}',
                'type': 'csv',
                'params': {
                    'timespan': '5weeks',
                    'rollingAverage': '8hours',
                    'start': '',
                    'format': 'csv',
                    'sampled': 'true'
                },
                'subdict': False,
                'columns': {
                    '': ''
                }
            },
            'values': {
                'name': 'stats',
                'type': 'json',
                'params': {
                    '': ''
                },
                'subdict': False,
                'columns': {
                    '': ''
                }
            }
        }
    }
}


# Database related variables
databases = {
    'market': {
        'latest_raw_values': {
            'api': 'coingecko',
            'type': 'values',
            'filename': 'latest_raw_values.json',
            'path': f'db/market/{currency_pair}/latest/',
            'update': {
                'time': '00:30',
                'interval': 0.25,
                'allow_rewrite': True
            },
            'custom_params': {
                '': ''
            }
        },
        'latest_chart': {
            'api': 'coingecko',
            'type': 'chart',
            'path': f'db/market/{currency_pair}/latest/',
            'update': {
                'time': '50:30',
                'interval': 0.25,
                'allow_rewrite': True
            },
            'custom_params': {
                'days': '1'
            }
        },
        'history_chart_days_90': {
            'api': 'coingecko',
            'type': 'chart',
            'path': f'db/market/{currency_pair}/history/',
            'update': {
                'time': '10:30',
                'interval': 1,
                'allow_rewrite': True
            },
            'custom_params': {
                'days': '90'
            }
        },
        'history_chart_days_max': {
            'api': 'coingecko',
            'type': 'chart',
            'path': f'db/market/{currency_pair}/history/',
            'update': {
                'time': '00:55:30',
                'interval': 24,
                'allow_rewrite': False
            },
            'custom_params': {
                'days': 'max'
            }
        }
    },
    'blockchain': {

    },
    'transactions': {
        
    }
}


# Market plot related variables
plot = {
    'path': f'db/market/{currency_pair}/',
    'font': 'src/font/font.ttf',
    'colors': {
        'date': 'white',
        'price': '#F7931A',
        'total_volume': '#1D910D',
        'frame': 'black',
        '-inf_to_-ten': '#CB2B1B',
        '-ten_to_zero': '#CB2B1B',
        'zero_to_+ten': '#2BD713',
        '+ten_to_+inf': '#2BD713'
    },
    'backgrounds': {
        '-inf_to_-ten': {
                'path': 'src/images/plot/backgrounds/superbad.png',
                'range': (-float('inf'), -10),
                'coordinates': (795, 5)
        },
        '-ten_to_zero': {
                'path': 'src/images/plot/backgrounds/bad.png',
                'range': (-10, 0),
                'coordinates': (25, 5)
        },
        'zero_to_+ten': {
                'path': 'src/images/plot/backgrounds/good.png',
                'range': (0, 10),
                'coordinates': (795, 5)
        },
        '+ten_to_+inf': {
                'path': 'src/images/plot/backgrounds/supergood.png',
                'range': (10, float('inf')),
                'coordinates': (25, 5)
        },
    }
}
