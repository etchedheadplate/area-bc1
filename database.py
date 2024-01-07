import os
import time
import json
import pandas as pd
from datetime import datetime, timedelta

import config
from tools import get_api_data, select_chart
from plot import make_history_plot
from values import write_history_values, write_latest_values


def get_chart_data(days):
    # Checks if chart exists. If not, creates empty chart with columns specified in user configuration
    # and updates it with new API data with regularity specified in user configuration.

    # User configuration related variables:
    chart_name = select_chart(days)[0]
    chart_api = config.databases[f'{chart_name}']['api']
    chart_type = config.databases[f'{chart_name}']['type']
    chart_path = config.databases[f'{chart_name}']['path']
    chart_file = chart_path + chart_name + '.csv'
    chart_columns = config.api[f'{chart_api}']['endpoint'][f'{chart_type}']['columns']
    chart_update_time = config.databases[f'{chart_name}']['update']['time']
    chart_update_interval = config.databases[f'{chart_name}']['update']['interval']
    chart_update_allow_rewrite = config.databases[f'{chart_name}']['update']['allow_rewrite']

    # Create data chart_name directory if it doesn' exists:
    if not os.path.isdir(chart_path):
        os.makedirs(chart_path, exist_ok=True)

    # Create empty data chart_name with template from user configuration
    chart_template = pd.DataFrame(chart_columns.keys())
    chart_template.to_csv(chart_file, index=False)

    # Regular data chart updates with new API data according to parameters defined by user configuration
    while True:

        # Time-related variables formatted as specified in user configuration for correct update period:
        time_current = datetime.strptime(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
        time_update = datetime.strptime(str(time_current)[:-len(chart_update_time)] + chart_update_time, '%Y-%m-%d %H:%M:%S')

        # Call to API and creation of DataFrame objects based on response data:
        response = get_api_data(chart_name)
        response_columns = pd.DataFrame({'Date': []})

        for column, row in chart_columns.items():
            response_data = pd.DataFrame(response[row], columns=['Date', f'{column}'])
            response_columns = response_columns.merge(response_data, on='Date', how='outer')

        response_columns = response_columns.drop_duplicates('Date')
        
        # If full data chart_name re-write is allowed by user configuration, data chart_name is updated with response data.
        # If not, response is checked if it contains new rows. If does, data chart_name is updated with response data.
        current_data = pd.read_csv(chart_file)

        if chart_update_allow_rewrite:
            response_columns.to_csv(chart_file, index=False)
            print(time_current, f'[{chart_name}]', len(response_columns), f'entries re-written')
        else:
            if len(response_columns) > len(current_data):
                response_columns.to_csv(chart_file, index=False)
                print(time_current, f'[{chart_name}]', len(response_columns) - len(current_data), f'entries added')
            else:
                print(time_current, f'[{chart_name}] no new entries')

        # Make chart plot and history values data:
        make_history_plot(days)
        print(time_current, f'[{chart_name}] plot updated')
        write_history_values(days)
        print(time_current, f'[{chart_name}] values updated')

        # Schedule next update time. Check if current time > update time. If is, shift update time
        # by user configuration specified update interval untill update time > current time.
        while time_current > time_update:
            time_update = time_update + timedelta(hours=chart_update_interval)
        else:
            print(time_current, f'[{chart_name}] update planned to {time_update}')

        seconds_untill_upgrade = (time_update - time_current).total_seconds()

        # Update data chart_name with regularity specified in user configuration:
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

    while True:

        # Time-related variables formatted as specified in user configuration for correct update period:
        time_current = datetime.strptime(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
        time_update = datetime.strptime(str(time_current)[:-len(latest_api_data_update_time)] + latest_api_data_update_time, '%Y-%m-%d %H:%M:%S')

        # Call to API and creation of values variables based on response data:
        response = get_api_data('latest_api_data')

        with open(latest_api_data_file, 'w') as json_file:
            json.dump(response, json_file)
            print(time_current, '[latest_api_data] re-written')
        
        # Make latest values data
        write_latest_values()
        print(time_current, '[latest_api_data] values updated')

        # Schedule next update time. Check if current time > update time. If is, shift update time
        # by user configuration specified update interval untill update time > current time.
        while time_current > time_update:
            time_update = time_update + timedelta(hours=latest_api_data_update_interval)
        else:
            print(time_current, f'[latest_api_data] update planned to {time_update}')

        seconds_untill_upgrade = (time_update - time_current).total_seconds()

        # Update data chart_name with regularity specified in user configuration:
        time.sleep(seconds_untill_upgrade)
