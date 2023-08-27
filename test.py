import time
from decimal import Decimal

import requests
from bs4 import BeautifulSoup

headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
        }

response = requests.get('https://www.ulta.com/shop/skin-care/all?page=2', headers=headers)
response.raise_for_status()

data = response.text
soup = BeautifulSoup(data, 'html.parser')

results_wrapped = soup.find('ul', class_='ProductListingResults__productList ProductListingResults__productList--space--top')
if results_wrapped:
    items = results_wrapped.find_all('li', class_='ProductListingResults__productCard')
    for item in items[0:3]:
        link = item.find('a')['href']
        # print(link)
        price = item.find('span', class_='Text-ds--black').text
        print(price)
        # price = Decimal(price)
        # print(price)

        time.sleep(0.5)

print('finish')