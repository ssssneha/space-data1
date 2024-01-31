import csv
import math

# My modules
import satellite

def get_sat_data(file_path):
    try:
        sat_data = []
        with open(file_path, 'r') as file:
            csv_reader = csv.reader(file)
            next(csv_reader, None)
            for lines in csv_reader:
                sat = satellite.Satellite()
                sat.import_line(lines)
                sat_data.append(sat)
        return sat_data

    except FileNotFoundError:
        print(f"Error: File not found. Please check the file path.")
        return None

def box_sat(sat_data, bot):
    boxed_sats = []

    max_x = bot.pos[0] + bot.b_range
    min_x = bot.pos[0] - bot.b_range
    max_y = bot.pos[1] + bot.b_range
    min_y = bot.pos[1] - bot.b_range
    max_z = bot.pos[2] + bot.b_range
    min_z = bot.pos[2] - bot.b_range
    for sat in sat_data:
        if not sat is None:
            pos = sat.pos
            if not (math.isnan(pos[0]) or math.isnan(pos[1]) or math.isnan(pos[2])):
                if (sat.type == "DEBRIS" and pos[0]<=max_x and pos[0]>=min_x and pos[1]<=max_y and pos[1]>=min_y and pos[2]<=max_z and pos[2]>=min_z):
                    boxed_sats.append(sat)
    return boxed_sats

