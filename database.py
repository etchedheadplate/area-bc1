import os
import time
import pandas as pd
from datetime import datetime, timedelta

import config
from data_tools import get_api_data


def update_database(database):
    # Checks if database exists. If not creates empty database with template
    # from user configuration and regulary updates it with new API data 

    # Local user configuration related variables:
    db_file = config.database[f'{database}']['path']
    db_columns = config.database[f'{database}']['columns']
    db_rewrite = config.database[f'{database}']['update']['rewrite']
  
    # Local time-related variables for regular database updates:
    current_time = datetime.now()
    update_interval = config.database[f'{database}']['update']['interval']
    next_update = current_time + timedelta(hours=update_interval)
    time_difference = (next_update - current_time).total_seconds()

    # Check if database exists. If not, empty database with template from user configuration created
    print(current_time, 'Initializing database:')
    if not os.path.isfile(db_file):
        db_template = pd.DataFrame(db_columns)
        db_template.to_csv(db_file, index=False)
        print(current_time, db_file, 'created')
    else:
        print(current_time, db_file, 'exists')

    # Regular database updates with new API data according to parameters defined by user configuration
    while True:
        print(current_time, 'Updating database:')

        # Call to API and creation of DataFrame objects based on response data:
        response = get_api_data(database)
        response_prices = pd.DataFrame(response['prices'], columns=['Date', 'Price'])
        response_market_cap = pd.DataFrame(response['market_caps'], columns=['Date', 'Market Cap'])
        response_total_volumes = pd.DataFrame(response['total_volumes'], columns=['Date', 'Total Volumes'])
        response_data = response_prices.merge(response_market_cap, on='Date', how='left').merge(response_total_volumes, on='Date', how='left')
        
        # Check if current data is empty or not. If empty, updates it with response data.
        # If not, updates it with rows from response data that are absent in current data:
        current_data = pd.read_csv(db_file)
        if db_rewrite:
            response_data.to_csv(db_file, index=False)
            print(current_time, len(response_data), 'entries re-written to', db_file)
        else:
            if len(response_data) > len(current_data):
                response_data.to_csv(db_file, index=False)
                print(current_time, len(response_data) - len(current_data), 'entries added to', db_file)
            else:
                print(current_time, db_file, 'is up to date, no new entries')

        # Update database in 1 hour:
        time.sleep(time_difference)


update_database('1_day')