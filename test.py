import requests
from bs4 import BeautifulSoup


sitemap_url = 'https://www.ulta.com/sitemap/shop.xml'

# HEADERS = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0",
#     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
#     "Accept-Language": "en-US,en;q=0.5",
#     "Accept-Encoding": "gzip, deflate",
#     "Connection": "keep-alive",
#     "Upgrade-Insecure-Requests": "1",
#     "Sec-Fetch-Dest": "document",
#     "Sec-Fetch-Mode": "navigate",
#     "Sec-Fetch-Site": "none",
#     "Sec-Fetch-User": "?1",
#     "Cache-Control": "max-age=0",
# }

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"
}

response = requests.get(sitemap_url, headers=headers)
sitemap_data = response.text
print(sitemap_data)

# sitemap_soup = BeautifulSoup(sitemap_data, 'xml')
#
# groups_urls = [loc.text for loc in sitemap_soup.find_all('loc')]
# print(groups_urls)
# categories = []
#
# count = 0
# for url in groups_urls[:3]:
#     print(url)
#     count += 1
#     print(f"Processing stage 1: # {count}/{len(groups_urls)}")
#     response = requests.get(url, headers=HEADERS)
#     data = response.text
#     soup = BeautifulSoup(data, 'xml')
#     links = soup.select('url > loc')
#     categories += [link.text for link in links]
# categories = list(set(categories))
# skips = []
# count = 0
# print('======================================')
# for category in categories[:1]:
#
#     count += 1
#     print(f"Processing stage 2: # {count}/{len(categories)}")
#
#     try:
#         if isinstance(category, Tag):
#             category = f"https://www.lowes.com{category['href']}"
#         elif not category.startswith('http'):
#             category = f"https://www.lowes.com{category}"
#
#         print(category)
#
#         response = requests.get(category, headers=HEADERS)
#         response.raise_for_status()
#         data = response.text
#         print(data)
#         soup = BeautifulSoup(data, 'html.parser')
#
#         app = soup.find_all('div', id='app')
#         # items = results_wrapped.find_all('div', class_='product-pod--ef6xv')
#         print(app)
#         # TODO: 2- navigate to price
#
#         # for item in items:
#         #     product_Info = {}
#         #     print(item.get_text())
#         #     print('i')
#
#     except (UnicodeDecodeError, ConnectionError, SSLError):
#         skips.append(category)
#         print(f"Error processing URL: {category}")
#         break
#     except requests.exceptions.HTTPError as http_err:
#         if http_err.response.status_code == 404:
#             print(f"URL not found: {category}")
#             break
#         else:
#             raise