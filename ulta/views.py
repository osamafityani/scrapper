from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
import time
from decimal import Decimal

import requests
from bs4 import BeautifulSoup
from django.http import HttpResponse
from rest_framework.response import Response

from home_depot.models import Product
from rest_framework.decorators import api_view

# domain = 'http://127.0.0.1:8000'
domain = 'https://scraper-27hwb.ondigitalocean.app'


@api_view(['GET'])
def scrap_ulta_v1(request):
    def do_after():
        with open('categories.txt', 'w') as file:
            file.truncate(0)
        with open('groups_urls.txt', 'w') as file:
            file.truncate(0)

        sitemap_url = 'https://www.ulta.com/sitemap/p.xml'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
        }

        response = requests.get(sitemap_url, headers=headers)
        sitemap_data = response.text
        sitemap_soup = BeautifulSoup(sitemap_data, 'xml')
        for loc in sitemap_soup.find_all('loc'):
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
            }

            response = requests.get(loc.text, headers=headers)
            response.raise_for_status()

            _data = response.text
            soup = BeautifulSoup(_data, 'xml')
            for loc_ in soup.find_all('loc'):
                if not loc_.text.startswith('https://media'):
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
                    }

                    response = requests.get(loc_.text, headers=headers)
                    response.raise_for_status()
                    link = loc_.text

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

        if response.status_code == 200:
            print("Request successful")
        else:
            print(f"Request failed with status code: {response.status_code}")

    response = HttpResponse()
    response._resource_closers.append(do_after)
    return response


@api_view(['GET'])
def scrap_ulta(request):
    with open('items.txt', 'r') as file:
        for line in file:
            return Response(True)

    return Response(False)


def categories_urls():
    with open('groups_urls.txt', 'w') as file:
        file.truncate(0)

    sitemap_url = 'https://www.ulta.com/sitemap/p.xml'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
    }

    response = requests.get(sitemap_url, headers=headers)
    sitemap_data = response.text
    sitemap_soup = BeautifulSoup(sitemap_data, 'xml')

    with open('groups_urls.txt', 'a') as file:
        for loc in sitemap_soup.find_all('loc'):
            file.write(loc.text + '\n')
    file.close()

    # url = f'{domain}/scrap_ulta/items_pages/'
    # requests.post(url, data={'page_url': loc.text})

    return


def items_pages():
    with open('items.txt', 'w') as file:
        file.truncate(0)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
    }

    with open('groups_urls.txt', 'r') as file:
        for line in file:
            response = requests.get(line.strip(), headers=headers)
            response.raise_for_status()

            data = response.text
            soup = BeautifulSoup(data, 'xml')

            with open('items.txt', 'a') as file:
                for loc in soup.find_all('loc'):
                    if not loc.text.startswith('https://media'):
                        file.write(loc.text + '\n')
            file.close()

    return


@api_view(['GET'])
def item_data(request):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
    }

    with open('items.txt', 'r') as file:
        link = file.readline().strip()
        lines = file.readlines()
        print(len(lines))
    file.close()

    if len(lines) == 0 or link == '':
        categories_urls()
        items_pages()
    else:
        with open('items.txt', 'w') as file:
            for line in lines:
                file.write(line)
        file.close()
    try:
        response = requests.get(link, headers=headers)

        data = response.text
        soup = BeautifulSoup(data, 'html.parser')

        try:
            price = soup.find('span', class_='Text-ds Text-ds--title-6 Text-ds--left Text-ds--black').text 
        except Exception as e:
            price = soup.find('span', class_='Text-ds Text-ds--title-6 Text-ds--left Text-ds--magenta-500').text 


        if price.count('$') == 1:
            price = Decimal(price[1:])
        else:
            price = 0

        product, created = Product.objects.get_or_create(link=link)

        if created:
            product.current_price = price

        else:
            product.last_price = product.current_price
            product.current_price = price

        product.save()

    except:
        with open('errors.txt', 'a') as file:
            file.write(link + '\n')
        file.close()

    return Response()


