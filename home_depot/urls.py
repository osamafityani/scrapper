from django.urls import path
from home_depot.views import scrap_home_depot, groups_urls, categories_urls, category_data

urlpatterns = [
     path('scrap_home_depot/', scrap_home_depot),
     path('home_depot/groups_urls/', groups_urls),
     path('home_depot/categories_urls/', categories_urls),
     path('home_depot/category_data/', category_data),
]
