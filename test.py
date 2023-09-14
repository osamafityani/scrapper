@api_view(['POST'])
def category_data(request):
    request_data = request.data

    def do_after(data):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
        }

        response = requests.get(data, headers=headers)
        response.raise_for_status()
        link = data
        print(link)

        data = response.text
        soup = BeautifulSoup(data, 'html.parser')
        prices = []

        price = soup.find('span',class_='Text-ds Text-ds--title-6 Text-ds--left Text-ds--black').text
        print(price)

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

        prices.clear
        time.sleep(0.5)

        print('finish')

    response = HttpResponse()
    response._resource_closers.append(lambda: do_after(request_data['page_url']))
    return response