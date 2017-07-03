from enum import Enum

class AttackType(Enum):
    ANTIAIR_ONLY = 11 #Doesn't hit characters on the ground? Very rare, appears on Alisa's chainsaw stance f+2
    THROW_ANIM = 10  #this is only the attack type *during* the throw animation
    LOW_UNBLOCKABLE = 9 #Yoshimitsu's 10 hit combo 2 has one
    HIGH_UNBLOCKABLE = 8  #Akuma's focus attack
    MID_UNBLOCKABLE = 7
    #UNKNOWN_6 = 6 #????? may not exist
    HIGH = 5
    SMID = 4
    PROJ = 3 #Also on Akuma's dps and one of King's throws. Shows as a special mid in practice mode, unknown what properties this has that are different than smid
    MID = 2
    LOW = 1
    NA = 0 #This move is not an attack


class SimpleMoveStates(Enum):
    UNINITIALIZED = 0

    STANDING_FORWARD = 1
    STANDING_BACK = 2
    STANDING = 3



    CROUCH_FORWARD = 5
    CROUCH_BACK = 6
    CROUCH = 7

    UNKNOWN_TYPE_9 = 9 #seen on Ling

    GROUND_FACEUP = 12
    GROUND_FACEDOWN = 13

    JUGGLED = 14
    KNOCKDOWN = 15




    #THE UNDERSTANDING OF THE FOLLOWING VALUES IS NOT COMPLETE


    OFF_AXIS_GETUP = 8

    UNKNOWN_10 = 10 #Yoshimitsu
    UNKNOWN_GETUP_11 = 11

    WALL_SPLAT_18 = 18
    WALL_SPLAT_19 = 19
    FLOOR_BREAK_BOUNCE_20 = 20  #??? not sure on this one

    UNKNOWN_23 = 23 #Kuma

    UNKNOWN_24 = 24 #Yoshimitsu
    AIRBORNE = 25
    UNKNOWN_26 = 26 #Eliza
    FLY = 27 #Devil Jin 3+4



class ComplexMoveStates(Enum):  #these seem difficult to pin down what they are exactly
    STILL = 0

    ATTACK_STARTING_1 = 1 #during startup
    ATTACK_STARTING_2= 2 #f+4 with Ling
    ATTACK_STARTING_3 = 3 #during startup
    ATTACK_STARTING_4 = 4  # elisa, one of the moves in the move list
    ATTACK_STARTING_5 = 5  #inferred but not tested, with Ling
    ATTACK_STARTING_6 = 6  #Alisa's b+2, 1 has this
    ATTACK_STARTING_7 = 7 #some moves have 7 instead of 3 or

    ATTACK_ENDING = 10 #after startup  ###Kazuya's ff+3 doesn't have a startup or attack ending flag, it's just 0 the whole way through ???  ###Lili's d/b+4 doesn't have it after being blocked
    BLOCK = 11
    MOVING_BACK_OR_FORWARD = 12 #applies to dashing and walking
    SIDEROLL_GETUP = 13 #only happens after side rolling???
    SIDEROLL_STAYDOWN = 14
    SIDESTEP = 15 #left or right, also applies to juggle techs


    RECOVERING = 16 #happens after you stop walking forward or backward, jumping, getting hit, going into a stance, and some other places
    RECOVERING_17 = 17  # f+4 with Ling

    UNKNOWN_22 = 22 #Eddy move
    UNKNOWN_23 = 23 #Steve 3+4, 1

    SIDEWALK = 28 #left or right

class InputDirectionCodes(Enum):
    FIGHT_START = 0

    N = 32

    u = 256
    ub = 128
    uf = 512

    f = 64
    b = 16

    d = 4
    df = 8
    db = 2

class InputAttackCodes(Enum):
    N = 0
    x1 = 512
    x2 = 1024
    x3 = 2048
    x4 = 4096
    x1x2 = 1536
    x1x3 = 2560
    x1x4 = 4608
    x2x3 = 3072
    x2x4 = 5120
    x3x4 = 6144
    x1x2x3 = 3584
    x1x2x4 = 5632
    x1x3x4 = 6656
    x2x3x4 = 7168
    x1x2x3x4 = 7680
    xRAGE = 8192



