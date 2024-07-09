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
            struct_formatted[field_name] = field_formatted #dict
        return struct_formatted 
    
    def format_field(self, chunk):
        is_nullable = self.is_nullable(chunk) #True or False
        if self.is_message(chunk): 
            type = 'message'
            value = None
        elif self.is_bool(chunk):
            type = 'bool'
            value = None
        elif self.is_enum(chunk):
            type = 'enum'
            value = None
        elif self.is_struct(chunk):
            type = 'struct'
            value = self.get_struct_name(chunk)
            if value == 'Cuid':
                type = 'custom'
                value = 'Cuid'
        elif self.is_map(chunk):
            type = 'map'
            value = self.get_map(chunk)
        elif self.is_array(chunk):
            type = 'array'
            value = self.get_array(chunk)
        elif self.is_basic(chunk):
            type = 'basic'   
            value = self.get_basic(chunk)     
        elif self.is_vector(chunk):
            type = 'vector'
            value = self.vector_type(chunk)
        elif self.is_string(chunk):
            type = 'string'
            value = self.get_string(chunk)
        elif self.is_custom(chunk):
            type = 'custom'
            value = self.get_custom(chunk)
        elif self.is_char(chunk):
            type = 'char'
            value = self.get_char_type(chunk)
        else:
            type = 'unknown'
            value = None

        return {'type': type, 'value': value, 'nullable': is_nullable}

    # HELPERS
    def is_nullable(self, chunk):
        pattern = r'\(in_x0 \+ (0x)?[0-9A-Fa-f]+\) == (0|(long *)0x0)'
        return bool(re.search(pattern, chunk)) #True or False
    
    def is_message(self, chunk):
        pattern = r'\(\*\*\(code \*\*\)\(\*\*\(long \*\*\)'
        return bool(re.search(pattern, chunk)) 
    
    def is_bool(self, chunk):
        pattern = r'\(in_x0 \+ (0x)?[0-9A-Fa-f]+\) == \'\\0\'|DAT_0901b5c8' 
        return bool(re.search(pattern, chunk)) 

    def is_enum(self, chunk):
        pattern = 'StaticEnum<(ETz\\w+)>'
        return bool(re.search(pattern, chunk)) 
        
    def is_struct(self, chunk):
        pattern = r'\s*(.*::ToJsonString())'
        return bool(re.search(pattern, chunk)) 
    def get_struct_name(self, chunk):
        pattern = r'(?:::)?(?:FTz)?(\w+)::ToJsonString'
        return (re.search(pattern, chunk)).group(1)
        
    def is_map(self, chunk):
        pattern = r'JsonSerializer(<TMap<.*>)[\s\n]*::'
        return bool(re.search(pattern, chunk)) 
    def get_map(self, chunk):
        pattern = r'JsonSerializer(<TMap<.*>)>'
        return (re.search(pattern, chunk)).group(1)
    
    def is_array(self, chunk):
        pattern = r'JsonSerializer(<TArray<.*>)[\s\n]*::'
        return bool(re.search(pattern, chunk))
    def get_array(self, chunk):
        pattern = r'JsonSerializer(<TArray<.*>)[\s\n]*::'
        return (re.search(pattern, chunk)).group(1)
    
    def is_basic(self, chunk):
        pattern = r'JsonSerializer<([^,]*)'
        basic_types = [
            'int', 'uint', 'float', 'long', 'long_long', 'short', 'unsigned_short',
            'signed_char', 'unsigned_char', 'unsigned_int'
        ]
        match = re.search(pattern, chunk)
        if match: 
            return bool(match and match.group(1) in basic_types)
    def get_basic(self, chunk):
        pattern = r'JsonSerializer<([^,]*)'
        return (re.search(pattern, chunk)).group(1)
    
    def is_vector(self, chunk):
        pattern = r'ndk1::vector<([^,]*),'
        return bool(re.search(pattern, chunk))
    def vector_type(self,chunk):
        pattern = r'::vector<([^,]*),'
        print(chunk)
        return (re.search(pattern, chunk)).group(1)
    
    def is_string(self, chunk):
        pattern = r'basic_string<([^,]*),'
        return bool(re.search(pattern, chunk))
    def get_string(self, chunk):
        pattern = r'basic_string<([^,]*),'
        return (re.search(pattern, chunk)).group(1)

    def is_custom(self, chunk):
        pattern = r'JsonSerializer<([^,]*)'
        return bool(re.search(pattern, chunk))
    def get_custom(self, chunk):
        pattern = r'JsonSerializer<([^,]*)'
        return (re.search(pattern, chunk)).group(1)
    
    def is_char(self, chunk):
        pattern = r'DefaultAllocator<[^>]*>'
        return bool(re.search(pattern, chunk))
    def get_char_type(self, chunk):
        pattern = r'DefaultAllocator<([^>]*)>'
        return (re.search(pattern, chunk)).group(1)

class Export:
    """
    exports the formatted_data to specified file
    """
    def __init__(self):
        pass

    def export(self, formatted_data, filename):
        with open(filename, 'w') as outfile:
            json.dump(formatted_data, outfile, indent=4)
        print(f"\nClassification data has been written to {filename}")

    def output_to_console(self, opcode, formatted_fields): 
        print("\n\n---------------------------------------------------")
        print(f'"{opcode}": {{')
        for fieldname, formatted_field in formatted_fields.items():
            print(f'    {fieldname:<30}: {formatted_field}') 
        print('  }')


# run the program
with open('./_raw_data.json', 'r') as file:
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

output_file = '_structures.json'
export.export(parsing_structures_formatted, output_file)