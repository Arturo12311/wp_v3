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

    def classify_chunk(self, chunked):
        self.classified = {} #output dict
        for fieldname, chunk in chunked.items(): #for each chunk
            chunk_tuple = self.determine_type(chunk) 
            self.classified[fieldname] = chunk_tuple #tuple as value for each fieldname key
        return self.classified #return dictionary of classified chunks
    
    def determine_type(self, chunk):
        nullable = self.is_nullable(chunk) #check if nullable
        is_message = self.is_message(chunk) 
        if is_message: return (nullable, 'message') #check if bool
        is_bool = self.is_bool(chunk) 
        if is_bool: return (nullable, 'bool') #check if bool
        type = self.other_types(chunk) #check other types if not bool
        type = self.clean_type(type) 
        return (nullable, type) #returns tuple
    
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
        return bool(re.search(nullable_pattern, chunk)) #is nullable pattern in chunk?

    def other_types(self, chunk):
        # regex patterns (struct, enum, map/array/basictype)
        type_patterns = [
            '\s*(.*::ToJsonString())',
            'StaticEnum<(ETz\\w+)>',
            'JsonSerializer(<.*>)[\s\n]*::',
        ]
        for pattern in type_patterns: #for each type pattern 
            match = re.search(pattern, chunk) #check if pattern in chunk
            if match:
                type = match.group(1) 
                return type #return matched pattern type
        return "unknown" #didnt match a pattern
    
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
    chunks, classifies, then exports the formatted_data to specified file
    """
    def __init__(self):
        pass

    def run(self):
        list_of_chunks = self.chunk()
        formated_data = self.classify(list_of_chunks)
        self.export(formated_data)

    def chunk(self):
        with open('./data.json', 'r') as file:
            dataset = json.load(file)
        chunkify = Chunkify()
        list_of_chunks = chunkify.get_list_of_chunks(dataset) 
        return list_of_chunks

    def classify(self, list_of_chunks):
        formatted_data = {}
        for chunk in list_of_chunks:
            [(opcode, chunk)] = chunk.items()    
            classify = ClassifyChunk()    
            classified_fields = classify.classify_chunk(chunk) #dictionary of classified types
            formatted_fields = self.format_fields(classified_fields) 
            formatted_data[opcode] = formatted_fields #adds {'opcode': 'formatted_fields dictionary'} to output dictionary
            # self.output_to_console(opcode, classified_fields) #not needed for now
        return formatted_data

    def format_fields(self, classified_fields):
        formatted_fields = {}  
        for fieldname, type_info in classified_fields.items(): 
            if not type_info[0]: #not nullable
                formatted_fields[fieldname] = type_info[1] #just put the type name if not nullable
            else:
                formatted_fields[fieldname] = f"(nullable, {type_info[1]})" #add 'nullable' if nullable type
        return formatted_fields
    
    def export(self, formatted_data):
        with open('extractor_output.json', 'w') as outfile:
            json.dump(formatted_data, outfile, indent=2)
        print("\nClassification data has been written to 'extractor_output.json'")

    def output_to_console(self, opcode, fields_chunk): 
        print("\n\n---------------------------------------------------")
        print(f'"{opcode}" {{')
        for fieldname, type in fields_chunk.items():
            if type[0] == False: #not nullable
                print(f'    {fieldname:<30}: {type[1]}') #just print the type
            else:
                print(f'    {fieldname:<30}: (nullable, {type[1]})') #prepend nullable label
        print('  }')

export = Export()
export.run()

