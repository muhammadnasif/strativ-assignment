from django.shortcuts import render
from django.http import JsonResponse
from http import HTTPStatus
import time
import aiohttp
import asyncio
from django.conf import settings
# import ujson
import requests
from .open_meteo_parser import open_meteo_parser
import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry


# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

cities = []

def openmeto_request(lat, long, start_date, end_date):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": long,
        "hourly": "temperature_2m",
        "timezone": "auto",
        "start_date": start_date,   # "2024-06-16",
        "end_date": end_date        # "2024-06-16"
    }
    responses = openmeteo.weather_api(url, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]
    print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
    print(f"Elevation {response.Elevation()} m asl")
    print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
    print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

    # Process hourly data. The order of variables needs to be the same as requested.
    hourly = response.Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()

    hourly_data = {"date": pd.date_range(
        start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
        end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = hourly.Interval()),
        inclusive = "left"
    )}
    hourly_data["temperature_2m"] = hourly_temperature_2m

    hourly_dataframe = pd.DataFrame(data = hourly_data)



def custom_response(data = None, message = "Success", status = 200):
    return JsonResponse({
        "success" : True if status == 200 else False,
        "data": data,
        "message": message
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

        # have to fetch it from the district list
        current_location_information = response["districts"][0]
        destination_location_information = response["districts"][1]

        current_corrdinates = current_location_information["lat"], current_location_information["long"]
        destination_corrdinates = destination_location_information["lat"], destination_location_information["long"]


        # async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
        #     task_fetch_data = session.get(url)
        #     response = await asyncio.wait_for(task_fetch_data, timeout=settings.REQUEST_TIMEOUT_THRESHOLD)

        elapsed_time = time.time() - start_time
        # response["elapsed_time"] = f"{elapsed_time*1000:.2f} ms"    
        if elapsed_time > settings.REQUEST_TIMEOUT_THRESHOLD:  # 500 ms threshold
            return custom_response(response, HTTPStatus.REQUEST_TIMEOUT.description, status=HTTPStatus.REQUEST_TIMEOUT)
        
        return custom_response(response, HTTPStatus.OK.description, status=HTTPStatus.OK)

    except asyncio.TimeoutError:
        return custom_response(None, HTTPStatus.REQUEST_TIMEOUT.description, status=HTTPStatus.REQUEST_TIMEOUT)        
    except Exception as e:
        return custom_response(None, str(e), status=HTTPStatus.INTERNAL_SERVER_ERROR)
