import json
import csv
import argparse

def json_to_csv(input_file, output_file):
    # Load the JSON data
    with open(input_file, 'r') as json_file:
        data = json.load(json_file)

    # Open a CSV file for writing
    with open(output_file, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)

        # Write the header
        header = ['host', 'hostid', 'icmp_id'] + [key for key in data[0].keys() if key not in ['host', 'hostid', 'icmp_id']]
        csv_writer.writerow(header)

        # Write the data
        for entry in data:
            row = [entry.get(key, '') for key in header]
            csv_writer.writerow(row)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert JSON to CSV.')
    parser.add_argument('input_file', help='Full path to the input JSON file')
    parser.add_argument('output_file', help='Path to the output CSV file')
    args = parser.parse_args()

    json_to_csv(args.input_file, args.output_file)