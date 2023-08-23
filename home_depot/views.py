import requests
from ssl import SSLError
from bs4 import BeautifulSoup
from bs4.element import Tag
from django.http import HttpResponse
from requests import ConnectionError

from home_depot.models import Product
from rest_framework.decorators import api_view


@api_view(['GET'])
def scrap_home_depot(request):
    def do_after():
        with open('categories.txt', 'w') as file:
            file.truncate(0)
        with open('groups_urls.txt', 'w') as file:
            file.truncate(0)

        url = 'https://scraper-ly28d.ondigitalocean.app/groups_urls/'

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

        with open('groups_urls.txt', 'w') as file:
            for loc in sitemap_soup.find_all('loc'):
                file.write(loc.text + '\n')

        url = 'https://scraper-ly28d.ondigitalocean.app/categories_urls/'
        requests.get(url, timeout=15)

    response = HttpResponse()
    response._resource_closers.append(do_after)
    return response


@api_view(['GET'])
def categories_urls(request):

    def do_after():
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
        }

        with open('groups_urls.txt', 'r') as file:
            groups_urls = [line.strip() for line in file]

        count = 0
        for url in groups_urls[:5]:
            with open('groups_urls.txt', 'r') as file:
                lines = file.readlines()[1:]
            with open('groups_urls.txt', 'w') as file:
                file.writelines(lines)

            count += 1
            print(f"Processing stage 1: # {count}/{len(groups_urls)}")
            response = requests.get(url, headers=headers)
            data = response.text
            soup = BeautifulSoup(data, 'xml')
            links = soup.find_all('loc')

            with open('categories.txt', 'w') as file:
                for link in links:
                    file.write(link.text + '\n')

        with open('groups_urls.txt', 'r') as file:
            first_char = file.read(1)
            if not first_char:
                url = 'https://scraper-ly28d.ondigitalocean.app/category_data/'
                requests.get(url, timeout=15)
            else:
                url = 'https://scraper-ly28d.ondigitalocean.app/categories_urls/'
                requests.get(url, timeout=15)


    response = HttpResponse()
    response._resource_closers.append(do_after)
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
        for category in categories[:5]:
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
                        product_Info['current_price'] = f'{spans[1].get_text()}.{spans[-1].get_text()}'
                    else:
                        product_Info['current_price'] = '---'

                    product, _ = Product.objects.get_or_create(link=product_Info['link'])
                    if _:
                        product.last_price = product.current_price
                        if product_Info['current_price'].startswith('$'):
                            product.current_price = float(product_Info['current_price'][1:])
                        elif product_Info['current_price'].endswith('¢'):
                            product.current_price = float(product_Info['current_price'][:-1])
                        else:
                            print(product_Info['current_price'])
                    else:
                        if product_Info['current_price'].startswith('$'):
                            product.current_price = float(product_Info['current_price'][1:])
                        elif product_Info['current_price'].endswith('¢'):
                            product.current_price = float(product_Info['current_price'][:-1])
                        else:
                            print(product_Info['current_price'])
                    product.save()

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
                url = 'https://scraper-ly28d.ondigitalocean.app/category_data/'
                requests.get(url, timeout=15)

    response = HttpResponse()
    response._resource_closers.append(do_after)
    return response
