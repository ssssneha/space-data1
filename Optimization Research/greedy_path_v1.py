import json
import sys
import math
import csv

# open_stream
# loop through json data - for each one get xyz, name, ID, type
# then write out to file and close

def read_csv_file(file_path):
    try:
        csv_data = []
        with open(file_path, 'r') as file:
            csv_reader = csv.reader(file)
            next(csv_reader, None)
            for lines in csv_reader:
                csv_data.append(lines)
        return csv_data

    except FileNotFoundError:
        print(f"Error: File not found. Please check the file path.")
        return None

def get_xyz(rows):
    x = rows[2]
    y = rows[3]
    z = rows[4]
    xyz = [float(x),float(y),float(z)]
    return xyz

def gen_greedy_path(box_data, box_center):
    total_distance = 0
    path = []
    bot_point = box_center
    for i in range(len(box_data)):
        min_dist = -1
        best_sat = None
        for sat in box_data:
            if not sat in path:
                dist = get_dist(bot_point, get_xyz(sat))
                if dist < min_dist or min_dist < 0:
                    min_dist = dist
                    best_sat = sat

        if best_sat == None:
            print ("Something bad happened")
            sys.exit()
        
        path.append(best_sat)
        bot_point = get_xyz(best_sat)
        total_distance += min_dist
        #print(f" min {min_dist}")
        #print(total_distance)
    return path, total_distance

def get_dist(a, b):
    #print("IN FUNC")
    #print(a)
    #print(b)
    d = math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2 + (a[2]-b[2])**2)
    return d

# output_loc_csv - json + output
def box_sat(csv_data, box_center, box_size):
    box_count = []
    bx = box_center[0]
    by = box_center[1]
    bz = box_center[2]
    max_x = bx + (box_size/2)
    min_x = bx - (box_size/2)
    max_y = by + (box_size/2)
    min_y = by - (box_size/2)
    max_z = bz + (box_size/2)
    min_z = bz - (box_size/2)
    for sat in csv_data:
        #print(sat)
        if len(sat) == 5:
            pos = get_xyz(sat)
            if not (math.isnan(pos[0]) or math.isnan(pos[1]) or math.isnan(pos[2])):
                if (sat[1] == "DEBRIS" and pos[0]<=max_x and pos[0]>=min_x and pos[1]<=max_y and pos[1]>=min_y and pos[2]<=max_z and pos[2]>=min_z):
                    box_count.append(sat)
    return box_count

# main 
if __name__ == "__main__":
    
    if len(sys.argv) != 2:
        print("Usage: python greedy_path.py input_file")
        sys.exit(1)

    input_file = sys.argv[1]

    
    #print(input_file)
    #output_file = sys.argv[2]

    print(f"Reading from file {input_file}")
    csv_data = read_csv_file(input_file)
    #print(csv_data)
    boxing = box_sat(csv_data, [7250,0,0], 1000)
    path, distance = gen_greedy_path(boxing, [7250,0,0])
    print(path)
    print(distance)