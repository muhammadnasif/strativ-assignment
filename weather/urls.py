from django.urls import path
from .views import *

urlpatterns = [
    path('suggest/', index, name='index')
]

get_all_district_information()