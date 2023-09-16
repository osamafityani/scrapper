import threading
import requests
# from scroll import scroll
from bs4 import BeautifulSoup
import time
import concurrent.futures
from concurrent.futures.thread import ThreadPoolExecutor

# # Define the URL of the website you want to scrape
# url = "https://www.homedepot.com/b/Electrical-Power-Distribution-Fuses/N-5yc1vZbtvm"  # Replace with the actual URL
# headers = {
#             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
#         }
# print(4)
# # Make an initial request to get the initial content
# response = requests.get(url, headers=headers)
# print(5)
# response.raise_for_status()
# print(0)
# # Create a scrollable object and set the scrolling behavior
# scrollable = scroll.Scrollable()
# scrollable.set_driver(response)

# # Scroll down to load more content (you can adjust the number of scrolls)
# for _ in range(8):
#     scrollable.scroll(1)  # Scroll down by 1 "page"
# print(1)
# # Get the HTML source after scrolling
# updated_html = scrollable.get_updated_html()
# print(2)
# # Parse the updated HTML with BeautifulSoup
# soup = BeautifulSoup(updated_html, 'html.parser')
# print(3)
# # Extract and process the data from the soup object
# data = soup.find_all('div', class_='browse-search__pod col__12-12 col__6-12--xs col__4-12--sm col__3-12--md col__3-12--lg')
# print(len(data))

# # Close the scrollable object
# scrollable.close()


def make_request(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
        }
        response = requests.get(url,headers=headers)
        return f"Response from {url}: {response.status_code}\n"
    except Exception as e:
        return f"Error while requesting {url}: {e}\n"

def read_sitemap_urls(sitemap_url):
    headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
        }
    response = requests.get(sitemap_url,headers=headers)
    soup = BeautifulSoup(response.content, 'xml')
    return [loc.text for loc in soup.find_all('loc')]

def threaded_requests():
    start_time = time.time()
    sitemap_url = 'https://www.ulta.com/sitemap/p.xml'
  
    # Step 1: Read URLs from the sitemap
    urls = read_sitemap_urls(sitemap_url)

    # Step 2: Create threads for the first set of URLs
    threads = []
    results = []

    with ThreadPoolExecutor(max_workers=None) as executor: # optimally defined number of threads
        res = [executor.submit(make_request, url) for url in urls]
        concurrent.futures.wait(res)

    results = [future.result() for future in res]


    end_time = time.time()
    elapsed_time = end_time - start_time
    print(elapsed_time)
    return results

print(threaded_requests())



#######################################
import threading
import time
from decimal import Decimal

import requests
from rest_framework.response import Response
from bs4 import BeautifulSoup
from django.http import HttpResponse
from home_depot.models import Product
from rest_framework.decorators import api_view
import concurrent.futures
from concurrent.futures.thread import ThreadPoolExecutor
import time
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


@api_view(['GET'])
def categories_urls(request):
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

    return Response()


@api_view(['GET'])
def items_pages(request):
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

    return Response()


@api_view(['GET'])
def item_data(request):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
    }

    with open('items.txt', 'r') as file:
        link = file.readline().strip()
        lines = file.readlines()
        print(len(lines))

    with open('items.txt', 'w') as file:
        for line in lines:
            file.write(line)

    response = requests.get(link, headers=headers)

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
        print('+++++++++++++++++++++++++++++++++')

    if created:
        product.current_price = price

    else:
        product.last_price = product.current_price
        product.current_price = price

    try:
        product.save()
    except:
        print('************************************')

    return Response()


def make_request(url):
    
    try:
        session = requests.Session()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
        }
        response = session.get(url,headers=headers)
        data = response.text
        soup = BeautifulSoup(data, 'xml')
        with open('items.txt', 'a') as file:
            for loc in soup.find_all('loc'):
                if not loc.text.startswith('https://media'):
                    file.write(loc.text + '\n')
            file.close()
        
        session.close()
        return f"Response from {url}: {response.status_code}\n"
    except Exception as e:
        return f"Error while requesting {url}: {e}\n"


def create_products(url):
    headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
        }
    try:
        session = requests.Session()
        response = session.get(url,headers=headers)
        data = response.text
        soup = BeautifulSoup(data, 'html.parser')

        price = soup.find('span', class_='Text-ds Text-ds--title-6 Text-ds--left Text-ds--black').text

        if price.count('$') == 1:
            price = Decimal(price[1:])
        else:
            price = 0

        try:
            product, created = Product.objects.get_or_create(link=url)
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
            print('**********************************')
        session.close()
        return f"Response from {url}: {response.status_code}\n"
    except Exception as e:
        return f"Error while requesting {url}: {e}\n"

def read_sitemap_urls(sitemap_url):
    headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
        }
    response = requests.get(sitemap_url,headers=headers)
    soup = BeautifulSoup(response.content, 'xml')
    return [loc.text for loc in soup.find_all('loc')]


def read_urls_chunk(file, chunk_size=1000):
    urls = []
    for _ in range(chunk_size):
        line = file.readline()
        if not line:
            break
        urls.append(line.strip())
    return urls


def threaded_requests(request):
    with open('items.txt', 'w') as file:
        file.truncate(0)

    start_time = time.time()
    sitemap_url = 'https://www.ulta.com/sitemap/p.xml'
  
    # Read URLs from the sitemap
    urls = read_sitemap_urls(sitemap_url)

    
    with ThreadPoolExecutor(max_workers=None) as executor: # optimally defined number of threads
        res = [executor.submit(make_request, url) for url in urls]
        concurrent.futures.wait(res)

    with open('items.txt', 'r') as file:
        while True:
            urls_chunk = read_urls_chunk(file)
            if not urls_chunk:
                break

            with ThreadPoolExecutor(max_workers=None) as executor:
                res = [executor.submit(create_products, url) for url in urls_chunk]
                concurrent.futures.wait(res)

    # results = [future.result() for future in res]


    end_time = time.time()
    elapsed_time = end_time - start_time
    # results.insert(0,elapsed_time)
    return HttpResponse(elapsed_time)



# @api_view(['POST'])
# def category_data(request):
#     request_data = request.data

#     def do_after(data):
#         headers = {
#             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
#         }

#         response = requests.get(data, headers=headers)
#         response.raise_for_status()
#         link = data
#         print(link)

#         data = response.text
#         soup = BeautifulSoup(data, 'html.parser')
#         prices = []

#         price = soup.find('span',class_='Text-ds Text-ds--title-6 Text-ds--left Text-ds--black').text
#         print(price)

#         if price.count('$') == 1:
#             price = Decimal(price[1:])
#         else:
#             price = 0

#         product, created = Product.objects.get_or_create(link=link)
#         if created:
#             product.current_price = price
#         else:
#             product.last_price = product.current_price
#             product.current_price = price
#         product.save()

#         prices.clear
#         time.sleep(0.5)

#         print('finish')

#     response = HttpResponse()
#     response._resource_closers.append(lambda: do_after(request_data['page_url']))
#     return response