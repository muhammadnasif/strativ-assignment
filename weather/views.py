from django.shortcuts import render
from django.http import JsonResponse
from http import HTTPStatus
import time
import aiohttp
import asyncio
from django.conf import settings
import requests
from .open_meteo_parser import avg_temp_parser

GET_DISTRICT_INFO_URL = "https://raw.githubusercontent.com/strativ-dev/technical-screening-test/main/bd-districts.json"
districts = [] 

def get_all_district_information():
    global districts
    districts = requests.get(GET_DISTRICT_INFO_URL).json()["districts"]
    print("Districts loaded successfully")


def custom_response(data = None, message = "Success", status = 200, start_time = None):
    return JsonResponse({
        "success" : True if status == 200 else False,
        "data": data,
        "message": message,
        "elapsed_time": None if start_time is None else f"{(time.time() - start_time)*1000:.2f} ms"
    }, status = status, safe=True)


# ---------------- USE AWAIT FOR TO HANDLE TIMEOUT ----------------
async def calculate_coolest_ten():

    time.sleep(2)  # Simulate a blocking operation

    ids, lat, long, names = [], [], [], []

    global districts

    ids = [district["id"] for district in districts]
    lat = [district["lat"] for district in districts]
    long = [district["long"] for district in districts]
    names = [district["name"] for district in districts]

    avg_temps = await avg_temp_parser(ids, lat, long, names)
    sorted_avg_temps = sorted(avg_temps, key=lambda x: x[1])

    coolest_ten_districts = sorted_avg_temps[:10]

    serialized_data = []
    for district in coolest_ten_districts:
        serialized_data.append({
        "id": district[0],
        "name": district[2],
        "temperature": f"{district[1]:.2f} °C"
        })  
    
    return serialized_data

async def index(request):
    start_time = time.time()  # Record the start time
    try:
        data = await asyncio.wait_for(calculate_coolest_ten(), timeout=0.001)
        return custom_response(data = data, message = HTTPStatus.OK.description, status=HTTPStatus.OK, start_time=start_time)

    except TimeoutError:
        return custom_response(data = None, message=HTTPStatus.REQUEST_TIMEOUT.description, status=HTTPStatus.REQUEST_TIMEOUT, start_time=start_time)        
    except Exception as e:
        return custom_response(data = None, message = str(e), status=HTTPStatus.INTERNAL_SERVER_ERROR, start_time=start_time)
