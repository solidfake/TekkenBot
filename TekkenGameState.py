"""
This module's classes are responsible for reading and interpreting the memory of a Tekken7.exe proecess.

TekkenGameReader reads the memory of Tekken7.exe, extracts information about the state of the game, then saves a
'snapshot' of each frame.

Each GameSnapshot has 2 BotSnapshots, together encapsulating the information of both players and shared data for a single game frame.

TekkenGameState saves these snapshots and provides an api that abstracts away the difference
between questions that query one player (is player 1 currently attacking?), both players (what is the expected frame
advantage when player 2 emerges from block), or multiple game states over time (did player 1 just begin to block this
frame?, what was the last move player 2 did?).

"""


import ctypes as c
from ctypes import wintypes as w
import struct
import math

import ModuleEnumerator
import PIDSearcher
from MoveInfoEnums import *
from MemoryAddressEnum import *
from ConfigReader import ConfigReader

#player_data_pointer_offset = 0x03360450 #pc patch 1
#player_data_pointer_offset = 0x0337A450 #pc patch 0

#charSelectValue = ("char_select", 0x03338618, 0x3CC, False)


#p2 values are 0x6690 more than p1 values
#input buffer at 0x714C???

k32 = c.windll.kernel32

OpenProcess = k32.OpenProcess
OpenProcess.argtypes = [w.DWORD,w.BOOL,w.DWORD]
OpenProcess.restype = w.HANDLE

ReadProcessMemory = k32.ReadProcessMemory
ReadProcessMemory.argtypes = [w.HANDLE,w.LPCVOID,w.LPVOID,c.c_size_t,c.POINTER(c.c_size_t)]
ReadProcessMemory.restype = w.BOOL

GetLastError = k32.GetLastError
GetLastError.argtypes = None
GetLastError.restype = w.DWORD

CloseHandle = k32.CloseHandle
CloseHandle.argtypes = [w.HANDLE]
CloseHandle.restype = w.BOOL


