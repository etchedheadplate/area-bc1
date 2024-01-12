import os
from datetime import datetime
import pandas as pd

import config
from tools import get_api_data


chart = config.databases['blockchain_history_chart']

chart_api_base = chart['api']['base']
chart_api_endpoint = chart['api']['endpoint']
chart_api_params = chart['api']['params']
chart_api_subdict = chart['api']['subdict']

chart_file_path = chart['file']['path']
chart_file_name = chart['file']['name']
chart_columns = chart['file']['columns']
chart_file = chart_file_path + chart_file_name

chart_update_time = chart['update']['time']
chart_update_interval = chart['update']['interval']


def get_blockchain_history_chart_data():

    # Create chart directory if it doesn' exists:
    if not os.path.isdir(chart_file_path):
        os.makedirs(chart_file_path, exist_ok=True)

    # Empty DataFrame for later filling with response DataFrame:
    response_columns = pd.DataFrame({'Date': []})

    for endpoint in chart_api_endpoint:
        
        # Time-related variables formatted as specified in user configuration for correct calculation of update period:
        time_current = datetime.strptime(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
        time_update = datetime.strptime(str(time_current)[:-len(chart_update_time)] + chart_update_time, '%Y-%m-%d %H:%M:%S')

        # Special variable to tie endpoint with column name:
        column_name_index = chart_api_endpoint.index(endpoint)

        # Call to API and creation of DataFrame objects based on response data:
        response = get_api_data(
            chart_api_base,
            endpoint,
            chart_api_params,
            chart_api_subdict)

        # Response data assigned to columns specified in user configuration
        response_data = pd.DataFrame(response).rename(columns={'x': 'Date', 'y': f'{chart_columns[column_name_index]}'})
        response_columns = response_columns.merge(response_data, on='Date', how='outer')
    
    # Filled with response data DataFrame saved to file:
    response_columns.to_csv(chart_file, index=False)


if __name__ == '__main__':
    get_blockchain_history_chart_data()
