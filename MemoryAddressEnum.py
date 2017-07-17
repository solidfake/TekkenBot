from enum import Enum

class MemoryAddressOffsets(Enum):
    player_data_pointer_offset = 0x03362540 #pc patch 2
    #player_data_pointer_offset =  0x03360450 #pc patch 1
    #player_data_pointer_offset = 0x0337A450 #pc patch 0
    player_data_second_pointer_offset = 0
    p2_data_offset = 0x66B0
    p2_end_block_offset = 0xC8
    rollback_frame_offset =  0x19F70

class GameDataAddress(Enum):
    #frame_count = 0x6a0 #resets sometimes on p1 backdash???
    #frame_count = 0x70C #caps at 0xFF
    frame_count = 0x19AD0
    facing = 0xAC4
    timer_in_frames = 0x19AD8

class EndBlockPlayerDataAddress(Enum):
    round_wins = 0x19AEC
    #p2_wins = 0x19BB4
    display_combo_counter = 0x19b50
    display_combo_damage = 0x19B58
    display_juggle_damage = 0x19B5C
    total_attacks_made = 0x19B5C
    total_moves_blocked = 0x19B5C
    #p2_display_combo_counter = 0x19c18
    #p2_display_combo_damage = 0x19c20
    #p2_display_juggle_damage = 0x19c24



class PlayerDataAddress(Enum):
    char_id = 0xD4
    move_timer = 0x1f0
    attack_damage = 0x2FC
    move_id = 0x31C
    recovery = 0x360
    hit_outcome = 0x39C
    attack_type = 0x3D4
    simple_move_state = 0x3D8
    stun_type = 0x3DC
    throw_tech = 0x3EC
    throw_flag = 0x3F8
    complex_move_state = 0x400

    power_crush = 0x4f6
    jump_flags = 0x544
    cancel_window = 0x568
    damage_taken = 0x6EC

    x = 0xBF0
    y = 0xBF4
    z = 0xBF8

    health_percent = 0x11D8
    # raw_array_start = 0xABC #this is the raw 'buttons' pressed before they are assigned to 1,2,3,4, 1+2, etc
    input_counter = 0x14E8  # goes up one every new input state, caps at 0x27
    input_attack = 0x14EC
    input_direction = 0x14F0

    attack_startup = 0x66A0
    attack_startup_end = 0x66A4





    rage_flag = 0x99A

    mystery_state = 0x000

    juggle_height = 0x11D8

    #super meter p1 0x9F4




class NonPlayerDataAddressesEnum(Enum):
    OPPONENT_NAME = 1


class NonPlayerDataAddressesTuples:
    offsets = {
        NonPlayerDataAddressesEnum.OPPONENT_NAME : (0x03339C20, 0x0, 0x8, 0x114),
    }



def IsDataAFloat(dataEnum):
    return dataEnum in {PlayerDataAddress.x, PlayerDataAddress.y, PlayerDataAddress.z}

CHEAT_ENGINE_BLOCK = '<CheatEntry> <ID>{id}</ID> <Description>"{name}"</Description> <VariableType>{variable_type}</VariableType> <Address>"TekkenGame-Win64-Shipping.exe"+{base_address}</Address> <Offsets> <Offset>{offset}</Offset> <Offset>0</Offset> </Offsets> </CheatEntry>'

def PrintCheatEngineBlock(id, name, base_address, offset, data_is_float = False):
        if data_is_float:
            variable_type = 'Float'
        else:
            variable_type = '4 Bytes'
        print(CHEAT_ENGINE_BLOCK.replace('{id}', str(id)).replace('{name}', name).replace('{variable_type}', variable_type).replace('{base_address}', format(base_address, 'x')).replace('{offset}', format(offset, 'x')))

if __name__ == "__main__":
    id = 999

    for enum in MemoryAddressOffsets:
        id += 1
        if enum != MemoryAddressOffsets.player_data_pointer_offset:
            PrintCheatEngineBlock(id, enum.name, MemoryAddressOffsets.player_data_pointer_offset.value, enum.value)

    for enum in GameDataAddress:
        id += 1
        PrintCheatEngineBlock(id, enum.name, MemoryAddressOffsets.player_data_pointer_offset.value, enum.value)

    for enum in PlayerDataAddress:
        id += 1
        PrintCheatEngineBlock(id, "p1_" + enum.name, MemoryAddressOffsets.player_data_pointer_offset.value, enum.value, IsDataAFloat(enum))
        id += 1
        PrintCheatEngineBlock(id, "p2_" + enum.name, MemoryAddressOffsets.player_data_pointer_offset.value,
                              enum.value + MemoryAddressOffsets.p2_data_offset.value, IsDataAFloat(enum))

    for enum in EndBlockPlayerDataAddress:
        id += 1
        PrintCheatEngineBlock(id, "p1_" + enum.name, MemoryAddressOffsets.player_data_pointer_offset.value, enum.value,
                              IsDataAFloat(enum))
        id += 1
        PrintCheatEngineBlock(id, "p2_" + enum.name, MemoryAddressOffsets.player_data_pointer_offset.value,
                              enum.value + MemoryAddressOffsets.p2_end_block_offset.value, IsDataAFloat(enum))