@api_view(['GET'])
def get_items_file(request):
    with open('items.txt', 'r') as file:
        response = HttpResponse(file, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=items.txt'
        return response


@api_view(['GET'])
def get_errors_file(request):
    with open('errors.txt', 'r') as file:
        response = HttpResponse(file, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=errors.txt'
        return response


@api_view(['GET'])
def get_groups_file(request):
    with open('groups_urls.txt', 'r') as file:
        response = HttpResponse(file, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=groups_urls.txt'
        return response


def make_request(url):
    
    try:
        print("#########################################")
        session = requests.Session()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
        }
        response = session.get(url,headers=headers)
        data = response.text
        soup = BeautifulSoup(data, 'xml')
        with open('threaded_items.txt', 'a') as file:
            for loc in soup.find_all('loc'):
                if not loc.text.startswith('https://media'):
                    file.write(loc.text + '\n')
            file.close()
        print("&&&&&&&&&&&&&&&&&&&&&&&&")
        session.close()
        return f"Response from {url}: {response.status_code}\n"
    except Exception as e:
        return f"Error while requesting {url}: {e}\n"


def create_products(url):
    headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
        }
    try:
        print("---------------------- requesting item info")
        response = requests.get(url,headers=headers)

        data = response.text
        soup = BeautifulSoup(data, 'html.parser')

        try:
            price = soup.find('span', class_='Text-ds Text-ds--title-6 Text-ds--left Text-ds--black').text 
        except Exception as e:
            price = soup.find('span', class_='Text-ds Text-ds--title-6 Text-ds--left Text-ds--magenta-500').text 


        if price.count('$') == 1:
            price = Decimal(price[1:])
        else:
            price = 0

        product, created = Product.objects.get_or_create(link=url)

        if created:
            product.current_price = price

        else:
            product.last_price = product.current_price
            product.current_price = price

        product.save()

    except:
        with open('errors.txt', 'a') as file:
            file.write(url + '\n')
        file.close()

@api_view(['GET'])
def thread_items(request):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
    }

    with open('items.txt', 'r') as file:
        urls = []
        lines = file.readlines()
        if len(lines) < 10:
            r = len(lines)
        else: r = 10

        for i in range(r):
            urls.append(file.readline().strip())
        lines = file.readlines()
        print(len(lines))
        if len(lines) == 0:
            check = True
        else: check=False
    file.close()
    print('********* - before checking if items empty')
    if check:
        print('+++++++++++++ - getting items')
        categories_urls()
        items_pages()
    else:
        print('&&&&&&&& - writing lines')
        with open('items.txt', 'w') as file:
            for line in lines:
                file.write(line)
        file.close()
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        res = [executor.submit(create_products, url) for url in urls]
        concurrent.futures.wait(res)
    print('@@@@@@@@@@ - Item Done')
    return Response()

def read_sitemap_urls(sitemap_url):
    headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
        }
    print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
    response = requests.get(sitemap_url,headers=headers)
    soup = BeautifulSoup(response.content, 'xml')
    return [loc.text for loc in soup.find_all('loc')]


def read_urls_chunk(file, chunk_size=10):
    urls = []
    for _ in range(chunk_size):
        link = file.readline().strip()
        urls.append(link)
    
    lines = file.readlines()
    print(len(lines))
    with open('items.txt', 'w') as file:
        for line in lines:
            file.write(line)
        
    return urls


def threaded_requests(request):

    with open('items.txt', 'r') as file:
        print('!!!!!!!!!!!!!!!!!!!!!!!!!')
        urls_chunk = read_urls_chunk(file)
        with ThreadPoolExecutor(max_workers=None) as executor:
            res = [executor.submit(create_products, url) for url in urls_chunk]
            concurrent.futures.wait(res)

    return HttpResponse()


