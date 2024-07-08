import json

def process_item(structures, unique_values=None):
    if unique_values is None:
        unique_values = set()
    
    if isinstance(structures, dict):
        for key, value in structures.items():
            if isinstance(value, dict):
                if 'type' in value and 'value' in value:
                    # Add the type-value combination to our set
                    unique_values.add((value['type'], value['value']))
                else:
                    # Recurse into nested dictionaries
                    process_item(value, unique_values)
    elif isinstance(structures, list):
        for element in structures:
            process_item(element, unique_values)
    
    return unique_values

# Main execution
def main():
    file_name = '_structures.json'
    with open(file_name, 'r') as file:
        structures = json.load(file)
    
    unique_combinations = process_item(structures)
    
    print("Unique type-value combinations:")
    for type_field, value_field in sorted(unique_combinations):
        print(f"Type: {type_field}, Value: {value_field}")
    
    print("\nUnique values:")
    # Use a custom key function to handle None values
    def sort_key(x):
        return (x is None, x)
    
    unique_values = sorted(set(value for _, value in unique_combinations), key=sort_key)
    for value in unique_values:
        print(value)

if __name__ == "__main__":
    main()
