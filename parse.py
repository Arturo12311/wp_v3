import json
import re

with open('./data.json', 'r') as file:
    dataset = json.load(file)


class Chunkify:
    """
    example usage:
    chunkify = Chunkify(dataset)
    list_of_chunks = chunkify.run()
    
    returns a list of dictionaries
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
            chunk = self.chunk_json_string(json_str)
            list_of_chunks.append(chunk)
        
        return list_of_chunks
    
    def chunk_json_string(self, json_str):
        chunked = {}
        
        split_str = re.split(r'(\\\"\w+\\\")', json_str) # splits at and includes fieldnames
        split_str = split_str[5:]
        
        for i in range(0, len(split_str), 2): 
            key = split_str[i].strip('\\\"')
            value = split_str[i + 1].strip()
            if key and value:
                chunked[key] = value

        return chunked

class ClassifyType:
    def __init__(self) -> None:
        pass
    
