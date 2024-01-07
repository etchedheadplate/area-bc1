import time
import concurrent.futures

from database import get_chart_data, get_values_data



def run_parallel_database_update():

    with concurrent.futures.ThreadPoolExecutor() as executor:
        
        first_launch_interval = 20

        update_values_data = executor.submit(get_values_data)

        charts = ['max', 90, 1]
        for chart in charts:
            update_chart_data = executor.submit(get_chart_data, chart)
            time.sleep(first_launch_interval)


        concurrent.futures.wait([update_values_data] + [update_chart_data])



if __name__ == '__main__':

    run_parallel_database_update()