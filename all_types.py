import json
import re

def extract_unique_types(data):
    unique_types = set()

    def process_item(item):
        if isinstance(item, dict):
            for value in item.values():
                if isinstance(value, str):
                    # Remove any parentheses and their contents
                    clean_value = value.split('(')[0].strip()
                    # Split by :: and take the first part
                    type_name = clean_value.split('::')[0].strip()
                    # Remove ETz and FTz prefixes
                    type_name = re.sub(r'^[EF]Tz', '', type_name)
                    unique_types.add(type_name)
                else:
                    process_item(value)
        elif isinstance(item, list):
            for element in item:
                process_item(element)

    process_item(data)
    return sorted(list(unique_types))

# Read the JSON file
file_name = 'extractor_output.json'
with open(file_name, 'r') as file:
    json_data = json.load(file)

# Extract unique types
unique_types = extract_unique_types(json_data)

# Print the unique types
print("Unique Types:")
for type_name in unique_types:
    print(type_name)

print(f"\nTotal unique types: {len(unique_types)}")
