from django.urls import path
from home_depot.views import scrap_home_depot

urlpatterns = [
     path('scrap_home_depot/', scrap_home_depot),
]
