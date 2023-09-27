import requests
import time
import sys
import simplejson as json
from api.coingecko import API_ERROR_CODES, API_ENDPOINTS, BASE
from data_tools import get_data, view_json_contents

'''for key in API_ENDPOINTS:
    endpoint = key.replace('{id}',ID)
    print(type(endpoint))
    base = 'https://api.coingecko.com/api/v3/'
    url = base + endpoint
    response = requests.get(url) # request for JSON object associated with endpoint
    data = response.json
    print(response.status_code, endpoint)
    time.sleep(6)

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
        return response.status_code, 'Unknown error' # if error is unknown returns status code'''

'''
Dictionary with availble CoinGecko API endpoints is represented
as a list, which is printed with associated indexes, so user can
choose needed endpoint just by entering number of endpoint. JSON
contents are printed in user-friendly form.
'''

'''endpoints = [(key, value) for key, value in API_ENDPOINTS.items()] # API endpoints as a list

for cnt, endpoint in enumerate(endpoints):
    print(cnt, endpoint[0]) # prints API endpoints in user-friendly form with associated index

api_number = int(input('Choose API endpoint: ')) # expects integer for list index

endpoint_name = endpoints[api_number][0].replace('{id}', ID) # specifies Bitcoin as asset of interest
endpoint_contents = json_contents(endpoint_name)
print(json.dumps(endpoint_contents, sort_keys=True, indent=4 * ' ')) # JSON contents are printed'''

'''
test_dict = get_data(BASE, 'coins/bitcoin/market_chart/range')
with open('tests/output.txt', 'w') as file:
    sys.stdout = file
    print(view_json_contents(test_dict))
sys.stdout = sys.__stdout__
print(test_dict)
'''

'''from currency_symbols import CurrencySymbols

# Создайте объект CurrencySymbols
currency_symbols = CurrencySymbols()

# Указывайте код валюты для получения символа
currency_code = 'sats'
currency_symbol = currency_symbols.get_symbol(currency_code)

if currency_symbol:
    print(f"The symbol for {currency_code} is {currency_symbol}")
else:
    print(f"Symbol not found for {currency_code}")
'''

'''from money.money import Money
m = Money(amount='2.22', currency='EUR')
print(m)'''

'''def length_checker(file_path):
    file=open(file_path, 'r')
    file_lines = file.readlines()
    list_of_lines=[]
    for line in file_lines:
        list_of_lines.append(line)
    print(len(list_of_lines))
    file.close()'''

import matplotlib.pyplot as plt
import matplotlib.image as mpimg

# Создайте график (фигуру)
fig, ax = plt.subplots()

# Размер графика
fig.set_size_inches(6, 4)

# Загрузите изображение для фона
bg_image = mpimg.imread('tests/background.jpg')  # Замените 'background_image.png' на путь к вашему фоновому изображению

# Создайте субграфик (axes)
ax = fig.add_subplot(111)

# Отобразите фоновое изображение за пределами сетки координат
ax.imshow(bg_image, aspect='auto', extent=[0, 1, 0, 1], zorder=-1)  # aspect='auto' подстраивает размер изображения под график

# Рисуйте ваш график на сетке координат
ax.plot([0.2, 0.4, 0.6], [0.2, 0.8, 0.4])

# Отобразите график
plt.show()
