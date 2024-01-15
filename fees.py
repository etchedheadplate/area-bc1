import io
import os
import time
import json
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter
from matplotlib import font_manager
from PIL import Image

import config
from tools import (get_api_data,
                   define_key_metric_movement,
                   calculate_percentage_change,
                   format_time_axis,
                   format_amount,
                   format_utc,
                   format_currency,
                   format_percentage,
                   format_quantity)






'''
Functions related to fetching fees data from Mempool Space API and updating
local database at ./db/fees/. All fees data stored localy as files which
are used as source of data for plots and values. All database files are updated
regulary as specified in user configuration.
'''


def get_fees_latest_raw_values():
    # Fetches raw API data for latest values and saves it to database.
    # Updates JSON file with regularity specified in user configuration.

    latest_raw_values_name = 'fees_latest_raw_values'

    # User configuration related variables:
    latest_raw_values = config.databases[f'{latest_raw_values_name}']
    latest_raw_values_api_base = latest_raw_values['api']['base']
    latest_raw_values_api_endpoint = latest_raw_values['api']['endpoint']
    latest_raw_values_file_path = latest_raw_values['file']['path']
    latest_raw_values_file_name = latest_raw_values['file']['name']
    latest_raw_values_file = latest_raw_values_file_path + latest_raw_values_file_name
    latest_raw_values_update_time = latest_raw_values['update']['time']
    latest_raw_values_update_interval = latest_raw_values['update']['interval']

    # Create directory for raw API data if it doesn' exists:
    if not os.path.isdir(latest_raw_values_file_path):
        os.makedirs(latest_raw_values_file_path, exist_ok=True)

    # Update raw API data for latest values:
    while True:

        # Time-related variables formatted as specified in user configuration for correct calculation of update period:
        time_current = datetime.strptime(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
        time_update = datetime.strptime(str(time_current)[:-len(latest_raw_values_update_time)] + latest_raw_values_update_time, '%Y-%m-%d %H:%M:%S')

        # Call to API and creation JSON file based on response data:
        response = get_api_data(
            latest_raw_values_api_base,
            latest_raw_values_api_endpoint)

        with open(latest_raw_values_file, 'w') as json_file:
            json.dump(response, json_file)
            print(time_current, f'[{latest_raw_values_name}] re-written')
        
#        # Write latest values data:
#        write_latest_values()
#        print(time_current, f'[{latest_raw_values_name}] values updated')

        # Schedule next update time. Check if current time > update time. If is, shift update time
        # by user configuration specified update interval untill update time > current time.
        while time_current > time_update:
            time_update = time_update + timedelta(hours=latest_raw_values_update_interval)
        else:
            print(time_current, f'[{latest_raw_values_name}] update planned to {time_update}')

        seconds_untill_upgrade = (time_update - time_current).total_seconds()

        # Update JSON file and latest values with regularity specified in user configuration:
        time.sleep(seconds_untill_upgrade)




get_fees_latest_raw_values()
