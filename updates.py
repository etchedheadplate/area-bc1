import time
import concurrent.futures

from lightning import get_lightning_chart, get_lightning_latest_raw_values
from market import get_market_chart, get_market_latest_raw_values
from network import get_network_chart, get_network_latest_raw_values


def run_parallel_database_update():
    # Runs concurrent updates for all databases.

    # Create concurrent executor:
    with concurrent.futures.ThreadPoolExecutor() as executor:
        
        # Set interval to comply with API providers rate limits:
        first_launch_interval = 20

        # Submit functions to executor:
        update_lightning_chart_data = executor.submit(get_lightning_chart)
        time.sleep(first_launch_interval)
        update_lightning_latest_raw_values = executor.submit(get_lightning_latest_raw_values)
        time.sleep(first_launch_interval)
        update_network_chart_data = executor.submit(get_network_chart)
        time.sleep(first_launch_interval)
        update_market_latest_raw_values = executor.submit(get_market_latest_raw_values)
        time.sleep(first_launch_interval)
        update_network_latest_raw_values = executor.submit(get_network_latest_raw_values)
        time.sleep(first_launch_interval)
        charts = ['max', 90, 1]
        for chart in charts:
            update_market_chart_data = executor.submit(get_market_chart, chart)
            time.sleep(first_launch_interval)

        # Launch executor:
        concurrent.futures.wait(
            [update_lightning_chart_data] +
            [update_lightning_latest_raw_values] +
            [update_network_chart_data] +
            [update_market_latest_raw_values] +
            [update_network_latest_raw_values] +
            [update_market_chart_data])

    
if __name__ == '__main__':

    run_parallel_database_update()