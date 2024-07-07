import struct
import json
import re

with open('opcode_map.json', 'r') as file:
    opcode_dictionary = json.load(file)
with open('extractor_output.json', 'r') as file:
    data_structures_dictionary = json.load(file)

class Parser:
    """
    decodes data from bytestram to datastructures
    """
    def __init__(self):
        pass


    def parse(self, msg):
        msg_op = msg[0:5]; msg_op = self.get_opcode_name(msg_op) #opcode name
        msg_data = msg[5:] #payload data

        msg_dict = self.get_matching_dictionary(msg_op)
        
        print(f'Opcode Name: {msg_op}\nData Structure: {msg_dict}')

        for field, type in msg_dict.items():
            value, rest = self.parse_field(type, msg_data)
            if value is not None:
                msg_dict[field] = value
                msg_data = rest

        return msg_dict, msg_data # Return both the parsed dictionary and remaining data
    
    def get_matching_dictionary(self, name):
        if name in data_structures_dictionary: 
            matching_structure = data_structures_dictionary[name].copy()  # returns matching dictionary
        else:
            raise ValueError(f"Unknown opcode: {name}") 
        return matching_structure

    def parse_field(self, type, msg_data):
        if type == 'Fstring':
            length = struct.unpack('<I', msg_data[0:4])[0]
            value = msg_data[4:4+length].decode('utf-8')  # Assuming UTF-8 encoding
            rest = msg_data[4+length:]

        elif type == "int":
            value = struct.unpack('<I', msg_data[0:4])[0]
            rest = msg_data[4:]

        elif type == 'message':
            value, rest = self.parse(msg_data)

        elif '::ToJsonString' in type:
            value, rest = self.parse_structure(type, msg_data)

        else:
            raise ValueError(f"Unknown field type: {type}")
        return value, rest

    def parse_structure(self, string, rest):
        name_pattern = r'(?:FTz)?(.*)::ToJsonString'
        match = re.search(name_pattern, string)
        if not match:
            raise ValueError(f"Unable to parse structure name from '{string}'")
        
        name = match.group(1)
        struct_dict = self.get_matching_dictionary(name)
        
        for field, type in struct_dict.items():
            value, rest = self.parse_field(type, rest)
            struct_dict[field] = value
        
        return struct_dict, rest

    def get_opcode_name(self, op):
        if len(op) != 5:
            raise ValueError("Opcode must be 5 bytes long")
    
        null_byte = op[0]
        if null_byte != 0:
            raise ValueError("First byte of opcode must be null (0)")

        opcode = struct.unpack('<I', op[1:5])[0]
        opcode_name = opcode_dictionary.get(str(opcode))

        if opcode_name is None:
            raise ValueError(f"Unknown opcode: {opcode}")
        
        return opcode_name


def test_parser():
    packet = bytes([
            0, 208, 13, 160, 235, 0, 64, 134, 244, 147, 0, 32, 0, 0, 0, 91, 102, 101, 56, 48, 58, 58,
            56, 51, 53, 58, 99, 51, 98, 100, 58, 55, 98, 55, 101, 58, 49, 50, 102, 100, 93, 58, 52,
            57, 55, 52, 49, 2, 0, 0, 0, 103, 0, 0, 0, 2, 0, 0, 0, 0, 6, 0, 0, 0, 49, 52, 46, 55, 46,
            49, 0, 10, 0, 0, 0, 105, 80, 104, 111, 110, 101, 49, 50, 44, 49, 0, 0, 0, 0, 0, 0, 36, 0,
            0, 0, 53, 56, 53, 54, 56, 55, 50, 55, 45, 67, 69, 48, 49, 45, 52, 68, 48, 67, 45, 56, 52,
            69, 70, 45, 53, 48, 51, 57, 50, 65, 65, 54, 50, 68, 57, 56, 0, 2, 0, 0, 0, 67, 78, 0, 5,
            0, 0, 0, 122, 104, 95, 84, 87, 0, 9, 0, 0, 0, 49, 46, 49, 57, 48, 49, 46, 50, 48, 1, 0, 0,
            0, 0, 10, 0, 0, 0, 105, 79, 83, 32, 49, 52, 46, 55, 46, 49, 0, 17, 0, 0, 0, 50, 51, 55,
            52, 48, 48, 48, 48, 48, 48, 48, 49, 55, 51, 57, 53, 55, 0, 33, 0, 0, 0, 84, 79, 85, 97,
            100, 114, 70, 119, 114, 68, 56, 49, 106, 122, 68, 50, 67, 86, 71, 118, 70, 90, 74, 69,
            118, 105, 79, 71, 106, 104, 100, 89, 110, 0, 88, 0, 0, 0, 54, 86, 103, 74, 90, 111, 53,
            86, 76, 99, 75, 120, 121, 110, 122, 111, 116, 98, 84, 114, 67, 71, 120, 113, 50, 79, 49,
            49, 52, 115, 77, 49, 119, 113, 57, 66, 70, 106, 103, 67, 86, 105, 50, 117, 100, 54, 80,
            117, 98, 105, 97, 89, 85, 87, 52, 52, 81, 79, 66, 102, 73, 116, 73, 88, 47, 97, 75, 86,
            54, 88, 120, 52, 86, 52, 122, 112, 103, 57, 108, 51, 112, 75, 84, 116, 67, 81, 61, 61, 0,
            13, 0, 0, 0, 48, 84, 55, 48, 48, 87, 48, 49, 48, 52, 48, 50, 48, 240, 46, 17, 0, 0, 0, 0,
            0
        ])
    
    parser = Parser()
    try:
        result, remaining = parser.parse(packet)
        print("Parsing successful!")
        print("Parsed result:", result)
    except Exception as e:
        print(f"Parsing failed: {e}")

if __name__ == "__main__":
    test_parser()

# class Packer:
#     """
#     encodes data from datastructures to bytestream
#     """
#     pass

# # data for packer
# datastructures = {
#     "InfoAuthenticate": {
#         "AuthenticateInfo": "message"
#     },
#     "AuthenticateInfo": {
#         "local_area_network_address": "FString",
#         "market": "int",
#         "authentication_kind": "int",
#         "os_kind": "int",
#         "os_version": "FString",
#         "device_model": "FString",
#         "adid": "FString",
#         "idfv": "FString",
#         "country_code": "FString",
#         "language": "FString",
#         "app_version": "FString",
#         "os_type": "int",
#         "os_name": "FString",
#         "npsn": "FString",
#         "np_token": "FString",
#         "ngsm_token": "FString",
#         "npa_code": "FString",
#         "nexon_sn": "int",
#         "terminator": "int"
#     }
# }
