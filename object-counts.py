import sys
import json

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



if __name__ == "__main__":
    # Check if the correct number of command-line arguments is provided
    if len(sys.argv) != 2:
        print("Usage: python object-counts.py input_file")
        sys.exit(1)

    input_file = sys.argv[1]

    json_data = read_json_file(input_file)

    if json_data is not None:
        print("Object Counts")
        # print(json_object)
        # inialize a variable count to 0
        objectCounts = {}

        for item in json_data:
            if "OBJECT_TYPE" in item:
                object_type_value = item["OBJECT_TYPE"]
                objectCounts[object_type_value] = objectCounts.get(object_type_value, 0) + 1
        
        totalCount = 0
        for key, count in objectCounts.items():
            print(f"{key} \t {count}")
            totalCount += count
        
        # print total count
        print ("-" * 20)
        print(f"TOTAL \t {totalCount}")
