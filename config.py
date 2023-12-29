'''
Variables used for API calls and data display. Can be adjusted manually
within this module or/and via user interface in bot. All paths are relative.
'''


# Currency related variables
cryptocurrency = 'bitcoin'
vs_currency = 'usd'
ticker = vs_currency.upper()


# API related variables
api = {
    'coingecko': {
        'base': 'https://api.coingecko.com/api/v3/',
        'endpoint' : {
            'latest': {
                'name': f'coins/{cryptocurrency}',
                'params': {
                    'localization': 'false',
                    'tickers': 'false',
                    'market_data': 'true',
                    'community_data': 'false',
                    'developer_data': 'false'
                },
            },
            'all-time': {
                'name': f'coins/{cryptocurrency}/market_chart',
                'params': { # Get historical market data include price, market cap, and 24h volume (granularity auto)
                    'vs_currency': f'{vs_currency}', # The target currency of market data (usd, eur, jpy, etc.)
                    'days': 'max', # 1,14,30,max
                    'interval': [],
                    'precision': '2' # full or any value between 0 - 18 to specify decimal place for currency price value
                }
            },
            '1_day': {
                'name': f'coins/{cryptocurrency}/market_chart',
                'params': { # Get historical market data include price, market cap, and 24h volume (granularity auto)
                    'vs_currency': f'{vs_currency}', # The target currency of market data (usd, eur, jpy, etc.)
                    'days': '1', # 1,14,30,max
                    'interval': '',
                    'precision': '2' # full or any value between 0 - 18 to specify decimal place for currency price value
                }
            },
            '90_days': {
                'name': f'coins/{cryptocurrency}/market_chart',
                'params': { # Get historical market data include price, market cap, and 24h volume (granularity auto)
                    'vs_currency': f'{vs_currency}', # The target currency of market data (usd, eur, jpy, etc.)
                    'days': '90', # 1,14,30,max
                    'interval': '',
                    'precision': '2' # full or any value between 0 - 18 to specify decimal place for currency price value
                }
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
database = {
#    'latest': {
#        'api': 'coingecko',
#        'path': 'db/latest_market_data.csv',
#        'columns': {
#            'Last Price': [],
#            'Market Cap': [],
#            'Tot.Volume': [],
#            'Δ24h Price': [],
#            'Δ24h M.Cap': [],
#            'Updated at': []
#        },
#        'update': {
#            'time': '00:30',
#            'interval': 0.5,
#            'allow_rewrite': True
#        }
#    },
    '1_day': {
        'path': 'db/history_market_data_1_day.csv',
        'api': 'coingecko',
        'columns': {
                'Date': [],
                'Price': [],
                'Market Cap': [],
                'Total Volumes': []
        },
        'update': {
            'time': '50:30',
            'interval': 0.5,
            'allow_rewrite': True
        }
    },
    '90_days': {
        'path': 'db/history_market_data_90_days.csv',
        'api': 'coingecko',
        'columns': {
                'Date': [],
                'Price': [],
                'Market Cap': [],
                'Total Volumes': []
        },
        'update': {
            'time': '05:30',
            'interval': 1,
            'allow_rewrite': True
        }
    },
    'all-time': {
        'path': 'db/history_market_data_all-time.csv',
        'api': 'coingecko',
        'columns': {
                'Date': [],
                'Price': [],
                'Market Cap': [],
                'Total Volumes': []
        },
        'update': {
            'time': '00:55:30',
            'interval': 24,
            'allow_rewrite': False
        }
    },
}

latest_market_values_file = 'db/latest_market_values.txt'


# Market plot related variables
plot = {
    'path': 'src/images/plot/market_plot.png',
    'font': 'src/font/font.ttf',
    'background': ( # filename, price range in %, DPI, X-coordinate, Y-coordinate
        ('src/images/plot/backgrounds/superbad.png', (-float('inf'), -10), 150, 800, 85), # (-inf to -10%]
        ('src/images/plot/backgrounds/bad.png', (-10, 0), 150, 100, 85), # (-10% to 0]
        ('src/images/plot/backgrounds/good.png', (0, 10), 150, 800, 85), # (0 to +10%]
        ('src/images/plot/backgrounds/supergood.png', (10, float('inf')), 150, 100, 85) # (+10% to +inf)
    ),
    'output': 'src/images/plot/output.png'
}