from django.http import JsonResponse
import time
import requests



GET_DISTRICT_INFO_URL = "https://raw.githubusercontent.com/strativ-dev/technical-screening-test/main/bd-districts.json"
districts = [] 

def get_all_district_information():
    global districts
    districts = requests.get(GET_DISTRICT_INFO_URL).json()["districts"]

def get_districts():
    global districts
    return districts

def custom_response(data = None, message = "Success", status = 200, start_time = None):
    return JsonResponse({
        "success" : True if status == 200 else False,
        "data": data,
        "message": message,
        "elapsed_time": None if start_time is None else f"{(time.time() - start_time)*1000:.2f} ms"
    }, status = status, safe=True)


def get_district_by_name(name):
    global districts
    for district in districts:
        if district["name"] == name:
            return district

    raise ValueError(f"District with name '{name}' not found")

