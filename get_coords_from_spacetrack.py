from datetime import datetime, timedelta
import spacetrack.operators as op
from spacetrack import SpaceTrackClient
from pyorbital.orbital import Orbital
import json
import os

USERNAME = 'YOUR_SPACETRACK_USERNAME'
PASSWORD = 'YOUR_SPACETRACK_PASSWORD'
CACHE_DIR = 'tle_cache'


def get_cached_tle(sat_id, date):
    cache_file = os.path.join(CACHE_DIR, f'{sat_id}_{date.strftime("%Y-%m-%d")}.tle')
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as file:
            tle_data = file.read().strip().split('\n')
            if len(tle_data) == 2:
                return tle_data[0], tle_data[1]
    return None, None


def cache_tle_data(sat_id, date, tle_1, tle_2):
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_file = os.path.join(CACHE_DIR, f'{sat_id}_{date.strftime("%Y-%m-%d")}.tle')
    with open(cache_file, 'w') as file:
        file.write(f"{tle_1}\n{tle_2}")


def get_tle_for_date_range(sat_id, start_date, end_date, username, password):
    st = SpaceTrackClient(identity=username, password=password)
    tle_data = []
    current_date = start_date

    while current_date <= end_date:
        cached_tle = get_cached_tle(sat_id, current_date)
        if cached_tle[0] and cached_tle[1]:
            tle_data.append((current_date, cached_tle[0], cached_tle[1]))
        else:
            try:
                data = st.tle(norad_cat_id=sat_id, orderby='epoch desc', format='tle', epoch=op.inclusive_range(current_date, current_date + timedelta(days=1)))
                tle_lines = [line for line in data.strip().split('\n') if line]
                if len(tle_lines) >= 2 and len(tle_lines) % 2 == 0:
                    for i in range(0, len(tle_lines), 2):
                        tle_1, tle_2 = tle_lines[i], tle_lines[i + 1]
                        cache_tle_data(sat_id, current_date, tle_1, tle_2)
                        tle_data.append((current_date, tle_1, tle_2))
                else:
                    print(f"Error: Expected TLE data in pairs, but got {len(tle_lines)} lines for date {current_date}")
            except Exception as e:
                print(f"Error fetching data for date {current_date}: {e}")

        current_date += timedelta(days=1)

    return tle_data


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


    try:
        st = SpaceTrackClient(identity=USERNAME, password=PASSWORD)
        test_data = st.tle(norad_cat_id=sat_id, orderby='epoch desc', format='tle', epoch=op.inclusive_range(start_date, start_date+timedelta(days=1)))
        print("Test data fetched successfully")
    except Exception as e:
        print(f"Test request error: {e}")


    tle_data = get_tle_for_date_range(sat_id, start_date, end_date, USERNAME, PASSWORD)

    if not tle_data:
        print("Failed to fetch TLE data.")
        return

    while current_date <= end_date:
        for tle_date, tle_1, tle_2 in tle_data:
            if current_date.date() == tle_date.date():
                lon, lat = get_lat_lon_sgp(tle_1, tle_2, current_date)
                save_coordinates_to_file(f'satellites/SAT-{satellite_id}.dat', current_date, lat, lon)
        current_date += delta


satellite_id = 59661
start_date = datetime(2024, 10, 6)
end_date = datetime(2024, 10, 7)

generate_and_save_coordinates(satellite_id, start_date, end_date)
