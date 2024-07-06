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
    def __init__(self) -> None:
        # regex patterns (struct, enum, map, array, basictype)
        self.patterns = [
            '(FTz\\w+)::ToJsonString',
            'StaticEnum<(ETz\\w+)>',
            'JsonSerializer<(TMap<[^,]+,TMap<[^,]+,[^,]+)',
            'JsonSerializer<(TMap<[^,]+,[^,]+)',
            'JsonSerializer<([^,]*)',
            'DAT_0901b5c8.*?pcVar10'
        ]

    def classify_chunk(self, chunked):
        self.classified = {} #output dict
        for fieldname, chunk in chunked.items(): #for each chunk 
            type = self.identify_type(chunk) #determine type
            self.classified[fieldname] = type 
        return self.classified #return dictionary of classified chunks

    def identify_type(self, chunk):
        for pattern in self.patterns: #for each pattern 
            match = re.search(pattern, chunk) #check if pattern in chunk
            if match:
                type = match.group(1) 
                return type #return matched pattern type
        return "unknown" #chunk didnt match a pattern

def output_to_console(opcode, fields_chunk): #temporary/testing pusrposes
    print("\n\n---------------------------------------------------")
    print(f'"{opcode}" {{')
    for fieldname, type in fields_chunk.items():
        print(f'    {fieldname:<30}: {type}')
    print('  }')


def main():
    """
    1. chunk raw data
    2. use regex to extract data
    3. format for output
    """

    # chunk 
    with open('./data.json', 'r') as file:
        dataset = json.load(file)
    chunkify = Chunkify()
    list_of_chunks = chunkify.get_list_of_chunks(dataset) 

    # classify 
    for chunk in list_of_chunks:
        [(opcode, chunk)] = chunk.items()    
        classify = ClassifyChunk()    
        classified = classify.classify_chunk(chunk)  
        output_to_console(opcode, classified)

    # output