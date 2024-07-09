import struct
import json
import re
import sys

with open('_opcode_dict.json', 'r') as file:
    opcode_dictionary = json.load(file)
with open('_structures.json', 'r') as file:
    extracted_structs = json.load(file)

class Parse:
    """
    unpacks data from packet 
    1. get name
    2. get parsing structure
    3. parse
    """
    def __init__(self, packet, type="msg", struct_name=""):
        self.packet = packet
        self.type = type
        self.struct_name = struct_name
    
    def run(self):
        # get name 
        if self.type == "msg":
            name, bytes = self.get_msg_name(self.packet)
        elif self.type == "struct":
            name = self.struct_name
            bytes = self.packet

        # get parsing structure
        parsing_structure = self.get_parsing_structure(name)

        # console output
        print("\n-----------------------------------------------");print(f"Parsing \"{name}\" '{self.type}'...\n"); 
        print(f'fields:  {{')
        if parsing_structure != {}:
            for key, value in parsing_structure.items():
                print(f'    {key}: {value},')
            print("  }")
        else:
            print(f'    empty\n  }}')
        print('bytes:', [int(byte) for byte in bytes])
        print("-----------------------------------------------")
        
        # parse the bytes
        if parsing_structure == {}:
            parsed_data = {}
        else: 
            parsed_data, bytes = self.parse_fields(parsing_structure, bytes)

        # console output
        print("-----------------------------------------------");print(f"Finished \"{name}\"\nremaining bytes: {list(bytes)}"); print("-----------------------------------------------")

        # return the parsed bytes and the remaining bytes
        return parsed_data, bytes

    def get_msg_name(self, packet):  
        null_byte = packet[0]
        opcode = struct.unpack('<I', packet[1:5])[0]
        msg_name = opcode_dictionary.get(str(opcode))

        if str(opcode) == '67471100':
            msg_name = 'TlsLikeEncryptPremasterSecret'

        bytes = packet[5:]

        if msg_name is None:
            print(f"Warning: Opcode '{opcode}' not found in 'opcode_dict.json' for {list(packet)}")
            sys.exit(1)
        else:
            return msg_name, bytes

    def get_parsing_structure(self, name):
        if name in extracted_structs:
            return extracted_structs[name].copy() #returns the parsing structure (dict) 
        else:
            print(f"Warning: No parsing structure found with the name: '{name}' in 'extracted_structs.json'")
            sys.exit(1)

    def parse_fields(self, parsing_structure, bytes):
        print(f'\n---\nParsing fields...')
        parsed_struct = {}
        for fieldname, field_dict in parsing_structure.items():
            parsed_field, bytes = self.parse_field(field_dict, bytes, fieldname) 
            parsed_struct[fieldname] = parsed_field; 
        return parsed_struct, bytes 

    def parse_field(self, field_dict, bytes, fieldname):
        string = False
        bytes_before = bytes
        if field_dict['value'] == "FString" or field_dict['type'] == 'string':
            null = bytes[0]
            bytes = bytes[1:]
            length = struct.unpack('<I', bytes[0:4])[0]
            parsed_field = bytes[4:4+length].decode('iso-8859-1')
            bytes = bytes[4+length:]
            string = True

        elif field_dict['type'] == 'enum' or field_dict['value'] == 'int' or field_dict['value'] == 'FDateTime' or field_dict['value'] == 'Cuid':
            parsed_field = struct.unpack('<I', bytes[0:4])[0]
            bytes = bytes[4:]

        elif field_dict['value'] == 'long_long':
            parsed_field = struct.unpack('<Q', bytes[0:8])[0]
            bytes = bytes[8:]

        elif field_dict['type'] == 'message':
            parsed_field, bytes = Parse(bytes).run() 

        elif field_dict['type'] == 'struct':
            struct_name = field_dict['value']
            parsed_field, bytes = Parse(bytes, "struct", struct_name).run()
        
        elif field_dict['value'] == 'FVector':
            x, y, z = struct.unpack('<fff', bytes[:12])
            parsed_field = (x, y, z) 
            bytes = bytes[12:]       

        elif field_dict['type'] == 'vector':
            print("hi")
            print(bytes)
            null = bytes[0]
            bytes = bytes[1:]
            length = struct.unpack('<I', bytes[0:4])[0]
            print(length)
            vector_bytes = bytes[4:4+length]
            parsed_field = self.parse_type(field_dict['value'], vector_bytes)
            rest_bytes = bytes[4+length:]
            print(bytes)
        
        elif field_dict['type'] == 'bool':
            parsed_field = bytes[0]
            bytes = bytes[1:]

        else:
            print(f"\n\nUnknown field type: {field_dict['type']}, {field_dict['value']}")
            sys.exit(1)

        print(f'--\nfield name: {fieldname} \nfield type: {field_dict}\nbytes before: {list(bytes_before)}')
        if not string:
            print(f'bytes after: {list(bytes)}\nparsed field: {parsed_field}\n--\n')
        else:
            print(f'bytes after: {list(bytes)}\nparsed field: {parsed_field.encode("utf-8")}\n--\n')
        return parsed_field, bytes
    
    def parse_type(self, type, bytes):
        if type == 'unsigned_char':
            output = []
            while bytes:
                output.append(bytes[0])
                bytes = bytes[1:]
            return output

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
    parsed_data, bytes = Parse(packet).run()
    print("\n\n------------------------------\n")
    print(f'Parsing successful!\n-\nParsed Data: {parsed_data}\n-\n"Rest Bytes: {bytes}')
    print("\n------------------------------")

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
