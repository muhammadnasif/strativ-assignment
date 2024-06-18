from django.urls import path
from .views import *

urlpatterns = [
    path('suggest/', get_ten_coolest_districts, name='get_ten_coolest_districts'),
    path('travel-suggestion/', travel_suggestion, name='travel_suggestion')
]

get_all_district_information()