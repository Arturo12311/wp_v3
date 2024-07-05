import json
import re

with open('./data.json', 'r') as file:
    dataset = json.load(file)


class Chunkify:
    """
    example usage:
    chunkify = Chunkify(dataset)
    list_of_chunks = chunkify.run()
    
    outputs a list of dictionaries
    [{opcode: {chunk_dictionary}}, ...]
    """

    def __init__(self, dataset):
        self.dataset = dataset

    def run(self):
        list_of_chunks = self.get_list_of_chunks(self.dataset)
        return list_of_chunks

    def get_list_of_chunks(self, dataset):
        list_of_chunks = []

        for instance in dataset:
            json_str = instance['ToJsonString']
            opcode = instance['opcode_name']

            chunk = self.chunk_json_string(json_str) # returns dictionary
            chunk = self.prepend_base_field(chunk)
            named_chunk = {opcode: chunk}
            list_of_chunks.append(named_chunk)   

        return list_of_chunks
    
    def chunk_json_string(self, json_str):
        chunked = {}
        
        split_str = re.split(r'(\\\"[\w.]+\\\")', json_str) # split at fieldnames
        split_str = split_str[5:]
        
        for i in range(0, len(split_str), 2): 
            key = split_str[i].strip('\\\"') #index 1007 name not found (DAT_090cae0e)
            value = split_str[i + 1].strip()
            if key != "Members" and key and value:
                chunked[key] = value

        return chunked
    
    def prepend_base_field(self, chunk):
        if 'Base' in chunk:
            base_field = {'Base': chunk['Base']}
            chunk_without_base = {k: v for k, v in chunk.items() if k != 'Base'}
            base_prepended_chunk = base_field | chunk_without_base
            return base_prepended_chunk
        return chunk


class ClassifyChunk:
    """
    example usage:
    classify_chunk = ClassifyChunk(chunk)
    classified = classify_chunk.run()

    takas a chunk as input           {fieldname: string, ...}
    outputs the classified chunk     {fieldname: type, ...})
    """

    def __init__(self, chunk) -> None:
        self.chunk = chunk 
        self.classified = {}

    def run(self):
        for fieldname, string in self.chunk.items(): 
            type = self.classify_type(string) 
            self.classified[fieldname] = type
        return self.classified

    def get_patterns(self):
        patterns= [
            "(FTz\w+)::ToJsonString",
            "StaticEnum<(ETz\w+)>",
            "JsonSerializer<(TMap<[^,]+,TMap<[^,]+,[^,]+)",
            "JsonSerializer<(TMap<[^,]+,[^,]+)",
            "JsonSerializer<([^,]*)"
            ]
        return patterns

    def classify_type(self, string):
        patterns = self.get_patterns()
        for pattern in patterns:
            match = re.search(pattern, string)
            if match:
                type = match.group(1)
                return type
        return "unknown"



chunkify = Chunkify(dataset)
list_of_chunks = chunkify.run() # list of chunks

for _ in range(0, 10):
    for named_chunk in list_of_chunks:
        [(opcode, chunk)] = named_chunk.items()        
        classify_chunk = ClassifyChunk(chunk)    
        classified = classify_chunk.run()
        print(f"{opcode:<50} | {classified} \n\n-----------------------------------------------------------------------------------------------------------------")
