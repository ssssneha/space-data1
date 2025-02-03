import json
import sys
import math
import csv
import random

from skyfield.api import Loader, EarthSatellite
from skyfield.timelib import Time
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from sgp4.api import Satrec
from sgp4.api import jday

# My modules
import satellite
import satutils
import bot

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
    
def filter_debris_satellites(json_data):
    debris = []
    for sat in json_data:
        if sat.get("OBJECT_TYPE") == "DEBRIS":
            debris.append(sat)
    return debris


def get_xyz(sat):
    satrec = Satrec.twoline2rv(sat["TLE_LINE1"], sat["TLE_LINE2"])
    jd, fr = jday(2019, 1, 1, 11, 59, 33) # I pick an epoch (close to the TLE's)
    e, r, v = satrec.sgp4(jd, fr) # e = error, r = position vector, v = speed vector
    return e, r, v

# Example usage
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python select_nearby.py input_file")
        sys.exit(1)

    input_file = sys.argv[1]

    print(f"Reading from file {input_file}")
    json_data = read_json_file(input_file)
    debris = filter_debris_satellites(json_data)


    n = 0
    for sat in debris:
        n += 1
        e, r, v = get_xyz(sat)
        #print(f"sat {n}: {sat['OBJECT_NAME']} - e: {e}, r: {r}, v: {v}")
        if e == 0:
            # write to file
            with open('debris_data.csv', mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([sat['OBJECT_NAME'], e, r, v])