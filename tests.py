import requests
from coingecko_api import API_ENDPOINTS, ID
import time

for key in API_ENDPOINTS:
    endpoint = key.replace('{id}',ID)
    print(type(endpoint))
    base = 'https://api.coingecko.com/api/v3/'
    url = base + endpoint
    response = requests.get(url) # request for JSON object associated with endpoint
    data = response.json
    print(response.status_code, endpoint)
    time.sleep(6)