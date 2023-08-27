import math
import time
from decimal import Decimal

import requests
from bs4 import BeautifulSoup
from django.http import HttpResponse
from home_depot.models import Product
from rest_framework.decorators import api_view

domain = 'http://127.0.0.1:8000'
# domain = 'https://scraper-ly28d.ondigitalocean.app'


@api_view(['GET'])
def scrap_ulta(request):
    def do_after():
        with open('categories.txt', 'w') as file:
            file.truncate(0)
        with open('groups_urls.txt', 'w') as file:
            file.truncate(0)

        url = f'{domain}/scrap_ulta/groups_urls/'
        response = requests.get(url, timeout=15)

        if response.status_code == 200:
            print("Request successful")
        else:
            print(f"Request failed with status code: {response.status_code}")

    response = HttpResponse()
    response._resource_closers.append(do_after)
    return response


@api_view(['GET'])
def groups_urls(request):
    def do_after():
        sitemap_url = 'https://www.ulta.com/sitemap/shop.xml'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
        }

        response = requests.get(sitemap_url, headers=headers)
        sitemap_data = response.text
        sitemap_soup = BeautifulSoup(sitemap_data, 'xml')

        with open('groups_urls.txt', 'w') as file:
            for loc in sitemap_soup.find_all('loc'):
                if loc.text.endswith('all'):
                    file.write(loc.text + '\n')

        url = f'{domain}/scrap_ulta/category_pages/'
        requests.get(url, timeout=15)

    response = HttpResponse()
    response._resource_closers.append(do_after)
    return response


@api_view(['GET'])
def category_pages(request):
    def do_after():
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
        }

        with open('groups_urls.txt', 'r') as file:
            categories = [line.strip() for line in file]
        categories = list(set(categories))

        count = 0
        for category in categories[:1]:
            count += 1
            with open('groups_urls.txt', 'r') as file:
                lines = file.readlines()[1:]
            with open('groups_urls.txt', 'w') as file:
                file.writelines(lines)
            file.close()

            response = requests.get(category, headers=headers)
            response.raise_for_status()

            data = response.text
            soup = BeautifulSoup(data, 'html.parser')

            items_num = int(soup.find('h2', class_='Text-ds Text-ds--title-6 Text-ds--left').text.split(' ')[0])
            for page in range(math.ceil(items_num / 96) + 1):
                page_url = f'{category}?page={page}'

                url = f'{domain}/scrap_ulta/category_data/'
                requests.post(url, data={'page_url': page_url}, timeout=15)
                time.sleep(2)

        with open('groups_urls.txt', 'r') as file:
            first_char = file.read(1)
            if not first_char:
                pass
            else:
                url = f'{domain}/scrap_ulta/category_pages/'
                requests.get(url, timeout=15)
                time.sleep(2)

    response = HttpResponse()
    response._resource_closers.append(do_after)
    return response


@api_view(['POST'])
def category_data(request):
    request_data = request.data

    def do_after(data):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
        }

        response = requests.get(data, headers=headers)
        response.raise_for_status()

        data = response.text
        soup = BeautifulSoup(data, 'html.parser')

        results_wrapped = soup.find('ul', class_='ProductListingResults__productList ProductListingResults__productList--space--top')
        if results_wrapped:
            items = results_wrapped.find_all('li', class_='ProductListingResults__productCard')
            for item in items:
                link = item.find('a')['href']
                price = item.find('span', class_='Text-ds--black').text
                if price.count('$') == 1:
                    price = Decimal(price[1:])
                elif price.count('$') == 2:
                    prices = price.split(' - ')
                    price = prices[0][1:]
                else:
                    price = 0

                product, _ = Product.objects.get_or_create(link=link)
                if _:
                    product.current_price = price
                else:
                    product.last_price = product.current_price
                    product.current_price = price
                product.save()

                time.sleep(0.5)

        print('finish')

    response = HttpResponse()
    response._resource_closers.append(lambda: do_after(request_data['page_url']))
    return response
