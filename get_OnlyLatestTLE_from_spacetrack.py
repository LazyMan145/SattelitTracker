from datetime import datetime, timedelta
import spacetrack.operators as op
from spacetrack import SpaceTrackClient
from pyorbital.orbital import Orbital
import json
import os

USERNAME = 'YOUR_SPACETRACK_USERNAME'
PASSWORD = 'YOUR_SPACETRACK_PASSWORD'

def get_latest_tle(sat_id, username, password):
    st = SpaceTrackClient(identity=username, password=password)
    try:
        data = st.tle_latest(norad_cat_id=sat_id, orderby='epoch desc', limit=1, format='tle')

        # Log the raw data returned by the API
        print(f"Raw TLE data: {data}")

    except Exception as e:
        print(f"Error fetching data: {e}")
        return None, None

    if not data:
        print("No data received from SpaceTrack.")
        return None, None

    tle_1, tle_2 = data.strip().split('\n')

    return tle_1, tle_2

def get_lat_lon_sgp(tle_1, tle_2, utc_time):
    orb = Orbital("N", line1=tle_1, line2=tle_2)
    lon, lat, alt = orb.get_lonlatalt(utc_time)
    return lon, lat

def save_coordinates_to_file(filename, utc_time, lat, lon):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'a') as file:
        file.write(f"{utc_time} {lat:.6e} {lon:.6e}\n")

def generate_and_save_coordinates(sat_id, start_date, end_date):
    delta = timedelta(minutes=1)
    current_date = start_date


    tle_1, tle_2 = get_latest_tle(sat_id, USERNAME, PASSWORD)

    if not tle_1 or not tle_2:
        print("Failed to fetch TLE data.")
        return

    while current_date <= end_date:
        lon, lat = get_lat_lon_sgp(tle_1, tle_2, current_date)
        save_coordinates_to_file('satellites/coordinates_latest.dat', current_date, lat, lon)
        current_date += delta

satellite_id = 44387
start_date = datetime(2026, 1, 1)
end_date = datetime(2026, 1, 1, 23, 59)

generate_and_save_coordinates(satellite_id, start_date, end_date)