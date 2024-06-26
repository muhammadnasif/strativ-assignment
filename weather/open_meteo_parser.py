import openmeteo_requests

import requests_cache
import pandas as pd
from retry_requests import retry

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

async def avg_temp_parser(ids : list, lat : list, long : list, names : list) -> dict:
    """
    Fetches average temperature for a specific location based on latitude list and longitude list.

    Parameters:
    lat (list -> float): Latitude of the location.
    long (list -> float): Longitude of the location.

    Returns:
    dict: A dictionary containing average temperature for the specified location.
    """
    params = {
        "latitude": lat,
	    "longitude": long,
        "hourly": "temperature_2m"
    }
    responses = openmeteo.weather_api(OPEN_METEO_URL, params=params)

    location_temps = []
    # Process first location. Add a for-loop for multiple locations or weather models
    id_ctr = 0
    for response in responses:
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
        location_temp = sum(hourly_dataframe["temperature_2m"][13 + (24*i)] for i in range(7))/7
        location_temps.append((ids[id_ctr], location_temp, names[id_ctr]))
        id_ctr += 1
    return location_temps


async def check_temperature_at_2pm(ids : list, lat : list, long : list, names : list, date) -> dict:
    """
    Fetches temperature at 2PM for a specific location based on latitude list and longitude list.

    Parameters:
    ids (list -> int): ID of the location.
    lat (list -> float): Latitude of the location.
    long (list -> float): Longitude of the location.
    names (list -> str): Name of the location.
    date (str): Date for which the temperature at 2PM is to be fetched.

    Returns:
    dict: A dictionary containing average temperature for the specified location.
    """
    params = {
        "latitude": lat,
	    "longitude": long,
        "hourly": "temperature_2m",
        "start_date": date,
	    "end_date": date
    }
    responses = openmeteo.weather_api(OPEN_METEO_URL, params=params)

    location_temps = []
    id_ctr = 0
    for response in responses:
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

        # temperature at 2PM is at hourly_dataframe["temperature_2m"][14]. Here 14 is the index of 2PM in the hourly data
        location_temps.append((ids[id_ctr], hourly_dataframe["temperature_2m"][14], names[id_ctr]))
        id_ctr += 1

    return location_temps


