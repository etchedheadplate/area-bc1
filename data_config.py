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

# Market plot related variables
plot_path = 'src/images/market_plot.png'
plot_font = 'src/font/south_park.ttf'
plot_background_path = 'src/images/backgrounds/'
plot_background_image = ( # filename, price range in %, DPI, X-coordinate, Y-coordinate
    (plot_background_path + 'superbad.png', (-float('inf'), -10), 150, 800, 85), # -inf to -10%
    (plot_background_path + 'bad.png', (-10, 0), 150, 100, 85), # -10% to 0
    (plot_background_path + 'good.png', (0, 10), 150, 800, 85), # 0 to +10%
    (plot_background_path + 'supergood.png', (10, float('inf')), 150, 100, 85) # +10% to +inf
)