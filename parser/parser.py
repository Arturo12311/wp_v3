import struct
import json

with open('opcode_map.json', 'r') as file:
    opcode_dictionary = json.load(file)
with open('extractor_output.json', 'r') as file:
    data_structures_dictionary = json.load(file)

class Unpacker:
    """
    decodes data from bytestram to datastructures
    """
    def __init__(self) -> None:
        pass

    def unpack(self, packet):
        # split the packet 
        op = packet[:5]
        payload = packet[5:] 

        # get the opcode name
        op_name = self.get_opcode_name(op) 
        if not op_name: return 

        # get the data structure
        if op_name in data_structures_dictionary:
            data_structure = data_structures_dictionary[op_name]
        if not data_structure: return 

        # console output
        print(f'Opcode Name: {op_name}\nData Structure: {data_structure}')

    def get_opcode_name(self, op):
        # split opcode
        op_null = op[:1] # null byte    
        op = op[1:5]     

        # translate opcode to little-32 integer
        op_int = struct.unpack('<I', op)[0] 

        # get opcode name
        if str(op_int) in opcode_dictionary:         
            op_name = opcode_dictionary[str(op_int)] 
            return op_name

# test/run Unpacker
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
unpacker = Unpacker()
unpacker.unpack(packet)

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
