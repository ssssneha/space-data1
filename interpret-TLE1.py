import json
import sys
import math
import datetime as dt
from pytz import timezone
from skyfield import almanac
from skyfield.framelib import itrs
from skyfield.api import N, W, wgs84, load, EarthSatellite
from skyfield.positionlib import position_of_radec

def read_json_file(file_path):
    try:
        with open(file_path, 'r') as file:
            json_data = json.load(file)
        return json_data

    except FileNotFoundError:
        print(f"Error: File not found. Please check the file path.")
        return None

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None

def print_TLE(record):
    obj_name = record["OBJECT_NAME"]
    tle_line1 = record["TLE_LINE1"]
    tle_line2 = record["TLE_LINE2"]
    #print(f"{tle_line1}\n{tle_line2}")
    ts = load.timescale()
    t = ts.utc(2023, 1, 3, 12, 45)
    #line1 = '1 25544U 98067A   14020.93268519  .00009878  00000-0  18200-3 0  5082'
    #line2 = '2 25544  51.6498 109.4756 0003572  55.9686 274.8005 15.49815350868473'
    satellite = EarthSatellite(tle_line1, tle_line2, obj_name, ts)

    t = ts.utc(2014, 1, 23, 11, 18, 7)

    geocentric = satellite.at(t)
    lat, lon = wgs84.latlon_of(geocentric)

    bluffton = wgs84.latlon(+40.8939, -83.8917)

    difference = satellite - bluffton
    topocentric = difference.at(t)
    alt, az, distance = topocentric.altaz()


    print(satellite)
    print('Latitude:', lat)
    print('Longitude:', lon)
    print('Altitude: ', alt)



if __name__ == "__main__":
    
    if len(sys.argv) != 2:
        print("Usage: python interpret-TLE1.py input_file")
        sys.exit(1)

    input_file = sys.argv[1]

    print(f"Reading from file {input_file}")
    json_data = read_json_file(input_file)
    # print(json_data)
    print_TLE(json_data[4])