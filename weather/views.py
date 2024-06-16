from django.shortcuts import render
from django.http import JsonResponse
from http import HTTPStatus
import time
import aiohttp
import asyncio
from django.conf import settings
# import ujson
import requests
from .open_meteo_parser import avg_temp_parser
import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry


# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

cities = []

def custom_response(data = None, message = "Success", status = 200, start_time = None):
    return JsonResponse({
        "success" : True if status == 200 else False,
        "data": data,
        "message": message,
        "elapsed_time": None if start_time is None else f"{(time.time() - start_time)*1000:.2f} ms"
    }, status = status, safe=True)


async def get_all_district_information(request):
    url = "https://raw.githubusercontent.com/strativ-dev/technical-screening-test/main/bd-districts.json"
    async with aiohttp.ClientSession() as session:
        task_fetch_data = session.get(url)
        response = await asyncio.wait_for(task_fetch_data, timeout=settings.REQUEST_TIMEOUT_THRESHOLD)


async def index(request):
    start_time = time.time()  # Record the start time
    response = {}
    url = "https://raw.githubusercontent.com/strativ-dev/technical-screening-test/main/bd-districts.json"
    try:
        response = requests.get(url).json()
        ids, lat, long, names = [], [], [], []

        for district in response["districts"]:
            ids.append(district["id"])
            lat.append(district["lat"])
            long.append(district["long"])   
            names.append(district["name"])

        avg_temps = avg_temp_parser(ids, lat, long, names)
        sorted_avg_temps = sorted(avg_temps, key=lambda x: x[1])

        coolest_ten_districts = sorted_avg_temps[:10]

        serialized_data = []
        for district in coolest_ten_districts:
            serialized_data.append({
                "id": district[0],
                "name": district[2],
                "temperature": f"{district[1]:.2f} °C"
            })  
        
        return custom_response(data = serialized_data, message = HTTPStatus.OK.description, status=HTTPStatus.OK, start_time=start_time)

    except asyncio.TimeoutError:
        return custom_response(data = None, message=HTTPStatus.REQUEST_TIMEOUT.description, status=HTTPStatus.REQUEST_TIMEOUT, start_time=start_time)        
    except Exception as e:
        return custom_response(data = None, message = str(e), status=HTTPStatus.INTERNAL_SERVER_ERROR, start_time=start_time)