class TekkenGameReader:
    def __init__(self):
        self.pid = -1
        self.needReaquireGameState = True
        self.needReacquireModule = True
        self.module_address = 0
        self.original_facing = None
        self.config_reader = ConfigReader('memory_address')
        self.player_data_pointer_offset = self.config_reader.get_property('player_data_pointer_offset', MemoryAddressOffsets.player_data_pointer_offset.value, lambda x: int(x, 16))

    def GetValueFromAddress(self, processHandle, address, isFloat=False, is64bit=False):
        data = c.c_ulonglong()
        bytesRead = c.c_ulonglong()
        successful = ReadProcessMemory(processHandle, address, c.byref(data), c.sizeof(data), c.byref(bytesRead))
        if not successful:
            e = GetLastError()
            print("ReadProcessMemory Error: Code " + str(e))
            self.needReacquireModule = True
            self.needReaquireGameState = True
            self.pid = -1

        if not is64bit:
            value = int(data.value) % pow(2, 32)
        else:
            value = int(data.value)

        if not isFloat:
            return (value)
        else:
            return struct.unpack("<f", struct.pack("<I", (value)))[0]

    def IsForegroundPID(self):
        pid = c.wintypes.DWORD()
        active = c.windll.user32.GetForegroundWindow()
        active_window = c.windll.user32.GetWindowThreadProcessId(active, c.byref(pid))
        return pid.value == self.pid

    def GetWindowRect(self):
        if self.IsForegroundPID():
            rect = c.wintypes.RECT()
            c.windll.user32.GetWindowRect(c.windll.user32.GetForegroundWindow(), c.byref(rect))
            return rect
        else:
            return None

    def HasWorkingPID(self):
        return self.pid > -1

    def GetUpdatedState(self):
        gameSnapshot = None

        if not self.HasWorkingPID():
            self.pid = PIDSearcher.GetPIDByName(b'TekkenGame-Win64-Shipping.exe')
            if self.HasWorkingPID():
                print("Tekken pid acquired: " + str(self.pid))
            else:
                print("Tekken pid not acquired. Trying to acquire...")

            return gameSnapshot

        if (self.needReacquireModule):
            print("Trying to acquire Tekken library in pid: " + str(self.pid))
            self.module_address = ModuleEnumerator.GetModuleAddressByPIDandName(self.pid, 'TekkenGame-Win64-Shipping.exe')
            if self.module_address == None:
                print("TekkenGame-Win64-Shipping.exe not found. Likely wrong process id.")
            elif(self.module_address != 0x140000000):
                print("Unrecognized location for TekkenGame-Win64-Shipping.exe module. Tekken.exe Patch? Wrong process id?")
            else:
                print("Found TekkenGame-Win64-Shipping.exe")
                self.needReacquireModule = False

        if self.module_address != None:
            processHandle = OpenProcess(0x10, False, self.pid)
            try:
                player_data_base_address = self.GetValueFromAddress(processHandle, self.module_address + self.player_data_pointer_offset, is64bit = True)
                if player_data_base_address == 0:
                    print("No fight detected. Gamestate not updated.")
                    self.needReaquireGameState = True

                else:
                    player_data_second_address = 0
                    best_frame_count = -1
                    second_address_base = self.GetValueFromAddress(processHandle, player_data_base_address, is64bit = True)
                    for i in range(8):  # for rollback purposes, there are 8 copies of the game state, each one updatating once every 8 frames
                        potential_second_address = second_address_base + (i * MemoryAddressOffsets.rollback_frame_offset.value)
                        potential_frame_count = self.GetValueFromAddress(processHandle, potential_second_address +  GameDataAddress.frame_count.value)
                        if potential_frame_count > best_frame_count:
                            player_data_second_address = potential_second_address
                            best_frame_count = potential_frame_count

                    p1_bot = BotSnapshot()
                    p2_bot = BotSnapshot()

                    for data in PlayerDataAddress:
                        p1_value = self.GetValueFromAddress(processHandle, player_data_second_address + data.value, IsDataAFloat(data))
                        p2_value = self.GetValueFromAddress(processHandle, player_data_second_address + MemoryAddressOffsets.p2_data_offset.value + data.value, IsDataAFloat(data))
                        p1_bot.player_data_dict[data] = p1_value
                        p2_bot.player_data_dict[data] = p2_value

                    bot_facing = self.GetValueFromAddress(processHandle, player_data_second_address + GameDataAddress.facing.value, IsDataAFloat(data))

                    #positionArrays = {}
                    #for startingAddress in valuesOfPositionArrays:
                    #    positionArrays[startingAddress[0]] = []
                    #    for i in range(16):
                    #        positionOffset = 32 #our xyz coordinate is 32 bytes, a 4 byte x, y, and z value followed by five 4 byte values that don't change
                    #        positionArrays[startingAddress[0]].append(TekkenGameReader.GetValueFromAddress(processHandle, player_data_second_address + startingAddress[1] + (i * positionOffset), startingAddress[2]))

                    #for key in positionArrays:
                    #    positionArray = positionArrays[key]
                    #    gameData[key] = sum(positionArray)/float(len(positionArray))

                    if self.original_facing == None and best_frame_count > 0:
                        self.original_facing = bot_facing > 0

                    self.needReaquireGameState = False

                    p1_bot.Bake()
                    p2_bot.Bake()
                    gameSnapshot = GameSnapshot(p1_bot, p2_bot, best_frame_count, bot_facing)
            finally:
                CloseHandle(processHandle)

        return gameSnapshot


    def GetNeedReacquireState(self):
        return self.needReaquireGameState

