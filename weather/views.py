from django.shortcuts import render
from django.http import JsonResponse
from http import HTTPStatus
import time
import json
import asyncio
from django.conf import settings
import requests
from .open_meteo_parser import avg_temp_parser, check_temperature_at_2pm
from django.views.decorators.csrf import csrf_exempt


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


async def calculate_coolest_ten():

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


async def get_ten_coolest_districts(request):
    start_time = time.time()  # Record the start time
    try:
        data = await asyncio.wait_for(calculate_coolest_ten(), timeout=settings.REQUEST_TIMEOUT_THRESHOLD)
        return custom_response(data = data, message = HTTPStatus.OK.description, status=HTTPStatus.OK, start_time=start_time)
    except asyncio.TimeoutError:
        return custom_response(data = None, message=HTTPStatus.REQUEST_TIMEOUT.description, status=HTTPStatus.REQUEST_TIMEOUT, start_time=start_time)        
    except Exception as e:
        return custom_response(data = None, message = str(e), status=HTTPStatus.INTERNAL_SERVER_ERROR, start_time=start_time)


def get_district_by_name(name):
    global districts
    for district in districts:
        if district["name"] == name:
            return district
    return None


async def calculate_travel_suggestion(request):
    request_data = json.loads(request.body)
    date = request_data.get("date")

    from_district = get_district_by_name(request_data.get("from"))
    to_district = get_district_by_name(request_data.get("to"))

    ids = [from_district["id"], to_district["id"]]
    long = [from_district["long"], to_district["long"]]
    lat = [from_district["lat"], to_district["lat"]]
    names = [from_district["name"], to_district["name"]]

    temps = await check_temperature_at_2pm(ids, lat, long, names, date=date)
    
    from_temp = temps[0][1]
    to_temp = temps[1][1]

    result = {}
    result["from"] = from_district
    result["to"] = to_district
    result["from"]["temperature"] = f"{from_temp}"
    result["to"]["temperature"] = f"{to_temp}"

    result["suggestion"] = ""

    if to_temp < from_temp:
        result["suggestion"] = "It's cooler at your destination. Enjoy your trip!"
    else:
        result["suggestion"] = "It's cooler at your place. You should until the temperature drops at your destination."

    return result

@csrf_exempt
async def travel_suggestion(request):
    start_time = time.time()
    try:
        data = await asyncio.wait_for(calculate_travel_suggestion(request=request), timeout=settings.REQUEST_TIMEOUT_THRESHOLD)
        return custom_response(data = data, message = HTTPStatus.OK.description, status=HTTPStatus.OK, start_time=start_time)
    except asyncio.TimeoutError:
        return custom_response(data = None, message=HTTPStatus.REQUEST_TIMEOUT.description, status=HTTPStatus.REQUEST_TIMEOUT, start_time=start_time)        
    except Exception as e:
        return custom_response(data = None, message = str(e), status=HTTPStatus.INTERNAL_SERVER_ERROR, start_time=start_time)
