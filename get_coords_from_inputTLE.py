from datetime import datetime, timedelta, date
from pyorbital.orbital import Orbital


def checksum(line):

    cksum = 0
    for char in line[:-1]:
        if char.isdigit():
            cksum += int(char)
        elif char == '-':
            cksum += 1
    return cksum % 10


def verify_tle(tle_1, tle_2):

    if int(tle_1[-1]) != checksum(tle_1):
        raise ValueError("Control sum error in line 1")
    if int(tle_2[-1]) != checksum(tle_2):
        raise ValueError("Control sum error in line 2")


def get_lat_lon_sgp(tle_1, tle_2, utc_time):
    orb = Orbital("N", line1=tle_1, line2=tle_2)
    lon, lat, alt = orb.get_lonlatalt(utc_time)
    return lon, lat


def save_coordinates_to_file(filename, utc_time, lat, lon):
    with open(filename, 'a') as file:
        file.write(f"{utc_time} {lat:9.6f} {lon:9.6f}\n")


def generate_and_save_coordinates(tle_1, tle_2, date):

    verify_tle(tle_1, tle_2)

    filename = 'coordinates_blyat.dat'
    delta = timedelta(minutes=1)
    current_time = datetime.combine(date, datetime.min.time())
    end_time = current_time + timedelta(days=1)

    while current_time < end_time:
        lon, lat = get_lat_lon_sgp(tle_1, tle_2, current_time)
        save_coordinates_to_file(filename, current_time, lat, lon)
        current_time += delta



tle_1 = "1 44387U 19038A   24134.50749057  .00000245  00000-0  12652-3 0  9998"
tle_2 = "2 44387  98.8247 103.6000 0002382  74.0416 286.1024 14.23882512252450"



specific_date = date(2023, 1, 1)


generate_and_save_coordinates(tle_1, tle_2, specific_date)


