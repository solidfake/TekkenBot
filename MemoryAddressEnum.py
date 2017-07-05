from enum import Enum

class MemoryAddressOffsets(Enum):
    player_data_pointer_offset = 0x03362540 #pc patch 2
    #player_data_pointer_offset =  0x03360450 #pc patch 1
    #player_data_pointer_offset = 0x0337A450 #pc patch 0
    player_data_second_pointer_offset = 0

    p2_data_offset = 0x66B0
    rollback_frame_offset =  0x19F70

class GameDataAddress(Enum):
    #frame_count = 0x6a0 #resets sometimes on p1 backdash???
    frame_count = 0x70C
    facing = 0xAC4

class PlayerDataAddress(Enum):


    move_id = 0x31C
    simple_move_state = 0x3D8
    stun_type = 0x3DC

    attack_type = 0x3D4
    complex_move_state = 0x400
    attack_damage = 0x2FC
    move_timer = 0x1f0
    recovery = 0x360
    char_id = 0xD4
    throw_flag = 0x3F8

    cancel_window = 0x568
    damage_taken = 0x6EC

    x = 0xBF0
    y = 0xBF4
    z = 0xBF8

    # raw_array_start = 0xABC #this is the raw 'buttons' pressed before they are assigned to 1,2,3,4, 1+2, etc
    input_counter = 0x14E8  # goes up one every new input state, caps at 0x27
    input_attack = 0x14EC
    input_direction = 0x14F0

    attack_startup = 0x66A0
    attack_startup_end = 0x66A4

    rage_flag = 0x99A



    #super meter p1 0x9F4

def IsDataAFloat(dataEnum):
    return dataEnum in {PlayerDataAddress.x, PlayerDataAddress.y, PlayerDataAddress.z}

CHEAT_ENGINE_BLOCK = '<CheatEntry> <ID>{id}</ID> <Description>"{name}"</Description> <VariableType>4 Bytes</VariableType> <Address>"TekkenGame-Win64-Shipping.exe"+{base_address}</Address> <Offsets> <Offset>{offset}</Offset> <Offset>0</Offset> </Offsets> </CheatEntry>'

def PrintCheatEngineBlock(id, name, base_address, offset):
        print(CHEAT_ENGINE_BLOCK.replace('{id}', id).replace('{name}', name).replace('{base_address}', base_address).replace('{offset}', offset))

if __name__ == "__main__":

    id = 100
    for enum in PlayerDataAddress:
        id += 1
        PrintCheatEngineBlock(str(id), "p1_" + enum.name, format(MemoryAddressOffsets.player_data_pointer_offset.value, 'x' ), str(hex(enum.value)).replace('0x', ''))
        id += 1
        PrintCheatEngineBlock(str(id), "p2_" + enum.name, format(MemoryAddressOffsets.player_data_pointer_offset.value, 'x'),
                              str(hex(enum.value + MemoryAddressOffsets.p2_data_offset.value)).replace('0x', ''))
