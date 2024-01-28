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

def scale_xyz(xyz):
    x1 = int (((xyz[0]*1000)/50000) + 1000)
    y1 = int (((xyz[1]*1000)/50000) + 1000)
    z1 = int (((xyz[2]*1000)/50000) + 1000)
    arr = [x1,y1,z1]
    return arr


# output_loc_csv - json + output
def output_loc_csv(csv_data, output_file):
    total_counts = 0
    box_count = 0
    box_size = 2500
    bx = 7250
    by = 0
    bz = 0
    max_x = bx + (box_size/2)
    min_x = bx - (box_size/2)
    max_y = by + (box_size/2)
    min_y = by - (box_size/2)
    max_z = bz + (box_size/2)
    min_z = bz - (box_size/2)
    with open(output_file, 'w') as f:
        f.write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2000 2000">')
        f.write("<g>")
        #lightcoral lightseagreen
        # and sat[1] == "DEBRIS"
        for sat in csv_data:
            #print(sat)
            if len(sat) == 5:
                #print(sat)
                if sat[1] == "DEBRIS":
                    currentcolor = "lightcoral"
                elif sat[1] == "PAYLOAD":
                    currentcolor = "lightseagreen"
                elif sat[1] == "ROCKET BODY":
                    currentcolor = "gold"
                elif sat[1] == "UNKNOWN":
                    currentcolor = "mediumpurple"
                pos = get_xyz(sat)
                if not (math.isnan(pos[0]) or math.isnan(pos[1]) or math.isnan(pos[2])):
                    if (sat[1] == "DEBRIS" and pos[0]<=max_x and pos[0]>=min_x and pos[1]<=max_y and pos[1]>=min_y and pos[2]<=max_z and pos[2]>=min_z):
                        box_count = box_count + 1 
                    if (pos[2]>=-500 and pos[2]<=500):
                        pos1 = scale_xyz(pos)
                        #print(f"{pos}")
                        f.write(f'<circle cx="{pos1[0]}" cy="{pos1[1]}" r="2" fill="{currentcolor}"/>\n')
                        total_counts += 1
                    #if (total_counts % 1000 ==0):
                        #print(f"{total_counts} records written")
        earth_r = int (((6378*1000)/50000))
        
        f.write(f'<circle cx="1000" cy="1000" r="{earth_r}" stroke="black" fill="transparent" stroke-width="2"/>')
        f.write(f'<line x1="1137" y1="1008" x2="1153" y2="1008" stroke="black" stroke-width="2"/>')
        f.write(f'<line x1="1153" y1="1008" x2="1153" y2="992" stroke="black" stroke-width="2"/>')
        f.write(f'<line x1="1153" y1="992" x2="1137" y2="992" stroke="black" stroke-width="2"/>')
        f.write(f'<line x1="1137" y1="992" x2="1137" y2="1008" stroke="black" stroke-width="2"/>')
        f.write("</g>")
        f.write("</svg>")
        print(f"{total_counts}")
                


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
    output_loc_csv(csv_data, output_file)