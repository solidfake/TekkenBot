from enum import Enum

class AttackType(Enum):
    ANTIAIR_ONLY = 11 #Doesn't hit characters on the ground? Very rare, appears on Alisa's chainsaw stance f+2
    THROW = 10  #this is only the attack type *during* the throw animation
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

    AIRBORNE_24 = 24 #Yoshimitsu
    AIRBORNE = 25
    AIRBORNE_26 = 26 #Eliza. Chloe
    FLY = 27 #Devil Jin 3+4



class ComplexMoveStates(Enum):  #these seem difficult to pin down what they are exactly
    STILL = 0

    ATTACK_STARTING_1 = 1 #during startup this value seems to occur mainly on tracking moves
    ATTACK_STARTING_2= 2 #f+4 with Ling, extremely rare
    ATTACK_STARTING_3 = 3 #very common
    ATTACK_STARTING_4 = 4  # elisa, one of the moves in the move list, extremely rare
    ATTACK_STARTING_5 = 5  #uncommon
    ATTACK_STARTING_6 = 6  #Alisa's b+2, 1 has this, extremely rare
    ATTACK_STARTING_7 = 7 #very common

    ATTACK_ENDING = 10 #after startup  ###Kazuya's ff+3 doesn't have a startup or attack ending flag, it's just 0 the whole way through ???  ###Lili's d/b+4 doesn't have it after being blocked
    BLOCK = 11
    MOVING_BACK_OR_FORWARD = 12 #applies to dashing and walking
    SIDEROLL_GETUP = 13 #only happens after side rolling???
    SIDEROLL_STAYDOWN = 14
    SIDESTEP = 15 #left or right, also applies to juggle techs


    RECOVERING = 16 #happens after you stop walking forward or backward, jumping, getting hit, going into a stance, and some other places
    RECOVERING_17 = 17  # f+4 with Ling
    UNKNOWN_18 = 18 #King's 1+2+3+4 ki charge

    UNKNOWN_22 = 22 #Eddy move
    UNKNOWN_23 = 23 #Steve 3+4, 1

    SIDEWALK = 28 #left or right

class ThrowTechs(Enum):
    NONE = 0
    TE1 = 1 #both 1 and 2 seem to sometimes include normal throws that can be broken with either
    TE2 = 2
    TE1_2 = 3

class StunStates(Enum):
    NONE = 0
    BLOCK = 0x01000100
    GETTING_HIT = 0x100
    DOING_THE_HITTING = 0x10000
    BEING_PUNISHED = 0x10100 #One frame at the begining of a punish #Also appears during simultaneous couterhits

    BLOCK_NO_HIT = 0x1000000 #law's UF+4, sometimes???? Proximity guard maybe?

class RawCancelStates(Enum):
    STUCK = 0 #Pressing buttons doesn't do anything
    UNKNOWN_1 = 1 #1 frames occurs during Alisa's u/f 1+2 command grab, also occurs during asuka's parry escapes
    CANCELABLE = 0x00010000
    BUFFERABLE = 0x01010000 #coming out of attack for sure, probably block and hit stun too?
    UNKNOWN_2 = 2 #Alisa's d+3 and chainsaw stance moves cause this, maybe it's a conditional buffer?  Also triggers during normal throws
    MOVE_ENDING_1 = 0x00010001  # ??? 3 frames at the end of cancel window??? alisa d+2
    MOVE_ENDING_2 = 0x00010002 #??? 1 frames near the end (or at the end?) of cancelable moves
    #Theory: 1 and 2 refer to 'parryable' states, these include the active frames of moves and the throw tech windows of moves
    # the next bit is the cancelable/not cancelable bit and finally there's a 'is being buffered' bit
    #EDIT: Doesn't seem to be parryyable state. Mostly correspond to active frames, but not entirely.

class CancelStatesBitmask(Enum):
    CANCELABLE =  0x00010000
    BUFFERABLE =  0x01000000
    PARRYABLE_1 = 0x00000001
    PARRYABLE_2 = 0x00000002


#Note that this information resides on the player BEING hit not the player doing the hitting. Also note that there's no counter hit state for side or back attacks.
class HitOutcome(Enum):
    NONE = 0
    BLOCKED_STANDING = 1
    BLOCKED_CROUCHING = 2
    JUGGLE = 3
    SCREW = 4
    UNKNOWN_SCREW_5 = 5 #Xiaoyu's sample combo 3 ends with this, off-axis or right side maybe?
    UNKNOWN_6 = 6 #May not exist???
    UNKNOWN_SCREW_7 = 7 #Xiaoy's sample combo 3 includes this
    GROUNDED_FACE_DOWN= 8
    GROUNDED_FACE_UP = 9
    COUNTER_HIT_STANDING = 10
    COUNTER_HIT_CROUCHING = 11
    NORMAL_HIT_STANDING = 12
    NORMAL_HIT_CROUCHING = 13
    NORMAL_HIT_STANDING_LEFT = 14
    NORMAL_HIT_CROUCHING_LEFT = 15
    NORMAL_HIT_STANDING_BACK = 16
    NORMAL_HIT_CROUCHING_BACK = 17
    NORMAL_HIT_STANDING_RIGHT = 18
    NORMAL_HIT_CROUCHING_RIGHT = 19


class JumpFlagBitmask(Enum):
    #GROUND = 0x800000
    #LANDING_OR_STANDING = 0x810000
    JUMP = 0x820000

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




class UniversalAnimationCodes(Enum):
    NEUTRAL = 32769
    CROUCHING_NEUTRAL = 32770
