import time
import concurrent.futures

from market import (get_chart,
                    get_latest_raw_values,
                    make_plot,
                    write_latest_values,
                    write_history_values)



def run_parallel_database_update():

    with concurrent.futures.ThreadPoolExecutor() as executor:
        
        first_launch_interval = 20

        update_latest_raw_values = executor.submit(get_latest_raw_values)
        time.sleep(first_launch_interval)

        charts = ['max', 90, 1]
        for chart in charts:
            update_chart_data = executor.submit(get_chart, chart)
            time.sleep(first_launch_interval)


        concurrent.futures.wait([update_latest_raw_values] + [update_chart_data])


    
if __name__ == '__main__':

    run_parallel_database_update()