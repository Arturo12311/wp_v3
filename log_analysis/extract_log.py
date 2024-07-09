import re
import json

# import log as string
with open('C:\\type_formatter\\log_analysis\\log.txt', 'r', encoding='utf-8') as file:
    file = file.read()

# find patterns in log
pattern = r'\'Elixir\.(.*)\'|[^o]data =>\s*<<([\s\S]*?)>>'
matches = re.findall(pattern, file)

# add each log to output dict
name = ''
bytes = ''
output = {}
for match in matches:
    if match[0] != '':
        name = match[0]
    else:
        bytes = match[1]
        bytes = ''.join(bytes.split())
        output[name] = bytes

for key, value in output.items():
    print(f'{key}: {value}\n--\n')

# output to file
with open('log_bytes.json', 'w') as file:
    json.dump(output, file, indent=4)