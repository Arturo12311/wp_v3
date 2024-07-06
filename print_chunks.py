import json
import re

with open('./data.json', 'r') as file:
    data = json.load(file)

def chunk_json_string(json_str):

    split_str = re.split(r'(\\\"\w+\\\")', json_str) # splits at and includes fieldnames
    split_str = split_str[5:]

    for i in split_str:
        print(i)
        print("----")
        
    print("---------------------------------------------------------")


count = 0
for instance in data:
    count += 1
    if count < 20:
        json_str = instance['ToJsonString']
        chunk_json_string(json_str)
    