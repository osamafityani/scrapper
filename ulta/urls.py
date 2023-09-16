from django.urls import path

from ulta.views import scrap_ulta, categories_urls, item_data, items_pages, scrap_ulta_v1, threaded_requests, \
     get_items_file, get_errors_file, get_groups_file, thread_items

urlpatterns = [
     path('scrap_ulta_v1/', scrap_ulta_v1),
     path('scrap_ulta/', scrap_ulta),
     path('scrap_ulta/item_data/', item_data),
     path('thread_items/',thread_items),
     path('get_items_file/', get_items_file),
     path('get_errors_file/', get_errors_file),
     path('get_groups_file/', get_groups_file),
]
