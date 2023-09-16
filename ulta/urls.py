from django.urls import path

from ulta.views import scrap_ulta, categories_urls, item_data, items_pages, scrap_ulta_v1,threaded_requests

urlpatterns = [
     path('scrap_ulta_v1/', scrap_ulta_v1),
     path('scrap_ulta/', scrap_ulta),
     path('scrap_ulta/item_data/', item_data),
     path('thread/', threaded_requests),
]
