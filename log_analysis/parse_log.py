import json
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
from packet_processor import Parse

# open file
with open('C:/Type_Formatter/log_analysis/log.json', 'r') as file:
    file = json.load(file)

# parse each instance
output = {}
for name, bytestream in file.items():
    bytestream = bytes(map(int, bytestream.split(',')))
    parsed = Parse(bytestream).run()
    output[name] = parsed

with open('C:/Type_Formatter/log_analysis/parsed_log.json', 'r') as file:
    json.dump(output, file, indent=4)
    