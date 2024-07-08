import json
import re

def extract_unique_types(data):
    unique_types = set()

    def process_item(item):
        if isinstance(item, dict):
            for value in item.values():
                if isinstance(value, str):
                    unique_types.add(value)
                else:
                    process_item(value)
        elif isinstance(item, list):
            for element in item:
                process_item(element)

    process_item(data)
    return sorted(list(unique_types))

# Read the JSON file
file_name = 'extracted_structs.json'
with open(file_name, 'r') as file:
    json_data = json.load(file)

# Extract unique types
unique_types = extract_unique_types(json_data)

# Print the unique types
print("Unique Types:")
for type_name in unique_types:
    print(type_name)

print(f"\nTotal unique types: {len(unique_types)}")
