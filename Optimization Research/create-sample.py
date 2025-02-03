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

def get_sample_data(json_data, sampleCount):
    sample = []
    objectCounts = {}
    totalCounts = 0
    for item in json_data:
        if "OBJECT_TYPE" in item:
            object_type_value = item["OBJECT_TYPE"]
            objectCounts[object_type_value] = objectCounts.get(object_type_value, 0) + 1
            if (objectCounts[object_type_value] <= sampleCount):
                sample.append(item)
                totalCounts += 1
    return sample, totalCounts

if __name__ == "__main__":
    # Check if the correct number of command-line arguments is provided
    if len(sys.argv) != 4:
        print("Usage: python object-counts.py input_file output_file Count")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    sampleCount = int(sys.argv[3])
    
    json_data = read_json_file(input_file)
    
    # if not json_data:
    if json_data is None:
        print(f"Error: No data to process.")
        sys.exit(1)

    sample, totalSamples = get_sample_data(json_data, sampleCount)
    # print(json.dumps(sample, indent=4))
    # write out the sample array as a JSON
    with open(output_file, 'w') as outfile:
        json.dump(sample, outfile, indent=4)
    print(f"{totalSamples} sample records, {sampleCount} per type, written to {output_file}")
        