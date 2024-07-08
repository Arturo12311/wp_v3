import json
import re

with open('extracted_structs.json', 'r') as file:
    structs = json.load(file)

def clean_field_value(field_value):
    pass

cleaned_struct_field_values = {}
for struct_name, struct in structs.items():
    for field_name, field_value in struct.items():
        field_value = clean_field_value(field_value)
        struct[field_name] = field_value
    structs[struct_name] = struct
    
        
with open('cleaned_structs.json', 'w') as json_file:
    json.dump(structs, json_file, indent=4)

print("cleaned extracted structs.  Check cleaned_structs.json")