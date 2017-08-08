import struct
from collections import Counter
from MoveInfoEnums import InputDirectionCodes

class MovelistParser:
    class EscapeAll(bytes):
        def __str__(self):
            return 'b\'{}\''.format(''.join('\\x{:02x}'.format(b) for b in self))

    class MoveNode:
        def __init__(self, forty_bytes, offset, all_bytes, all_names):


            #self.input_bytes = forty_bytes[0:8]

            try:
                self.direction_bytes = InputDirectionCodes(struct.unpack('<H', forty_bytes[0:2])[0]).name
            except:

                self.direction_bytes = '{:x}'.format(struct.unpack('<H', forty_bytes[0:2])[0])
                print("Failed to find direction code for {}".format(self.direction_bytes))

            self.unknown_input_dir = struct.unpack('<H', forty_bytes[2:4])[0]
            self.attack_bytes = struct.unpack('<H', forty_bytes[4:6])[0]
            self.unknown_buton_press = struct.unpack('<H', forty_bytes[6:8])[0]

            self.pointer_one = struct.unpack('<Q', forty_bytes[8:16])[0] - offset
            self.pointer_two = struct.unpack('<Q', forty_bytes[16:24])[0] - offset
            self.number_one = struct.unpack('<I', all_bytes[self.pointer_one: self.pointer_one + 4])[0]
            self.number_two = struct.unpack('<I', all_bytes[self.pointer_two: self.pointer_two + 4])[0]

            self.unknown_bool = struct.unpack('<I', forty_bytes[24:28])[0]
            self.cancel_window_1 = struct.unpack('<I', forty_bytes[28:32])[0]
            self.cancel_window_2 = struct.unpack('<I', forty_bytes[32:36])[0]
            #self.unknown_bytes = forty_bytes[24:36]
            self.move_id = int(struct.unpack('<H', forty_bytes[36:38])[0])
            self.unknown_two_byte = forty_bytes[38:40]

            if self.move_id < len(all_names):
                self.name = all_names[self.move_id]
            else:
                self.name = self.move_id

        def __repr__(self):
            return '{} | {} |{:x} |{:x} |{:x} | {:x} | {:x} | {} | {} | {} | {:x} | {}'.format(
                self.name, self.direction_bytes, self.unknown_input_dir, self.attack_bytes, self.unknown_buton_press, self.number_one, self.number_two, self.unknown_bool, self.cancel_window_1, self.cancel_window_2, self.move_id, self.unknown_two_byte)


    def __init__(self, movelist_bytes, movelist_pointer):
        self.bytes = movelist_bytes
        self.pointer = movelist_pointer
        self.parse_header()



    def parse_header(self):
        header_length = 0x2e8
        header_bytes = self.bytes[0:header_length]
        identifier = self.header_line(0)
        char_name_address = self.header_line(1)
        developer_name_address = self.header_line(2)
        date_address = self.header_line(3)
        timestamp_address = self.header_line(4)


        #print ('{:x}'.format(date_address - self.pointer))
        print(self.bytes[char_name_address:developer_name_address])

        unknown_regions = {}
        for i in range(42, 91, 2):
            unknown_regions[i] = self.header_line(i)
            #print(unknown_regions[i])

        #self.names = self.bytes[timestamp_address:unknown_regions[42]]
        self.names_double = self.bytes[header_length:unknown_regions[42]].split(b'\00')[4:]
        self.names = []
        for i in range(0, len(self.names_double) - 1, 2):
            self.names.append(self.names_double[i].decode('utf-8') + '/' + self.names_double[i+1].decode('utf-8'))


        self.move_nodes_raw = self.bytes[unknown_regions[54]:unknown_regions[58]] #there's two regions of move nodes, first one might be blocks????
        self.move_nodes = []
        for i in range(0, len(self.move_nodes_raw), 40):
            self.move_nodes.append(MovelistParser.MoveNode(self.move_nodes_raw[i:i+40], self.pointer, self.bytes, self.names))


        self.linked_nodes_raw = self.bytes[unknown_regions[46]:unknown_regions[48]]
        self.linked_nodes = []
        #for i in range(0, len(self.linked_nodes_raw), 24):

        #for node in self.move_nodes:
            #if node.move_id == 324:
                #print(node.move_id)


        self.print_nodes(0x180)

        #print('{:x}'.format(unknown_regions[54] + self.pointer))
        print(self.bytes[date_address:timestamp_address])
        uniques = []
        for node in self.move_nodes:
            uniques.append(node.unknown_buton_press)
        counter = Counter(uniques)
        for key, value in sorted(counter.items()):
            print('{:x} | {}'.format(key, value))

        with open('test4.txt', 'w') as fw:
            pass
            #for node in self.move_nodes:
                #fw.write(str(node) + '\n')
            #for name in self.names:
                #fw.write(name + '\n')

        for node in self.move_nodes:
            if node.unknown_buton_press == 4:
                print(node)

    def header_line(self, line):
        bytes = self.bytes[line * 8:(line+1) * 8]
        return struct.unpack('<Q', bytes)[0] - self.pointer


    def print_nodes(self, node_id):
        for node in self.move_nodes:
            if node_id == node.move_id:
                print(node)