import csv
import sys

def print_TLE(file_p):
    with open(file_p, mode ='r') as file:
        csv_file = csv.reader(file)
        for lines in csv_file:
            print(lines)


if __name__ == "__main__":
    
    if len(sys.argv) != 2:
        print("Usage: python testing_csv.py input_file")
        sys.exit(1)

    input_file = sys.argv[1]

    #print(f"Reading from file {input_file}")
    #csv_file = read_csv_file(input_file)
    # print(json_data)
    print_TLE(input_file)