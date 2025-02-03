import json
import sys
import math
import datetime as dt
from pytz import timezone
from skyfield import almanac
from skyfield.framelib import itrs
from skyfield.api import N, W, wgs84, load, EarthSatellite
from skyfield.positionlib import position_of_radec



# open_stream
# loop through json data - for each one get xyz, name, ID, type
# then write out to file and close

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

def get_xyz(sat):
    obj_name = sat["OBJECT_NAME"]
    tle_line1 = sat["TLE_LINE1"]
    tle_line2 = sat["TLE_LINE2"]

    #print(f"{tle_line1}\n{tle_line2}")

    ts = load.timescale()
    t = ts.utc(2023, 1, 3, 12, 45)

    satellite = EarthSatellite(tle_line1, tle_line2, obj_name, ts)

    t = ts.utc(2014, 1, 23, 11, 18, 7)

    pos = satellite.at(t)
    return pos.position.km


# output_loc_csv - json + output
def output_loc_csv(json_data, output_file):
    total_counts = 0
    with open(output_file, 'w') as f:
        for sat in json_data:
            if "OBJECT_TYPE" in sat:
                object_type_value = sat["OBJECT_TYPE"]
                cat_id = sat["OBJECT_ID"]
                pos = get_xyz(sat)
                f.write(f"{cat_id},{object_type_value},{pos[0]},{pos[1]},{pos[2]}\n")
                total_counts += 1
                if (total_counts % 1000 ==0):
                    print(f"{total_counts} records written")
                


# main 
if __name__ == "__main__":
    
    if len(sys.argv) != 3:
        print("Usage: python generate_loc_data.py input_file output_file")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    print(f"Reading from file {input_file}")
    json_data = read_json_file(input_file)

    output_loc_csv(json_data, output_file)