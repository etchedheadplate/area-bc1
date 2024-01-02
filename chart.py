import os
import time
import pandas as pd
from datetime import datetime, timedelta

import config
from tools import get_api_data


def update_data_chart(data_chart):
    # Checks if data chart exists. If not creates empty data chart by template from user
    # configuration and updates it with new API data with regularity specified in user configuration.

    # User configuration related variables:
    data_chart_api = config.databases[f'{data_chart}']['api']
    data_chart_type = config.databases[f'{data_chart}']['type']
    data_chart_file = config.databases[f'{data_chart}']['path']
    data_chart_columns = config.api[f'{data_chart_api}']['endpoint'][f'{data_chart_type}']['columns']
    data_chart_update_time = config.databases[f'{data_chart}']['update']['time']
    data_chart_update_interval = config.databases[f'{data_chart}']['update']['interval']
    data_chart_update_allow_rewrite = config.databases[f'{data_chart}']['update']['allow_rewrite']

    # Check if data chart exists. If not, empty data chart with template from user configuration created.
    print(f'[{data_chart}] initializing:')
    if not os.path.isfile(data_chart_file):
        data_chart_template = pd.DataFrame(data_chart_columns.keys())
        data_chart_template.to_csv(data_chart_file, index=False)
        print(f'[{data_chart}]', data_chart_file, 'created')
    else:
        print(f'[{data_chart}]', data_chart_file, 'exists')

    # Regular data chart updates with new API data according to parameters defined by user configuration.
    while True:

        # Time-related variables formatted as specified in user configuration:
        time_current = datetime.strptime(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
        time_update = datetime.strptime(str(time_current)[:-len(data_chart_update_time)] + data_chart_update_time, '%Y-%m-%d %H:%M:%S')

        print(time_current, f'[{data_chart}] updating:')

        # Call to API and creation of DataFrame objects based on response data:
        response = get_api_data(data_chart)
        response_columns = pd.DataFrame({'Date': []})

        for column, row in data_chart_columns.items():
            response_data = pd.DataFrame(response[row], columns=['Date', f'{column}'])
            response_columns = response_columns.merge(response_data, on='Date', how='outer')

        response_columns = response_columns.drop_duplicates('Date')
        
        # If full data chart re-write is allowed by user configuration, data chart is updated with response data.
        # If not, response is checked if it contains new rows. If does, data chart is updated with response data.
        current_data = pd.read_csv(data_chart_file)
        if data_chart_update_allow_rewrite:
            response_columns.to_csv(data_chart_file, index=False)
            print(time_current, f'[{data_chart}]', len(response_columns), f'entries re-written')
        else:
            if len(response_columns) > len(current_data):
                response_columns.to_csv(data_chart_file, index=False)
                print(time_current, f'[{data_chart}]', len(response_columns) - len(current_data), f'entries added')
            else:
                print(time_current, f'[{data_chart}] is up to date, no new entries')

        # Schedule next update time. Check if current time > update time. If is, shift update time
        # by user configuration specified update interval untill update time > current time.
        if time_current > time_update:
            time_update = time_update + timedelta(hours=data_chart_update_interval)
            print(time_current, f'[{data_chart}] current time > update time, update planned to {time_update}')
        else:
            print(time_current, f'[{data_chart}] update planned to {time_update}')

        seconds_untill_upgrade = (time_update - time_current).total_seconds()

        # Update data chart with regularity specified in user configuration.:
        time.sleep(seconds_untill_upgrade)


if __name__ == '__main__':
    update_data_chart('data_chart_max_days')