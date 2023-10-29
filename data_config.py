'''
Variables used for API calls and data display. Can be adjusted manually
within this module or/and via user interface in bot. All paths are relative.
'''


# Currency related variables
cryptocurrency = 'bitcoin'
vs_currency = 'usd'
ticker = vs_currency.upper()

# Database related variables
database_file = 'db/History_market_data.csv'

# Market chart related variables
chart_path = 'src/images/market_chart.png'
chart_font = 'src/font/south_park.ttf'
chart_background_path = 'src/images/backgrounds/'
chart_background_image = ( # filename, price range in %, DPI, X-coordinate, Y-coordinate
    ('superbad.png', (-float('inf'), -10), 150, 750, 85),
    ('bad.png', (-10, 0), 150, 750, 85),
    ('good.png', (0, 10), 150, 750, 85),
    ('supergood.png', (10, float('inf')), 150, 750, 85)
)