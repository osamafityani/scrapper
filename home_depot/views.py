import requests
from ssl import SSLError
from bs4 import BeautifulSoup
from bs4.element import Tag
from requests import ConnectionError

from home_depot.models import Product
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET'])
def scrap_home_depot(request):
    sitemap_url = 'https://www.homedepot.com/sitemap/d/plp_sitemap.xml'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
    }

    response = requests.get(sitemap_url, headers=headers)
    sitemap_data = response.text
    sitemap_soup = BeautifulSoup(sitemap_data, 'xml')

    groups_urls = [loc.text for loc in sitemap_soup.find_all('loc')]

    categories = []
    count = 0
    for url in groups_urls[:5]:
        count += 1
        print(f"Processing stage 1: # {count}/{len(groups_urls)}")
        response = requests.get(url, headers=headers)
        data = response.text
        soup = BeautifulSoup(data, 'xml')
        links = soup.find_all('loc')
        categories += [link.text for link in links]
    categories = list(set(categories))

    skips = []
    count = 0
    for category in categories[:5]:
        count += 1
        print(f"Processing stage 2: # {count}/{len(categories)}")
        print(category)
        try:
            if isinstance(category, Tag):
                category = f"https://www.homedepot.com{category['href']}"
            elif not category.startswith('http'):
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
                    print(product_Info['current_price'])
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

    return Response("Scraping completed")
