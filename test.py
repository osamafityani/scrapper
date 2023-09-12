import requests
from scroll import scroll
from bs4 import BeautifulSoup

# Define the URL of the website you want to scrape
url = "https://www.homedepot.com/b/Electrical-Power-Distribution-Fuses/N-5yc1vZbtvm"  # Replace with the actual URL
headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
        }
print(4)
# Make an initial request to get the initial content
response = requests.get(url, headers=headers)
print(5)
response.raise_for_status()
print(0)
# Create a scrollable object and set the scrolling behavior
scrollable = scroll.Scrollable()
scrollable.set_driver(response)

# Scroll down to load more content (you can adjust the number of scrolls)
for _ in range(8):
    scrollable.scroll(1)  # Scroll down by 1 "page"
print(1)
# Get the HTML source after scrolling
updated_html = scrollable.get_updated_html()
print(2)
# Parse the updated HTML with BeautifulSoup
soup = BeautifulSoup(updated_html, 'html.parser')
print(3)
# Extract and process the data from the soup object
data = soup.find_all('div', class_='browse-search__pod col__12-12 col__6-12--xs col__4-12--sm col__3-12--md col__3-12--lg')
print(len(data))

# Close the scrollable object
scrollable.close()
