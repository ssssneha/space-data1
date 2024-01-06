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

def scale_radius(xyz):
    x = xyz[0]
    y = xyz[1]
    z = xyz[2]
    r = math.sqrt(math.pow(x, 2) + math.pow(y, 2) + math.pow(z, 2))
    r1 = round(r/50)
    return r1

def check_in_list(val):
    possible_values = list(range(1000))
    if val in possible_values:
        return val


# output_loc_csv - json + output
def compile_arr(csv_data, output_file):
    total_counts = 0
    histogram = [[0] * 4 for _ in range(1000)]
    for sat in csv_data:
        if len(sat) == 5:
            #print(sat)
            if sat[1] == "DEBRIS":
                obj_type = 2
            elif sat[1] == "PAYLOAD":
                obj_type = 0
            elif sat[1] == "ROCKET BODY":
                obj_type = 1
            elif sat[1] == "UNKNOWN":
                obj_type = 3
            pos = get_xyz(sat)
            #print(f"{pos}")
            if not (math.isnan(pos[0]) or math.isnan(pos[1]) or math.isnan(pos[2])):
                radius = scale_radius(pos)
                if (radius >= 0 and radius <= 1000):
                    #print(f"{radius}")
                    val = check_in_list(radius)
                    #print(f"{radius} {val}")
                    count = histogram[val][obj_type]
                    #print(f"{count}")
                    count_in = count + 1
                    #print(f"Here! {radius} {val} {obj_type} {count_in}")
                    histogram[val][obj_type] = count_in
                    #print(f"{histogram[val][obj_type]}")
                total_counts += 1
                if (total_counts % 1000 ==0):
                    print(f"{total_counts} records written")
    print("now to csv...")
    #print(f"{histogram}")
    with open(output_file, 'w') as f:
        f.write(f"Radius,Payload,RocketBody,Debris,Unknown\n")
        ri = 0
        for elem in histogram:
            r = ri*50
            f.write(f"{r},{elem[0]},{elem[1]},{elem[2]},{elem[3]}\n")
            ri += 1
                


# main 
if __name__ == "__main__":
    
    if len(sys.argv) != 3:
        print("Usage: python gen_svg_from_csv.py input_file output_file")
        sys.exit(1)

    input_file = sys.argv[1]
    
    #print(input_file)
    output_file = sys.argv[2]

    print(f"Reading from file {input_file}")
    csv_data = read_csv_file(input_file)
    #print(csv_data)
    compile_arr(csv_data, output_file)