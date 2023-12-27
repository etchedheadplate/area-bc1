import os
import time
import pandas as pd
from datetime import datetime, timedelta
from data_tools import get_data
from config import api, database


# Global variables based on user configuration:

base = api['coingecko']['base']

history_endpoint = api['coingecko']['endpoint']['history']['name']
history_params = api['coingecko']['endpoint']['history']['params']
history_database = database['history']


def initialize_database(database):
    # Checks if database exists. If not creates empty one with pre-defined columns

    print('Initializing database:')
    if not os.path.isfile(database['path']): # Check if data filedatabase exists
        database_columns = database['columns']
        database_template = pd.DataFrame(database_columns)
        database_template.to_csv(database['path'], index=False) # Save DataFrame to CSV database without index
        print(f"{database['path']} created")
    else:
        print(f"{database['path']} exists")


def update_database(base, endpoint, database):
    # Updates database with data recieved from API call to CoinGecko
    while True:
        # Local time-related variables for regular database updates:
        current_time = datetime.now()
        next_update = current_time + timedelta(hours=1)
        time_difference = (next_update - current_time).total_seconds()
        
        current_data = pd.read_csv(database['path'])
        
        print(current_time, 'Updating database:')

        # Call to CoinGecko API and creation of DataFrame objects based on response data:
        response = get_data(base, endpoint)
        response_prices = pd.DataFrame(response['prices'], columns=['Date', 'Price'])
        response_market_cap = pd.DataFrame(response['market_caps'], columns=['Date', 'Market Cap'])
        response_total_volumes = pd.DataFrame(response['total_volumes'], columns=['Date', 'Total Volumes'])
        response_data = response_prices.merge(response_market_cap, on='Date', how='left').merge(response_total_volumes, on='Date', how='left')
        
        # Check if current data is empty or not. If empty, updates it with response data.
        # If not, updates it with rows from response data that are absent in current data:
        if not current_data.empty:
            if len(response_data) > len(current_data):
                updated_data = pd.concat([current_data, response_data]).drop_duplicates()
                updated_data.to_csv(database['path'], index=False)
                print(current_time, len(response_data) - len(current_data), f"entries added to {database['path']}")
            else:
                print(current_time, f"{database['path']} is up to date")
        else:
            response_data.to_csv(database['path'], index=False)
            print(current_time, len(response_data) - len(current_data), f"entries added to {database['path']}")

        # Update database in 1 hour:
        time.sleep(time_difference)


initialize_database(history_database)
update_database(base, history_endpoint, history_database)