class BotSnapshot:

    def __init__(self):
        self.player_data_dict = {}

    def Bake(self):
        d = self.player_data_dict
        self.xyz = (d[PlayerDataAddress.x], d[PlayerDataAddress.y], d[PlayerDataAddress.z])
        self.move_id = d[PlayerDataAddress.move_id]
        self.simple_state = SimpleMoveStates(d[PlayerDataAddress.simple_move_state])
        self.attack_type = AttackType(d[PlayerDataAddress.attack_type])
        self.startup = d[PlayerDataAddress.attack_startup]
        self.startup_end = d[PlayerDataAddress.attack_startup_end]
        self.attack_damage = d[PlayerDataAddress.attack_damage]
        self.complex_state = ComplexMoveStates(d[PlayerDataAddress.complex_move_state])
        self.damage_taken = d[PlayerDataAddress.damage_taken]
        self.move_timer = d[PlayerDataAddress.move_timer]
        self.recovery = d[PlayerDataAddress.recovery]
        self.char_id = d[PlayerDataAddress.char_id]
        self.throw_flag = d[PlayerDataAddress.throw_flag]
        self.rage_flag = d[PlayerDataAddress.rage_flag]

    def IsBlocking(self):
        return self.complex_state == ComplexMoveStates.BLOCK

    def IsGettingHit(self):
        return self.complex_state == ComplexMoveStates.RECOVERING and self.simple_state == SimpleMoveStates.STANDING_FORWARD #TODO: make this more accurate

    def IsAttackMid(self):
        return self.attack_type == AttackType.MID

    def IsAttackUnblockable(self):
        return self.attack_type in {AttackType.UNBLOCKABLE_HIGH, AttackType.UNBLOCKABLE_LOW, AttackType.UNBLOCKABLE_MID}

    def IsAttackThrow(self):
        return self.throw_flag == 1

    def IsAttackLow(self):
        return self.attack_type == AttackType.LOW

    def IsInThrowing(self):
        return self.attack_type == AttackType.THROW_TECH

    def GetActiveFrames(self):
        return self.startup_end - self.startup + 1

    def IsAttackWhiffing(self):
        return self.complex_state in {ComplexMoveStates.ATTACK_ENDING, ComplexMoveStates.STILL, ComplexMoveStates.RECOVERING, ComplexMoveStates.RECOVERING_17, ComplexMoveStates.SIDESTEP, ComplexMoveStates.MOVING_BACK_OR_FORWARD}

    def IsOnGround(self):
        return self.simple_state in {SimpleMoveStates.GROUND_FACEDOWN, SimpleMoveStates.GROUND_FACEUP}

    def IsBeingJuggled(self):
        return self.simple_state == SimpleMoveStates.JUGGLED

    def IsBeingKnockedDown(self):
        return self.simple_state == SimpleMoveStates.KNOCKDOWN

    def IsWhileStanding(self):
        return (self.simple_state in {SimpleMoveStates.CROUCH, SimpleMoveStates.CROUCH_BACK, SimpleMoveStates.CROUCH_FORWARD}) or (self.IsBlocking() and self.simple_state == SimpleMoveStates.STANDING_FORWARD)

    def IsWallSplat(self):
        return self.move_id == 2396 or self.move_id == 2387 or self.move_id == 2380 or self.move_id == 2382 #TODO: use the wall splat states in ComplexMoveStates #move ids may be different for 'big' characters

    def IsAttackStarting(self):
        #return self.complex_state in {ComplexMoveStates.ATTACK_STARTING_1, ComplexMoveStates.ATTACK_STARTING_2, ComplexMoveStates.ATTACK_STARTING_3, ComplexMoveStates.ATTACK_STARTING_5, ComplexMoveStates.ATTACK_STARTING_6, ComplexMoveStates.ATTACK_STARTING_7} #doesn't work on several of Kazuya's moves, maybe others
        if self.startup > 0:
            is_active = self.move_timer <= self.startup
            return is_active
        else:
            return False


class GameSnapshot:
    def __init__(self, bot, opp, frame_count, facing_bool):
        self.bot = bot
        self.opp = opp
        self.frame_count = frame_count
        self.facing_bool = facing_bool

    def FromMirrored(self):
        return GameSnapshot(self.opp, self.bot, self.frame_count, self.facing_bool)


    def GetDist(self):
        return math.hypot(self.bot.xyz[0] - self.opp.xyz[0], self.bot.xyz[2] - self.opp.xyz[2])



