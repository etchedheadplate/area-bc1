'''
Variables used for API calls and data display. Can be adjusted manually
within this module or/and via user interface in bot. All paths are relative.
'''


# Currency related variables
cryptocurrency = 'bitcoin'
crypto_ticker = 'BTC'
vs_currency = 'usd'
vs_ticker = vs_currency.upper()


# API related variables
api = {
    'coingecko': {
        'base': 'https://api.coingecko.com/api/v3/',
        'endpoint' : {
            'data_chart': {
                'name': f'coins/{cryptocurrency}/market_chart',
                'params': {
                    'vs_currency': f'{vs_currency}',
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
            'data_granular': {
                'name': f'coins/{cryptocurrency}',
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
    }
}


# Database related variables
databases = {
    'data_granular_latest': {
        'api': 'coingecko',
        'type': 'data_granular',
        'path': 'db/data_granular_latest.txt',
        'update': {
            'time': '00:30',
            'interval': 0.5,
            'allow_rewrite': True
        },
        'custom_params': {
            '': ''
        }
    },
    'data_chart_1_day': {
        'api': 'coingecko',
        'type': 'data_chart',
        'path': 'db/data_chart_1_day.csv',
        'update': {
            'time': '50:30',
            'interval': 0.5,
            'allow_rewrite': True
        },
        'custom_params': {
            'days': '1'
        }
    },
    'data_chart_90_days': {
        'api': 'coingecko',
        'type': 'data_chart',
        'path': 'db/data_chart_90_days.csv',
        'update': {
            'time': '05:30',
            'interval': 1,
            'allow_rewrite': True
        },
        'custom_params': {
            'days': '90'
        }
    },
    'data_chart_max_days': {
        'api': 'coingecko',
        'type': 'data_chart',
        'path': 'db/data_chart_max_days.csv',
        'update': {
            'time': '00:55:30',
            'interval': 24,
            'allow_rewrite': False
        },
        'custom_params': {
            'days': 'max'
        }
    },
}



# Market plot related variables
plot = {
    'path': 'src/images/plot/market_plot.png',
    'output': 'src/images/plot/market_plot_with_background.png',
    'font': 'src/font/font.ttf',
    'colors': {
        'date': 'white',
        'price': '#F7931A',
        'total_volume': '#1D910D', # 0E86D4
        'frame': 'black',
        '-inf_to_-ten': '#CB2B1B', # +
        '-ten_to_zero': '#CB2B1B', # +
        'zero_to_+ten': '#2BD713', # +
        '+ten_to_+inf': '#2BD713' # +
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
