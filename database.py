import os
import time
import pandas as pd
from datetime import datetime, timedelta

import config
from data_tools import get_api_data


def update_database(database):
    # Checks if database exists. If not creates empty database by template from user configuration
    # and updates it with new API data with regularity specified in user configuration.

    # Local user configuration related variables:
    db_file = config.database[f'{database}']['path']
    db_columns = config.database[f'{database}']['columns']
    db_update_time = config.database[f'{database}']['update']['time']
    db_update_interval = config.database[f'{database}']['update']['interval']
    db_update_allow_rewrite = config.database[f'{database}']['update']['allow_rewrite']

    # Local time-related variables formatted as specified in user configuration:
    time_current = datetime.strptime(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
    time_update = datetime.strptime(str(time_current)[:-len(db_update_time)] + db_update_time, '%Y-%m-%d %H:%M:%S')

    print(time_current, f'[{database}] update planned to {time_update}')

    # Check if current time > update time. If is, shifts update time by user configuration
    # specified update interval untill update time > current time.
    if time_current > time_update:
        time_update = time_update + timedelta(hours=db_update_interval)
        print(time_current, f'[{database}] current time > update time, update planned to {time_update}')

    seconds_untill_upgrade = (time_update - time_current).total_seconds()

    # Check if database exists. If not, empty database with template from user configuration created.
    print(time_current, f'[{database}] initializing:')
    if not os.path.isfile(db_file):
        db_template = pd.DataFrame(db_columns)
        db_template.to_csv(db_file, index=False)
        print(time_current, f'[{database}]', db_file, 'created')
    else:
        print(time_current, f'[{database}]', db_file, 'exists')

    # Regular database updates with new API data according to parameters defined by user configuration.
    while True:
        print(time_current, f'[{database}] updating:')

        # Call to API and creation of DataFrame objects based on response data:
        response = get_api_data(database)
        response_prices = pd.DataFrame(response['prices'], columns=['Date', 'Price'])
        response_market_cap = pd.DataFrame(response['market_caps'], columns=['Date', 'Market Cap'])
        response_total_volumes = pd.DataFrame(response['total_volumes'], columns=['Date', 'Total Volumes'])
        response_data = response_prices.merge(response_market_cap, on='Date', how='left').merge(response_total_volumes, on='Date', how='left')
        
        # If full database re-write is allowed by user configuration database is updated with response data.
        # If not, response is checked if it contains new rows. If does, database is updated with response data.
        current_data = pd.read_csv(db_file)
        if db_update_allow_rewrite:
            response_data.to_csv(db_file, index=False)
            print(time_current, f'[{database}]', len(response_data), f'entries re-written')
        else:
            if len(response_data) > len(current_data):
                response_data.to_csv(db_file, index=False)
                print(time_current, f'[{database}]', len(response_data) - len(current_data), f'entries added')
            else:
                print(time_current, f'[{database}] is up to date, no new entries')

        print(time_current, f'[{database}] next update planned to {time_update}')

        # Update database with regularity specified in user configuration.:
        time.sleep(seconds_untill_upgrade)


if __name__ == '__main__':
    databases = list(config.database.keys())
    for db in databases:
        update_database(db)