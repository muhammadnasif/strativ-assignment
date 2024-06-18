from django.urls import path
from .views import *
from .utils import get_all_district_information

urlpatterns = [
    path('suggest/', ten_coolest_districts, name='ten_coolest_districts'),
    path('travel-suggestion/', travel_suggestion, name='travel_suggestion')
]

get_all_district_information()