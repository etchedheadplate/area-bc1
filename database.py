import os
import time
import json
import pandas as pd
from datetime import datetime, timedelta

import config
from tools import get_api_data, select_chart


def get_chart_data(days):
    # Checks if data chart exists. If not, creates empty data chart by user configuration
    # template and updates it with new API data with regularity specified in user configuration.

    # User configuration related variables:
    chart = select_chart(days)[0]
    chart_api = config.databases[f'{chart}']['api']
    chart_type = config.databases[f'{chart}']['type']
    chart_path = config.databases[f'{chart}']['path']
    chart_file = chart_path + chart + '.csv'
    chart_columns = config.api[f'{chart_api}']['endpoint'][f'{chart_type}']['columns']
    chart_update_time = config.databases[f'{chart}']['update']['time']
    chart_update_interval = config.databases[f'{chart}']['update']['interval']
    chart_update_allow_rewrite = config.databases[f'{chart}']['update']['allow_rewrite']

    # Create data chart directory if it doesn' exists:
    print(f'[{chart}] initializing:')
    if not os.path.isdir(chart_path):
        os.makedirs(chart_path, exist_ok=True)
        print(f'[{chart}]', chart_path, 'created')
    else:
        print(f'[{chart}]', chart_path, 'exists')

    # Create empty data chart with template from user configuration
    chart_template = pd.DataFrame(chart_columns.keys())
    chart_template.to_csv(chart_file, index=False)

    # Regular data chart updates with new API data according to parameters defined by user configuration:
    while True:

        # Time-related variables formatted as specified in user configuration for correct update period:
        time_current = datetime.strptime(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
        time_update = datetime.strptime(str(time_current)[:-len(chart_update_time)] + chart_update_time, '%Y-%m-%d %H:%M:%S')

        print(time_current, f'[{chart}] updating...')

        # Call to API and creation of DataFrame objects based on response data:
        response = get_api_data(chart)
        response_columns = pd.DataFrame({'Date': []})

        for column, row in chart_columns.items():
            response_data = pd.DataFrame(response[row], columns=['Date', f'{column}'])
            response_columns = response_columns.merge(response_data, on='Date', how='outer')

        response_columns = response_columns.drop_duplicates('Date')
        
        # If full data chart re-write is allowed by user configuration, data chart is updated with response data.
        # If not, response is checked if it contains new rows. If does, data chart is updated with response data.
        current_data = pd.read_csv(chart_file)

        if chart_update_allow_rewrite:
            response_columns.to_csv(chart_file, index=False)
            print(time_current, f'[{chart}]', len(response_columns), f'entries re-written')
        else:
            if len(response_columns) > len(current_data):
                response_columns.to_csv(chart_file, index=False)
                print(time_current, f'[{chart}]', len(response_columns) - len(current_data), f'entries added')
            else:
                print(time_current, f'[{chart}] is up to date, no new entries')

        # Calculation of Supply column
        current_data = pd.read_csv(chart_file)
        current_data['Supply'] = current_data['Market Cap'] / current_data['Price']
        current_data.to_csv(chart_file, index=False)

        # Schedule next update time. Check if current time > update time. If is, shift update time
        # by user configuration specified update interval untill update time > current time.
        while time_current > time_update:
            time_update = time_update + timedelta(hours=chart_update_interval)
            print(time_current, f'[{chart}] current time > update time, update planned to {time_update}')
        else:
            print(time_current, f'[{chart}] update planned to {time_update}')

        seconds_untill_upgrade = (time_update - time_current).total_seconds()

        # Update data chart with regularity specified in user configuration:
        time.sleep(seconds_untill_upgrade)


def get_values_data():
    # Makes API call and parses JSON response to values variables. Variables formatted
    # for user presentation. Data is updated with regularity specified in user configuration.

    # User configuration related variables:
    latest_api_data = config.databases['latest_api_data']
    latest_api_data_path = latest_api_data['path']
    latest_api_data_file = latest_api_data_path + latest_api_data['filename']
    latest_api_data_update_time = latest_api_data['update']['time']
    latest_api_data_update_interval = latest_api_data['update']['interval']

    # Regular values updates with new API data according to parameters defined by user configuration:
    while True:

        # Time-related variables formatted as specified in user configuration for correct update period:
        time_current = datetime.strptime(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
        time_update = datetime.strptime(str(time_current)[:-len(latest_api_data_update_time)] + latest_api_data_update_time, '%Y-%m-%d %H:%M:%S')

        print(time_current, '[latest_api_data] updating...')

        # Call to API and creation of values variables based on response data:
        response = get_api_data('latest_api_data')
    
        with open(latest_api_data_file, 'w') as json_file:
            json.dump(response, json_file)
            print(time_current, '[latest_api_data] is up to date')
        
        # Schedule next update time. Check if current time > update time. If is, shift update time
        # by user configuration specified update interval untill update time > current time.
        while time_current > time_update:
            time_update = time_update + timedelta(hours=latest_api_data_update_interval)
            print(time_current, f'[latest_api_data] current time > update time, update planned to {time_update}')
        else:
            print(time_current, f'[latest_api_data] update planned to {time_update}')

        print(time_current, '[latest_api_data] latest_values written')

        seconds_untill_upgrade = (time_update - time_current).total_seconds()

        # Update data chart with regularity specified in user configuration:
        time.sleep(seconds_untill_upgrade)




if __name__ == '__main__':
#    get_chart_data(111)
    get_values_data()