class TekkenGameState:
    def __init__(self):
        self.gameReader = TekkenGameReader()
        self.isPlayer1 = True

        self.duplicateFrameObtained = 0
        self.stateLog = []
        self.mirroredStateLog = []

        self.isMirrored = False

    def Update(self):
        gameData = self.gameReader.GetUpdatedState()

        if(gameData != None):
            if len(self.stateLog) == 0 or gameData.frame_count != self.stateLog[-1].frame_count or gameData.frame_count == 65535: #we don't run perfectly in sync, if we get back the same frame, throw it away
                self.duplicateFrameObtained = 0
                if gameData.frame_count == 65535:
                    print("PRACTICE TIME LIMIT EXCEEDED. PLEASE RESTART OR RESET PRACTICE.")
                    self.duplicateFrameObtained = 9999

                if not self.isMirrored:
                    self.stateLog.append(gameData)
                    self.mirroredStateLog.append(gameData.FromMirrored())
                else:
                    self.stateLog.append(gameData.FromMirrored())
                    self.mirroredStateLog.append(gameData)

                if (len(self.stateLog) > 300):
                    self.stateLog.pop(0)
                    self.mirroredStateLog.pop(0)
                return True
            elif gameData.frame_count == self.stateLog[-1].frame_count:
                self.duplicateFrameObtained += 1
        return False

    def FlipMirror(self):
        tempLog = self.mirroredStateLog
        self.mirroredStateLog = self.stateLog
        self.stateLog = tempLog
        self.isMirrored = not self.isMirrored

    def IsGameHappening(self):
        return not self.gameReader.GetNeedReacquireState()

    def IsBotOnLeft(self):
        isPlayerOneOnLeft = self.gameReader.original_facing == self.stateLog[-1].facing_bool
        if not self.isMirrored:
            return isPlayerOneOnLeft
        else:
            return not isPlayerOneOnLeft

    def GetDist(self):
        return self.stateLog[-1].GetDist()

    def IsBotBlocking(self):
        return self.stateLog[-1].bot.IsBlocking()

    def IsOppBlocking(self):
        return self.stateLog[-1].opp.IsBlocking()

    def IsOppGettingHit(self):
        return self.stateLog[-1].opp.IsGettingHit()

    def IsBotGettingHit(self):
        return self.GetFramesSinceBotTookDamage() < 15

    def IsBotStartedGettingHit(self):
        if len(self.stateLog) > 2:
            return self.IsBotGettingHit() and not self.stateLog[-2].bot.IsGettingHit()
        else:
            return False

    def IsBotStartedBeingThrown(self):
        if len(self.stateLog) > 2:
            return self.IsBotBeingThrown() and not self.stateLog[-2].opp.IsInThrowing()
        else:
            return False

    def IsBotComingOutOfBlock(self):
        if(len(self.stateLog) >= 2):
            previousState = self.stateLog[-2].bot.block_flags
            currentState = self.stateLog[-1].bot.block_flags
            return previousState == 11 and currentState != 11
        else:
            return False

    def GetRecoveryOfMoveId(self, moveID):
        largestTime = -1
        for state in reversed(self.stateLog):
            if(state.bot.move_id == moveID):
                largestTime = max(largestTime, state.bot.move_timer)
        return largestTime

    def GetLastMoveID(self):
        for state in reversed(self.stateLog):
            if(state.bot.startup > 0):
                return state.bot.move_id
        return -1

    def GetBotJustMoveID(self):
        return self.stateLog[-2].bot.move_id

    def DidBotRecentlyDoMove(self):
        if len(self.stateLog) > 5:
            return self.stateLog[-1].bot.move_timer < self.stateLog[-5].bot.move_timer
        else:
            return False

    def DidBotRecentlyDoDamage(self):
        if len(self.stateLog) > 10:
            if self.stateLog[-1].opp.damage_taken > self.stateLog[-20].opp.damage_taken:
                return True
        return False

    def IsOppAttackMid(self):
        return self.stateLog[-1].opp.IsAttackMid()

    def IsOppAttackUnblockable(self):
        return self.stateLog[-1].opp.IsAttackUnblockable()

    def IsOppAttackThrow(self):
        return self.stateLog[-1].opp.IsAttackThrow()

    def IsOppAttackLow(self):
        return self.stateLog[-1].opp.IsAttackLow()

    def IsOppAttacking(self):
        return self.stateLog[-1].opp.IsAttackStarting()

    def GetFramesUntilOutOfBlock(self):
        #print(self.stateLog[-1].bot.block_flags)
        if not self.IsBotBlocking():
            return 0
        else:
            recovery = self.stateLog[-1].bot.recovery
            blockFrames = self.GetFramesBotHasBeenBlockingAttack()
            return (recovery ) - blockFrames



    def GetFrameProgressOfOppAttack(self):
        mostRecentStateWithAttack = None
        framesSinceLastAttack = 0
        for state in reversed(self.stateLog):
            if mostRecentStateWithAttack == None:
                if state['p2_attack_startup'] > 0:
                    mostRecentStateWithAttack = state
            elif (state['p2_move_id'] == mostRecentStateWithAttack.opp.move_id) and (state.opp.move_timer < mostRecentStateWithAttack.opp.move_timer):
                framesSinceLastAttack += 1
            else:
                break
        return framesSinceLastAttack

    def GetFramesBotHasBeenBlockingAttack(self):
        if not self.stateLog[-1].bot.IsBlocking():
            return 0
        else:
            opponentMoveId = self.stateLog[-1].opp.move_id
            opponentMoveTimer = self.stateLog[-1].opp.move_timer

            framesSpentBlocking = 0
            for state in reversed(self.stateLog):
                #print(state.opp.move_timer)
                #print(state.opp.move_id)
                #print(opponentMoveId)
                if state.bot.IsBlocking() and (state.opp.move_timer <= opponentMoveTimer) and (state.opp.move_id == opponentMoveId) and state.opp.move_timer > state.opp.startup:
                    framesSpentBlocking += 1
                    opponentMoveTimer = state.opp.move_timer
                else:
                    break
            #print(framesSpentBlocking)
            return framesSpentBlocking


    def IsOppWhiffing(self):
        return self.stateLog[-1].opp.IsAttackWhiffing()

    def IsBotWhiffing(self):
        return self.stateLog[-1].bot.IsAttackWhiffing()

    def IsBotWhileStanding(self):
        return self.stateLog[-1].bot.IsWhileStanding()

    def GetBotFramesUntilRecoveryEnds(self):
        return (self.stateLog[-1].bot.recovery) - (self.stateLog[-1].bot.move_timer)


    def IsBotMoveChanged(self):
        if (len(self.stateLog) > 2):
            return self.stateLog[-1].bot.move_id != self.stateLog[-2].bot.move_id
        else:
            return False

    def IsBotWhiffingAlt(self):
        currentBot = self.stateLog[-1].bot
        if currentBot.startup == 0: #we might still be in recovery
            for i, state in enumerate(reversed(self.stateLog)):
                if state.bot.startup > 0:
                    pass
        else:
            return currentBot.IsAttackWhiffing()

    def GetOpponentMoveIDWithCharacterMarker(self):
        characterMarker = self.stateLog[-1].opp.char_id
        return (self.stateLog[-1].opp.move_id + (characterMarker * 10000000))

    def GetOppStartup(self):
        return self.stateLog[-1].opp.startup

    def GetOppActiveFrames(self):
        return self.stateLog[-1].opp.GetActiveFrames()

    def GetOppRecovery(self):
        return self.stateLog[-1].opp.recovery

    def GetBotRecovery(self):
        return self.stateLog[-1].bot.recovery

    def GetOppMoveId(self):
        return self.stateLog[-1].opp.move_id

    def GetOppAttackType(self):
        return self.stateLog[-1].opp.attack_type

    def GetBotMoveId(self):
        return self.stateLog[-1].bot.move_id

    def GetBotStartup(self):
        return self.stateLog[-1].bot.startup

    def GetBotMoveTimer(self):
        return self.stateLog[-1].bot.move_timer

    def GetOppMoveTimer(self):
        return self.stateLog[-1].opp.move_timer

    def IsBotAttackStarting(self):
        return (self.GetBotStartup() - self.GetBotMoveTimer()) > 0

    def GetOppTimeUntilImpact(self):
        return self.GetOppStartup() - self.stateLog[-1].opp.move_timer + self.stateLog[-1].opp.GetActiveFrames()

    def GetBotTimeUntilImpact(self):
        return self.GetBotStartup() - self.stateLog[-1].bot.move_timer + self.stateLog[-1].bot.GetActiveFrames()

    def IsBotOnGround(self):
        return self.stateLog[-1].bot.IsOnGround()

    def IsBotBeingKnockedDown(self):
        return self.stateLog[-1].bot.IsBeingKnockedDown()

    def GetMostRecentOppDamage(self):
        if self.stateLog[-1].opp.attack_damage > 0:
            return self.stateLog[-1].opp.attack_damage

        currentHealth = self.stateLog[-1].bot.damage_taken

        for state in reversed(self.stateLog):
            if state.bot.damage_taken < currentHealth:
                return currentHealth - state.bot.damage_taken
        return 0

    def IsBotJustGrounded(self):
        if (len(self.stateLog) > 2):
            return self.stateLog[-1].bot.IsOnGround() and not self.stateLog[-2].bot.IsOnGround() and not self.stateLog[-2].bot.IsBeingJuggled() and not self.stateLog[-2].bot.IsBeingKnockedDown()
        else:
            return False

    def IsBotBeingJuggled(self):
        return self.stateLog[-1].bot.IsBeingJuggled()

    def IsBotStartedBeingJuggled(self):
        if (len(self.stateLog) > 2):
            return self.stateLog[-1].bot.IsBeingJuggled() and not self.stateLog[-2].bot.IsBeingJuggled()
        else:
            return False

    def IsBotBeingThrown(self):
        return self.stateLog[-1].opp.IsInThrowing()

    def IsOppWallSplat(self):
        return self.stateLog[-1].opp.IsWallSplat()

    def DidBotJustTakeDamage(self):
        if(len(self.stateLog) > 2):
            return self.stateLog[-1].bot.damage_taken > self.stateLog[-2].bot.damage_taken
        else:
            return False

    def DidBotTimerReduceXMovesAgo(self, framesAgo):
        if len(self.stateLog) > framesAgo:
            return self.stateLog[0 - framesAgo].bot.move_timer < self.stateLog[0 - framesAgo - 1].bot.move_timer
        else:
            return False

    def DidBotIdChangeXMovesAgo(self, framesAgo):
        if len(self.stateLog) > framesAgo:
            return self.stateLog[0 - framesAgo].bot.move_id != self.stateLog[0 - framesAgo - 1].bot.move_id
        else:
            return False



    def GetFramesSinceBotTookDamage(self):
        damage_taken = self.stateLog[-1].bot.damage_taken
        for i, state in enumerate(reversed(self.stateLog)):
            if state.bot.damage_taken < damage_taken:
                return i
        return 1000

    def GetLastOppSnapshotWithDifferentMoveId(self):
        moveId = self.stateLog[-1].opp.move_id
        for state in reversed(self.stateLog):
            if state.opp.move_id != moveId:
                return state
        return self.stateLog[-1]

    def GetLastOppWithDifferentMoveId(self):
        return self.GetLastOppSnapshotWithDifferentMoveId().opp

    def GetFrameDataOfCurrentOppMove(self):
        if self.stateLog[-1].opp.startup > 0:
            opp = self.stateLog[-1].opp
        else:
            gameState = self.GetLastOppSnapshotWithDifferentMoveId()
            if gameState != None:
                opp = gameState.opp
            else:
                opp = self.stateLog[-1].opp
        return self.GetFrameData(self.stateLog[-1].bot, opp)


    def GetFrameDataOfCurrentBotMove(self):
        return self.GetFrameData(self.stateLog[-1].opp, self.stateLog[-1].bot)

    def GetFrameData(self, defendingPlayer, attackingPlayer):
        return (defendingPlayer.recovery + attackingPlayer.startup) - attackingPlayer.recovery

    def GetBotCharId(self):
        char_id = self.stateLog[-1].bot.char_id
        #if -1 < char_id < 50:
        print("Character: " + str(char_id))
        return char_id

    def IsFightOver(self):
        return self.duplicateFrameObtained > 5

    def WasFightReset(self):
        if len(self.stateLog) > 2:
            return self.stateLog[-1].frame_count < self.stateLog[-2].frame_count
        else:
            return False

    def IsForegroundPID(self):
        return self.gameReader.IsForegroundPID()