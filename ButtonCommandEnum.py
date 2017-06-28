from enum import Enum
class Command(Enum):
    Wait = 0
    TapBack = 1
    TapForward = 2
    TapDown = 3
    TapUp = 4
    TapRight = 5
    TapLeft = 6




    HoldBack = 30
    ReleaseBack = 31
    HoldDownBack = 32
    ReleaseDownBack = 33
    HoldForward = 34
    ReleaseForward = 35
    HoldDown = 36
    ReleaseDown = 37
    HoldUp = 38
    ReleaseUp = 39

    Tap1 = 101
    Tap2 = 102
    Tap3 = 103
    Tap4 = 104
    Accept = 105



    HitConfirm = 200
    PunishConfirm = 201 #we mash our punish until it comes out
    Recovery = 202 #wait until move recovers
    Nextmove = 203
    Startupmove = 204
    FullRecovery = 205


    ReleaseAll = 999