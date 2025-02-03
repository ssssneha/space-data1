import json
import csv
import sys
import math


from skyfield.api import Loader, EarthSatellite
from skyfield.timelib import Time

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

def write_tle_to_csv(tle_data, output_csv="tle_data.csv"):
    # Define CSV column headers
    csv_header = ["OBJECT_NAME", "TLE_LINE1", "TLE_LINE1"]

    # Open file and write data
    with open(output_csv, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(csv_header)  # Write headers
        
        for tle in tle_data:
            name = tle.get("OBJECT_NAME", "")
            line1 = tle.get("TLE_LINE1", "")
            line2 = tle.get("TLE_LINE2", "")
            writer.writerow([name, line1, line2])  # Write TLE data
    
    print(f"TLE data successfully written to {output_csv}")

if __name__ == "__main__":
    
    if len(sys.argv) != 2:
        print("Usage: python json-csv-data.py input_file")
        sys.exit(1)

    input_file = sys.argv[1]

    print(f"Reading from file {input_file}")
    json_data = read_json_file(input_file)

    for sat in json_data:
        debris = filter_debris_satellites(json_data)

    write_tle_to_csv(debris)
