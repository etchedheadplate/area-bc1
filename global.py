import requests
import simplejson as json
from coingecko_api import API_ERROR_CODES, API_ENDPOINTS, ID

'''
Function builds URL to API endpoint, executes GET command and
returns JSON object if response status code is OK. Otherwise
returns error code and tries to point to specific problem.
'''

def json_contents(endpoint):
    base = 'https://api.coingecko.com/api/v3'
    url = base + endpoint
    response = requests.get(url) # request for JSON object associated with endpoint
    if response.status_code == 200: # if status code is OK... 
        data = response.json() # ...builds JSON object...
        return data # ...and returns JSON object
    elif response.status_code in API_ERROR_CODES: # if known error status code is recieved...
        return f'{response.status_code}:{API_ERROR_CODES[response.status_code]}' # ...returns status code and description
    else:
        return response.status_code, 'Unknown error' # if error is unknown returns status code

'''
Dictionary with availble CoinGecko API endpoints is represented
as a list, which is printed with associated indexes, so user can
choose needed endpoint just by entering number of endpoint. JSON
contents are printed in user-friendly form.
'''

endpoints = [(key, value) for key, value in API_ENDPOINTS.items()] # API endpoints as a list

for cnt, endpoint in enumerate(endpoints):
    print(cnt, endpoint[0]) # prints API endpoints in user-friendly form with associated index

api_number = int(input('Choose API endpoint: ')) # expects integer for list index

endpoint_name = endpoints[api_number][0].replace('{id}', ID) # specifies Bitcoin as asset of interest
endpoint_contents = json_contents(endpoint_name)
print(json.dumps(endpoint_contents, sort_keys=True, indent=4 * ' ')) # JSON contents are printed