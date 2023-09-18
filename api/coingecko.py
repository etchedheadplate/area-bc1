BASE = 'https://api.coingecko.com/api/v3/'

API_ENDPOINTS = { # Dictionary of all API endpoids available for free by CoinGecko
    '/simple/price':{
        'ids':'bitcoin',
        'vs_currencies':'usd', # The target currency of market data (usd, eur, jpy, etc.)
        'include_market_cap':'true',
        'include_24hr_vol':'true',
        'include_24hr_change':'true',
        'include_last_updated_at':'true',
        'precision':"2" # full or any value between 0 - 18 to specify decimal place for currency price value
    },
    '/coins/markets':{ # ERROR: list, not dict //
        'vs_currency':'usd', # The target currency of market data (usd, eur, jpy, etc.)
        'ids':'bitcoin',
        'order':'market_cap_desc',
        'per_page':'100',
        'page':'1',
        'sparkline':'false',
        'price_change_percentage':'1h%2C24h%2C7d', # 1h,24h,7d,14d,30d,200d,1y
        'locale':'en',
        'precision':'2' # full or any value between 0 - 18 to specify decimal place for currency price value
    },
    'coins/bitcoin':{
        'localization':'true',
        'tickers':'true',
        'market_data':'true',
        'community_data':'true',
        'developer_data':'true'
    },
    'coins/bitcoin/history':{ # Get historical data at a given date for a coin. The data returned is at 00:00:00 UTC.
        'date':'01-01-2010', # dd-mm-yyyy
        'localization':'false'
    },
    'coins/bitcoin/market_chart':{ # Get historical market data include price, market cap, and 24h volume (granularity auto)
        'vs_currency':'usd', # The target currency of market data (usd, eur, jpy, etc.)
        'days':'30', # 1,14,30,max
        'interval':'daily',
        'precision':'2' # full or any value between 0 - 18 to specify decimal place for currency price value
    },
    'coins/bitcoin/market_chart/range':{ # Get historical market data include price, market cap, and 24h volume within a range of timestamp (granularity auto)
        'vs_currency':'usd', # The target currency of market data (usd, eur, jpy, etc.)
        'from':'1392577232', # From date in UNIX Timestamp
        'to':'1422577232', # To date in UNIX Timestamp
        'precision':'2' # full or any value between 0 - 18 to specify decimal place for currency price value
    },
    'coins/bitcoin/ohlc':{ # ERROR: list, not dict // Open-high-low-close chart
        'vs_currency':'usd', # The target currency of market data (usd, eur, jpy, etc.)
        'days':'7',# Data up to number of days ago (1/7/14/30/90/180/365/max)
        'precision':'2' # full or any value between 0 - 18 to specify decimal place for currency price value
    },
    'exchange_rates':'' # BTC-to-Currency exchange rates
}

API_ERROR_CODES = { # Dictionary of API error codes specific to CoinGecko API
    400:"Bad Request",
    403:"Forbidden",
    404:"omething is wrong, check syntaxis",
    401:"Unauthorised",
    429:"Too many requests",
    500:"Internal Server Error",
    503:"Service Unavailable",
    1020:"Acces Denied",
    10002:"API Key Missing",
    10005:"Request limited to PRO API"
}

SUPPORTED_VS_CURRENCIES = [ # List of symbols of all currencies available on CoinGecko
    "btc",
    "eth",
    "ltc",
    "bch",
    "bnb",
    "eos",
    "xrp",
    "xlm",
    "link",
    "dot",
    "yfi",
    "usd",
    "aed",
    "ars",
    "aud",
    "bdt",
    "bhd",
    "bmd",
    "brl",
    "cad",
    "chf",
    "clp",
    "cny",
    "czk",
    "dkk",
    "eur",
    "gbp",
    "hkd",
    "huf",
    "idr",
    "ils",
    "inr",
    "jpy",
    "krw",
    "kwd",
    "lkr",
    "mmk",
    "mxn",
    "myr",
    "ngn",
    "nok",
    "nzd",
    "php",
    "pkr",
    "pln",
    "rub",
    "sar",
    "sek",
    "sgd",
    "thb",
    "try",
    "twd",
    "uah",
    "vef",
    "vnd",
    "zar",
    "xdr",
    "xag",
    "xau",
    "bits",
    "sats"
]

