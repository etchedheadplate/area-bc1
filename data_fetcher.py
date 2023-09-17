import requests
from api.coingecko import API_ERROR_CODES, API_ENDPOINTS

def build_api_url(base, endpoint, **kwargs):
    # Builds URL with specific query parameters to API endpoint
    query_parameters = [] # empty list for query parameters
    for key, value in kwargs.items():
        query_parameters.append(f"{key}={value}") # parameters are copied from dictionary to list...
    url = f"{base}{endpoint}?{'&'.join(query_parameters)}" # ...so they can be formated correctly to queries...
    return url # ... and returned as correct URL to API endpoint 

def get_json_data(url):
    # Returns JSON object or error code
    response = requests.get(url) # executes GET command to endpoint
    if response.status_code == 200: # if status code is OK... 
        data = response.json() # ...builds JSON object...
        return data # ...and returns JSON object
    elif response.status_code in API_ERROR_CODES: # if known error status code is recieved...
        return f'{response.status_code}:{API_ERROR_CODES[response.status_code]}' # ...returns status code and description
    else:
        return response.status_code, 'Unknown error' # if error is unknown returns status code

def view_json_contents(json, indent=0):
    # Allows to view nested dictionaries in human-readable form
    for key, value in json.items():
        if isinstance(value, dict): # if value is nested dictionary
            print(' ' * indent + f'{key}:') # prints key associated with value as nested dictionary
            view_json_contents(value, indent + 4) # recursively calls view_json_contents() until no nested dictionaries left
        else:
            print(' ' * indent + f'{key}: {value}') # prints key and value

def get_data(base, endpoint):
    # Returns unformatted dictionary with data provided by API endpoint
    endpoint_base = base
    endpoint_params = API_ENDPOINTS.get(endpoint)
    endpoint_url = build_api_url(endpoint_base, endpoint, **endpoint_params)
    endpoint_data = get_json_data(endpoint_url)
    return endpoint_data