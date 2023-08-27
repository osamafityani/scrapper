from django.urls import path

from ulta.views import scrap_ulta, groups_urls, category_data, category_pages

urlpatterns = [
     path('scrap_ulta/', scrap_ulta),
     path('scrap_ulta/groups_urls/', groups_urls),
     path('scrap_ulta/category_pages/', category_pages),
     path('scrap_ulta/category_data/', category_data),
]
