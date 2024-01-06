import os
import time
import pandas as pd
from datetime import datetime, timedelta

import config
from tools import get_api_data, select_history_chart


def update_history_chart(days):
    # Checks if data chart exists. If not, creates empty data chart by user configuration
    # template and updates it with new API data with regularity specified in user configuration.

    # User configuration related variables:
    history_chart = select_history_chart(days)[0]
    history_chart_api = config.databases[f'{history_chart}']['api']
    history_chart_type = config.databases[f'{history_chart}']['type']
    history_chart_path = config.databases[f'{history_chart}']['path']
    history_chart_file = history_chart_path + history_chart + '.csv'
    history_chart_columns = config.api[f'{history_chart_api}']['endpoint'][f'{history_chart_type}']['columns']
    history_chart_update_time = config.databases[f'{history_chart}']['update']['time']
    history_chart_update_interval = config.databases[f'{history_chart}']['update']['interval']
    history_chart_update_allow_rewrite = config.databases[f'{history_chart}']['update']['allow_rewrite']

    # Create data chart directory if it doesn' exists:
    print(f'[{history_chart}] initializing:')
    if not os.path.isdir(history_chart_path):
        os.makedirs(history_chart_path, exist_ok=True)
        print(f'[{history_chart}]', history_chart_path, 'created')
    else:
        print(f'[{history_chart}]', history_chart_path, 'exists')

    # Create empty data chart with template from user configuration
    history_chart_template = pd.DataFrame(history_chart_columns.keys())
    history_chart_template.to_csv(history_chart_file, index=False)

    # Regular data chart updates with new API data according to parameters defined by user configuration:
    while True:

        # Time-related variables formatted as specified in user configuration for correct update period:
        time_current = datetime.strptime(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
        time_update = datetime.strptime(str(time_current)[:-len(history_chart_update_time)] + history_chart_update_time, '%Y-%m-%d %H:%M:%S')

        print(time_current, f'[{history_chart}] updating:')

        # Call to API and creation of DataFrame objects based on response data:
        response = get_api_data(history_chart)
        response_columns = pd.DataFrame({'Date': []})

        for column, row in history_chart_columns.items():
            response_data = pd.DataFrame(response[row], columns=['Date', f'{column}'])
            response_columns = response_columns.merge(response_data, on='Date', how='outer')

        response_columns = response_columns.drop_duplicates('Date')
        
        # If full data chart re-write is allowed by user configuration, data chart is updated with response data.
        # If not, response is checked if it contains new rows. If does, data chart is updated with response data.
        current_data = pd.read_csv(history_chart_file)
        if history_chart_update_allow_rewrite:
            response_columns.to_csv(history_chart_file, index=False)
            print(time_current, f'[{history_chart}]', len(response_columns), f'entries re-written')
        else:
            if len(response_columns) > len(current_data):
                response_columns.to_csv(history_chart_file, index=False)
                print(time_current, f'[{history_chart}]', len(response_columns) - len(current_data), f'entries added')
            else:
                print(time_current, f'[{history_chart}] is up to date, no new entries')

        # Schedule next update time. Check if current time > update time. If is, shift update time
        # by user configuration specified update interval untill update time > current time.
        while time_current > time_update:
            time_update = time_update + timedelta(hours=history_chart_update_interval)
            print(time_current, f'[{history_chart}] current time > update time, update planned to {time_update}')
        else:
            print(time_current, f'[{history_chart}] update planned to {time_update}')

        seconds_untill_upgrade = (time_update - time_current).total_seconds()

        # Update data chart with regularity specified in user configuration:
        time.sleep(seconds_untill_upgrade)


if __name__ == '__main__':
    update_history_chart('max')