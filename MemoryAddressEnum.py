from enum import Enum

class MemoryAddressOffsets(Enum):
    player_data_pointer_offset = 0x03362540 #pc patch 2
    #player_data_pointer_offset =  0x03360450 #pc patch 1
    #player_data_pointer_offset = 0x0337A450 #pc patch 0
    player_data_second_pointer_offset = 0

    p2_data_offset = 0x6690
    rollback_frame_offset =  0x19ef0

class GameDataAddress(Enum):
    #frame_count = 0x6a0 #resets sometimes on p1 backdash???
    frame_count = 0x6FC
    facing = 0xAB4

class PlayerDataAddress(Enum):
    x = 0xBE0
    y = 0xBE4
    z = 0xBE8

    move_id = 0x31C
    simple_move_state = 0x3D8
    stun_type = 0x3DC
    cancel_window = 0x558
    attack_type = 0x3D4
    attack_startup = 0x6680
    attack_startup_end = 0x6684
    attack_damage = 0x2FC
    complex_move_state = 0x400
    damage_taken = 0x6DC
    move_timer = 0x1f0
    recovery = 0x360
    char_id = 0xD4
    throw_flag = 0x3F8
    rage_flag = 0x988



    #raw_array_start = 0xABC #this is the raw 'buttons' pressed before they are assigned to 1,2,3,4, 1+2, etc
    input_counter = 0x14D8  #goes up one every new input state, caps at 0x27
    input_attack = 0x14DC
    input_direction = 0x14E0

    #super meter p1 0x9E4

def IsDataAFloat(dataEnum):
    return dataEnum in {PlayerDataAddress.x, PlayerDataAddress.y, PlayerDataAddress.z}