from django.urls import path

from ulta.views import scrap_ulta, categories_urls, item_data, items_pages, scrap_ulta_v1

urlpatterns = [
     path('scrap_ulta_v1/', scrap_ulta_v1),
     path('scrap_ulta/', scrap_ulta),
     path('scrap_ulta/categories_urls/', categories_urls),
     path('scrap_ulta/items_pages/', items_pages),
     path('scrap_ulta/item_data/', item_data),
]
