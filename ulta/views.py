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

        url = f'{domain}/scrap_ulta/categories_urls/'
        response = requests.get(url, timeout=15)

        if response.status_code == 200:
            print("Request successful")
        else:
            print(f"Request failed with status code: {response.status_code}")

    response = HttpResponse()
    response._resource_closers.append(do_after)
    return response


@api_view(['GET'])
def categories_urls(request):
    def do_after():
        sitemap_url = 'https://www.ulta.com/sitemap/p.xml'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
        }

        response = requests.get(sitemap_url, headers=headers)
        sitemap_data = response.text
        sitemap_soup = BeautifulSoup(sitemap_data, 'xml')
        for loc in sitemap_soup.find_all('loc'):
            url = f'{domain}/scrap_ulta/items_pages/'
            requests.post(url, data={'page_url': loc.text}, timeout=15)

    response = HttpResponse()
    response._resource_closers.append(do_after)
    return response


@api_view(['POST'])
def items_pages(request):
    request_data = request.data
    def do_after(data):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
        }

        response = requests.get(data, headers=headers)
        response.raise_for_status()

        data = response.text
        soup = BeautifulSoup(data, 'xml')
        for loc in soup.find_all('loc'):
            if not loc.text.startswith('https://media'):
                url = f'{domain}/scrap_ulta/item_data/'
                requests.post(url, data={'page_url': loc.text}, timeout=15)
                time.sleep(0.5)

    response = HttpResponse()
    response._resource_closers.append(lambda: do_after(request_data['page_url']))
    return response


@api_view(['POST'])
def item_data(request):
    request_data = request.data

    def do_after(data):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
        }

        response = requests.get(data, headers=headers)
        response.raise_for_status()
        link = data

        data = response.text
        soup = BeautifulSoup(data, 'html.parser')

        price = soup.find('span', class_='Text-ds Text-ds--title-6 Text-ds--left Text-ds--black').text

        if price.count('$') == 1:
            price = Decimal(price[1:])
        else:
            price = 0

        try:
            product, created = Product.objects.get_or_create(link=link)
        except:
            try:
                product, created = Product.objects.get_or_create(link=link)
            except:
                print('+++++++++++++++++++++++++++++++++')
        if created:
            product.current_price = price

        else:
            product.last_price = product.current_price
            product.current_price = price

        try:
            product.save()
        except:
            try:
                product.save()
            except:
                print('************************************')

    response = HttpResponse()
    response._resource_closers.append(lambda: do_after(request_data['page_url']))
    return response