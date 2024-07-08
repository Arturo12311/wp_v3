"""
makes raw c++ pseudocode more useful by extracting fieldnames and types using regex.
Then formats the extracted data and exports it.
[
    1. divide raw data (c++ pseudocode) into chunks
    2. extract fieldname and type from each chunk
    3. format and export 
]
"""
import json
import re

class Chunkify:
    """
    splits data into useful chunks
    """
    def __init__(self):
        pass

    def get_list_of_chunks(self, dataset):
        list_of_chunks = [] #output list
        for instance in dataset:
            json_str = instance['ToJsonString']
            opcode = instance['opcode_name']
            chunked = self.chunk_json_string(json_str) #returns dictionary {fieldname: string/chunk}
            chunked = self.prepend_base_field(chunked) #makes base field come first
            formatted = {opcode: chunked}
            list_of_chunks.append(formatted) #add to output list
        return list_of_chunks 
    
    def chunk_json_string(self, json_str):
        chunked = {} #output dict
        split_str = re.split(r'(\\\"[\w.]+\\\")', json_str) #split at fieldnames
        split_str = split_str[5:] #cut unneeded data
        for i in range(0, len(split_str), 2): 
            key = split_str[i].strip('\\\"') #fieldname
            value = split_str[i + 1].strip() #chunk
            if key != "Members" and key and value:
                chunked[key] = value #add to output dict
        return chunked 
    
    def prepend_base_field(self, chunked):
        if 'Base' in chunked:
            base = {'Base': chunked['Base']} #save base value
            removed_base = {k: v for k, v in chunked.items() if k != 'Base'}
            fixed = base | removed_base 
            return fixed #'base' field comes first now
        return chunked

class ClassifyChunk:
    """
    classifies chunk to specific type
    """
    def __init__(self):
        pass

    def format_fields(self, struct_chunk):
        struct_formatted = {} #output dict
        for field_name, field_chunk in struct_chunk.items(): 
            field_formatted = self.format_field(field_chunk) 
            struct_formatted[field_name] = field_formatted #{type: x, size: y, nullable: z}
        return struct_formatted 
    
    def format_field(self, chunk):
        nullable = self.is_nullable(chunk) #check if nullable
        is_message = self.is_message(chunk) 
        if is_message: return (nullable, 'message') #check if bool
        is_bool = self.is_bool(chunk) 
        if is_bool: return (nullable, 'bool') #check if bool
        other_type = self.other_types(chunk) #check other types if not bool
        type = self.clean_type(type) 
        return (nullable, type) #{type: x, size: y, nullable: z}

    def is_char(self, chunk):
        char_pattern = r'DefaultAllocator<([^>]*)>'
        match = re.search(char_pattern, chunk)
        if match:
            signed_or_unsigned = match.group(1)
            return signed_or_unsigned

    def is_message(self, chunk):
        message_pattern = r'\(\*\*\(code \*\*\)\(\*\*\(long \*\*\)'
        return bool(re.search(message_pattern, chunk)) #is message pattern in chunk?
    
    def is_bool(self, chunk):
        bool_pattern = r'\(in_x0 \+ (0x)?[0-9A-Fa-f]+\) == \'\\0\'|DAT_0901b5c8' 
        match = re.search(bool_pattern, chunk)
        if match: 
            return True

    def is_nullable(self, chunk):
        nullable_pattern = r'\(in_x0 \+ (0x)?[0-9A-Fa-f]+\) == (0|(long *)0x0)'
        return bool(re.search(nullable_pattern, chunk)) #True or False

    def is_enum(self, chunk):
        enum_pattern = 'StaticEnum<(ETz\\w+)>'
        match = re.search(enum_pattern, chunk)
        if match: 
            enum_name = match.group(1)
            return enum_name
        
    def is_struct(self, chunk):
        struct_pattern = r'\s*(.*::ToJsonString())'
        match = re.search(struct_pattern, chunk)
        if match:
            struct_name = match.group(1)
            return struct_name
        
    def is_map(self, chunk):
        map_pattern = r'JsonSerializer(<TMap<.*>)[\s\n]*::'
        match = re.search(map_pattern, chunk)
        if match:
            map_name = match.group(1)
            return map_name
    
    def is_array(self, chunk):
        array_pattern = r'JsonSerializer(<TArray<.*>)[\s\n]*::'
        match = re.search(array_pattern, chunk)
        if match:
            array_name = match.group(1)
            return array_name
    
    def is_basic(self, chunk):
        pattern = r'JsonSerializer(<.*>)[\s\n]*::'
        match = re.search(pattern, chunk)
        if match:
            name = match.group(1)
            return name

    def clean_type(self, type):
        patterns = [
            r'(TMap<[^,]*,TMap<[^,]*,[^,]*,TMap<[^,]*,[^,]*)',#Nested Nested TMap
            r'(TMap<[^,]*,TMap<[^,]*,[^,]*)', #Nested TMap
            r'(TMap<[^,]*,[^,]*)',            #TMap
            r'(TArray<[^,]*),',               #TArray
            r'<(.*),void>'                    #Basic          
        ]
        for pattern in patterns: 
            match = re.search(pattern, type) #check if pattern is in type
            if match: 
                return match.group(1) #return the extracted pattern if matched
        return type #keep the same if no match

class Export:
    """
    exports the formatted_data to specified file
    """
    def __init__(self):
        pass

    def export(self, formatted_data, filename):
        with open(filename, 'w') as outfile:
            json.dump(formatted_data, outfile, indent=2)
        print(f"\nClassification data has been written to {filename}")

    def output_to_console(self, opcode, formatted_fields): 
        print("\n\n---------------------------------------------------")
        print(f'"{opcode}": {{')
        for fieldname, formatted_field in formatted_fields.items():
            print(f'    {fieldname:<30}: {formatted_field}') 
        print('  }')


# run the program
with open('./data.json', 'r') as file:
    data = json.load(file)

parsing_structures_formatted = {}
chunkify = Chunkify()
classify = ClassifyChunk()
export = Export()

parsing_structures_chunks = chunkify.get_list_of_chunks(data)
for chunk in parsing_structures_chunks:
    [(struct_name, struct_chunk)] = chunk.items()   
    struct_formatted = classify.format_fields(struct_chunk) 
    parsing_structures_formatted[struct_name] = struct_formatted #dict
    export.output_to_console(struct_name, struct_formatted)

output_file = 'parsing_structures.json'
export.export(parsing_structures_formatted, output_file)