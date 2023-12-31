import time
from decimal import Decimal

import requests
from ssl import SSLError
from bs4 import BeautifulSoup
from bs4.element import Tag
from django.http import HttpResponse
from requests import ConnectionError

from home_depot.models import Product
from rest_framework.decorators import api_view

domain = 'http://127.0.0.1:8000'
# domain = 'https://scraper-ly28d.ondigitalocean.app'


def get_from_home_depot(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
    }

    url = 'https://www.homedepot.com/sitemap/d/plp_sitemap.xml'
    response = requests.get(url, headers=headers)
    sitemap_data = response.text
    rerequest = True
    while rerequest:
        sitemap_soup = BeautifulSoup(sitemap_data, 'xml')
        rerequest = sitemap_soup.find('div', class_='error__container') != None
    return sitemap_data

@api_view(['GET'])
def scrap_home_depot(request):
    def do_after():
        with open('categories.txt', 'w') as file:
            file.truncate(0)
        # with open('groups_urls.txt', 'w') as file:
        #     file.truncate(0)

        url = f'{domain}/home_depot/groups_urls/'

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
        sitemap_url = 'https://www.homedepot.com/sitemap/d/plp_sitemap.xml'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
        }

        response = requests.get(sitemap_url, headers=headers)
        sitemap_data = response.text
        sitemap_soup = BeautifulSoup(sitemap_data, 'xml')
        # groups_urls = [loc.text for loc in sitemap_soup.find_all('loc')]
        print(sitemap_data)
        # with open('groups_urls.txt', 'w') as file:
        for loc in sitemap_soup.find_all('loc'):
            page_url = loc.text
            url = f'{domain}/home_depot/categories_urls/'
            requests.post(url, data={'page_url': page_url}, timeout=15)
            time.sleep(0.1)

    response = HttpResponse()
    response._resource_closers.append(do_after)
    return response


@api_view(['GET'])
def categories_urls(request):
    request_data = request.data

    def do_after(data):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
        }

        response = requests.get(data, headers=headers)
        data = response.text
        soup = BeautifulSoup(data, 'xml')
        links = soup.find_all('loc')

        with open('categories.txt', 'a') as file:
            for link in links:
                file.write(link.text + '\n')

        # with open('groups_urls.txt', 'r') as file:
        #     first_char = file.read(1)
        #     if not first_char:
        #         url = f'{domain}/home_depot/category_data/'
        #         requests.get(url, timeout=15)
        #     else:
        #         url = f'{domain}/home_depot/categories_urls/'
        #         requests.get(url, timeout=15)


    response = HttpResponse()
    response._resource_closers.append(lambda: do_after(request_data['page_url']))
    return response


@api_view(['GET'])
def category_data(request):
    def do_after():
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
        }

        with open('categories.txt', 'r') as file:
            categories = [line.strip() for line in file]
        categories = list(set(categories))

        skips = []
        count = 0
        for category in categories[:20]:
            with open('categories.txt', 'r') as file:
                lines = file.readlines()[1:]
            with open('categories.txt', 'w') as file:
                file.writelines(lines)

            count += 1
            print(f"Processing stage 2: # {count}/{len(categories)}")
            try:
                if not category.startswith('http'):
                    category = f"https://www.homedepot.com{category}"

                response = requests.get(category, headers=headers)
                response.raise_for_status()

                data = response.text
                soup = BeautifulSoup(data, 'html.parser')

                results_wrapped = soup.find('div', class_='results-wrapped')
                items = results_wrapped.find_all('div', class_='product-pod--ef6xv')

                for item in items:
                    product_Info = {}

                    product_link = item.find('a', class_='product-image')
                    if product_link:
                        product_Info['link'] = 'https://www.homedepot.com' + product_link['href']
                    else:
                        product_Info['link'] = '---'

                    product_price = item.find('div', class_='price')
                    price_div = product_price.find('div', class_='price-format__main-price')
                    spans = price_div.find_all('span')

                    if product_price:
                        if spans[1].get_text() == '¢':
                            product_Info['current_price'] = f'0.{spans[0].get_text()}'
                        else:
                            product_Info['current_price'] = f'{spans[1].get_text()}.{spans[-1].get_text()}'
                    else:
                        product_Info['current_price'] = '---'

                    product, _ = Product.objects.get_or_create(link=product_Info['link'])
                    try:
                        if _:
                            product.current_price = Decimal(product_Info['current_price'])
                        else:
                            product.last_price = product.current_price
                            product.current_price = Decimal(product_Info['current_price'])
                        product.save()
                    except Exception as e:
                        print(e)
                        print(category)
                        print(product_Info)
            except (UnicodeDecodeError, ConnectionError, SSLError):
                skips.append(category)
                print(f"Error processing URL: {category}")
                break
            except requests.exceptions.HTTPError as http_err:
                if http_err.response.status_code == 404:
                    print(f"URL not found: {category}")
                    break
                else:
                    raise

        with open('categories.txt', 'r') as file:
            first_char = file.read(1)
            if not first_char:
                print('finish')
            else:
                url = f'{domain}/home_depot/category_data/'
                requests.get(url, timeout=15)

    response = HttpResponse()
    response._resource_closers.append(do_after)
    return response
