import requests
import simplejson as json
from api.coingecko import API_ERROR_CODES, API_ENDPOINTS

base = 'https://api.coingecko.com/api/v3/'
endpoint = '/simple/price'
endpoint_params = API_ENDPOINTS.get(endpoint)

'''
Function builds URL with specific query parameters to API endpoint.
'''

def build_api_url(base, endpoint, **kwargs):
    query_parameters = [] # empty list for query parameters
    for key, value in kwargs.items():
        query_parameters.append(f"{key}={value}") # parameters are copied from dictionary to list...
    url = f"{base}{endpoint}?{'&'.join(query_parameters)}" # ...so they can be formated correctly to queries...
    return url # ... and returned as correct URL to API endpoint 

'''
Function executes GET command to URL and returns JSON object if response status
code is OK. Otherwise returns error code and tries to point to specific problem.
'''

def get_json_data(url):
    response = requests.get(url) # request for JSON object associated with endpoint
    if response.status_code == 200: # if status code is OK... 
        data = response.json() # ...builds JSON object...
        return data # ...and returns JSON object
    elif response.status_code in API_ERROR_CODES: # if known error status code is recieved...
        return f'{response.status_code}:{API_ERROR_CODES[response.status_code]}' # ...returns status code and description
    else:
        return response.status_code, 'Unknown error' # if error is unknown returns status code

'''
Function allows to view nested dictionaries in human-readable form.
'''

def view_json_contents(json, indent=0): 
    for key, value in json.items():
        if isinstance(value, dict): # if value is nested dictionary
            print(' ' * indent + f'{key}:') # prints key associated with value as nested dictionary
            view_json_contents(value, indent + 4) # recursively calls view_json_contents() until no nested dictionaries left
        else:
            print(' ' * indent + f'{key}: {value}') # prints key and value

test_url = build_api_url(base, endpoint, **endpoint_params)
test_get_json_data = get_json_data(test_url)
test_view_json_contents = view_json_contents(test_get_json_data)
'''print(test_view_json_contents)'''

data_source = view_json_contents(get_json_data(build_api_url(base, endpoint, **endpoint_params)))