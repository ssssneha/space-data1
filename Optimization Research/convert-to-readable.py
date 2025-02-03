import sys
import json

def read_and_write_json(input_file, output_file):
    try:
        # Read JSON data from input file
        with open(input_file, 'r') as infile:
            data = json.load(infile)

        # Write formatted JSON data to output file
        with open(output_file, 'w') as outfile:
            json.dump(data, outfile, indent=4)

        print(f"Successfully formatted and wrote JSON data to {output_file}")
    
    except FileNotFoundError:
        print(f"Error: File not found. Please check the file paths.")
    
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")

if __name__ == "__main__":
    # Check if the correct number of command-line arguments is provided
    if len(sys.argv) != 3:
        print("Usage: python convert-to-readable.py input_file output_file")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    read_and_write_json(input_file, output_file)
