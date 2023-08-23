import requests

# URL you want to send the GET request to
url = 'http://127.0.0.1:8000/categories_urls/'

# Sending the GET request
response = requests.get(url, timeout=15)

# Check the status code of the response
if response.status_code == 200:
    print("Request successful")
    # Print the content of the response
    print(response.text)
else:
    print(f"Request failed with status code: {response.status_code}")
