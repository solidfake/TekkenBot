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
from MoveDataReport import MoveDataReport

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

    def ReacquireEverything(self):
        self.needReacquireModule = True
        self.needReaquireGameState = True
        self.pid = -1

    def GetValueFromAddress(self, processHandle, address, isFloat=False, is64bit=False):
        data = c.c_ulonglong()
        bytesRead = c.c_ulonglong()
        successful = ReadProcessMemory(processHandle, address, c.byref(data), c.sizeof(data), c.byref(bytesRead))
        if not successful:
            e = GetLastError()
            print("ReadProcessMemory Error: Code " + str(e))
            self.ReacquireEverything()

        if not is64bit:
            value = int(data.value) % pow(2, 32)
        else:
            value = int(data.value)

        if not isFloat:
            return (value)
        else:
            return struct.unpack("<f", struct.pack("<I", (value)))[0]

    def GetPlayerDataFrame(self, processHandle, address):
        data = c.create_string_buffer(MemoryAddressOffsets.rollback_frame_offset.value)
        bytesRead = c.c_ulonglong(MemoryAddressOffsets.rollback_frame_offset.value)
        successful = ReadProcessMemory(processHandle, address, c.byref(data), c.sizeof(data), c.byref(bytesRead))
        if not successful:
            e = GetLastError()
            print("Getting Player Data Error: Code " + str(e))
        #print('{} : {}'.format(address, self.GetValueFromFrame(data, PlayerDataAddress.simple_move_state)))
        return data

    def GetValueFromFrame(self, frame, offset, is_player_2, is_float=False):
        address = offset
        if is_player_2:
            address += MemoryAddressOffsets.p2_data_offset.value
        bytes = frame[address: address + 4]
        if not is_float:
            return struct.unpack("<I", bytes)[0]
        else:
            return struct.unpack("<f", bytes)[0]

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

    def GetUpdatedState(self, rollback_frame = 0):
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
                print("TekkenGame-Win64-Shipping.exe not found. Likely wrong process id. Reacquiring pid.")
                self.ReacquireEverything()
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
                    if not self.needReaquireGameState:
                        print("No fight detected. Gamestate not updated.")
                    self.needReaquireGameState = True

                else:
                    last_eight_frames = []

                    second_address_base = self.GetValueFromAddress(processHandle, player_data_base_address, is64bit = True)
                    for i in range(8):  # for rollback purposes, there are 8 copies of the game state, each one updatating once every 8 frames
                        potential_second_address = second_address_base + (i * MemoryAddressOffsets.rollback_frame_offset.value)
                        potential_frame_count = self.GetValueFromAddress(processHandle, potential_second_address +  GameDataAddress.frame_count.value)
                        last_eight_frames.append((potential_frame_count, potential_second_address))

                    if rollback_frame >= len(last_eight_frames):
                        print("ERROR: requesting {} frame of {} long rollback frame".format(rollback_frame, len(last_eight_frames)))
                        rollback_frame = len(last_eight_frames) - 1

                    best_frame_count, player_data_second_address = sorted(last_eight_frames, key=lambda x: -x[0])[rollback_frame]

                    p1_bot = BotSnapshot()
                    p2_bot = BotSnapshot()

                    player_data_frame = self.GetPlayerDataFrame(processHandle, player_data_second_address)

                    for offset_enum in PlayerDataAddress:
                        #p1_value = self.GetValueFromAddress(processHandle, player_data_second_address + data.value, IsDataAFloat(data))
                        #p2_value = self.GetValueFromAddress(processHandle, player_data_second_address + MemoryAddressOffsets.p2_data_offset.value + data.value, IsDataAFloat(data))
                        p1_value = self.GetValueFromFrame(player_data_frame, offset_enum.value, False)
                        p2_value = self.GetValueFromFrame(player_data_frame, offset_enum.value, True)
                        p1_bot.player_data_dict[offset_enum] = p1_value
                        p2_bot.player_data_dict[offset_enum] = p2_value


                    game_snapshot_dict = {}
                    for offset_enum in EndBlockPlayerDataAddress:
                        game_snapshot_dict[offset_enum] = self.GetValueFromFrame(player_data_frame, offset_enum.value, False)


                    #bot_facing = self.GetValueFromAddress(processHandle, player_data_second_address + GameDataAddress.facing.value, IsDataAFloat(offset_enum))
                    bot_facing = self.GetValueFromFrame(player_data_frame, GameDataAddress.facing.value, False)


                    #for startingAddress in (PlayerDataAddress.x, PlayerDataAddress.y, PlayerDataAddress.z):
                    #    positionOffset = 32  # our xyz coordinate is 32 bytes, a 4 byte x, y, and z value followed by five 4 byte values that don't change
                    #    p1_coord_array = []
                    #    p2_coord_array = []
                    #    for i in range(16):
                    #        #p1_coord_array.append(self.GetValueFromAddress(processHandle, player_data_second_address + startingAddress.value + (i * positionOffset), True))
                    #        #p2_coord_array.append(self.GetValueFromAddress(processHandle, player_data_second_address + startingAddress.value + (i * positionOffset) + MemoryAddressOffsets.p2_data_offset.value, True))
                    #        p1_coord_array.append(self.GetValueFromFrame(player_data_frame, startingAddress.value + (i * positionOffset), False, True))
                    #        p2_coord_array.append(self.GetValueFromFrame(player_data_frame, startingAddress.value + (i * positionOffset), True, True))
                    #    p1_bot.player_data_dict[startingAddress] = p1_coord_array
                    #    p2_bot.player_data_dict[startingAddress] = p2_coord_array
                    #    #print("numpy.array([" + xyz_coord + "])")
                    ##print("--------------------")



                    if self.original_facing == None and best_frame_count > 0:
                        self.original_facing = bot_facing > 0

                    if self.needReaquireGameState:
                        print("Fight detected. Updating gamestate.")
                    self.needReaquireGameState = False

                    p1_bot.Bake()
                    p2_bot.Bake()
                    gameSnapshot = GameSnapshot(p1_bot, p2_bot, best_frame_count, bot_facing, game_snapshot_dict)
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
        self.input_counter = d[PlayerDataAddress.input_counter]
        self.input_direction = InputDirectionCodes(d[PlayerDataAddress.input_direction])
        self.input_button = InputAttackCodes(d[PlayerDataAddress.input_attack] % InputAttackCodes.xRAGE.value)
        self.rage_button_flag = d[PlayerDataAddress.input_attack] >= InputAttackCodes.xRAGE.value
        self.stun_state = StunStates(d[PlayerDataAddress.stun_type])
        self.power_crush_flag = d[PlayerDataAddress.power_crush] > 0

        cancel_window_bitmask = d[PlayerDataAddress.cancel_window]

        self.is_cancelable = (CancelStatesBitmask.CANCELABLE.value & cancel_window_bitmask) == CancelStatesBitmask.CANCELABLE.value
        self.is_bufferable = (CancelStatesBitmask.BUFFERABLE.value & cancel_window_bitmask) == CancelStatesBitmask.BUFFERABLE.value
        self.is_parry_1 = (CancelStatesBitmask.PARRYABLE_1.value & cancel_window_bitmask) == CancelStatesBitmask.PARRYABLE_1.value
        self.is_parry_2 = (CancelStatesBitmask.PARRYABLE_2.value & cancel_window_bitmask) == CancelStatesBitmask.PARRYABLE_2.value

        #self.highest_y = max(d[PlayerDataAddress.y])
        #self.lowest_y = min(d[PlayerDataAddress.y])

        self.is_jump = d[PlayerDataAddress.jump_flags] & JumpFlagBitmask.JUMP.value == JumpFlagBitmask.JUMP.value
        self.hit_outcome = HitOutcome(d[PlayerDataAddress.hit_outcome])
        self.mystery_state = d[PlayerDataAddress.mystery_state]


    def PrintYInfo(self):
        #print("h: " + str(self.highest_y) + " l: " + str(self.lowest_y) + ' d: ' + str(self.highest_y - self.lowest_y))
        print('{:.4f}, {:.4f}, {:.4f}'.format(self.highest_y, self.lowest_y, self.highest_y - self.lowest_y))

    def GetInputState(self):
        return (self.input_direction, self.input_button, self.rage_button_flag)

    def IsBlocking(self):
        return self.complex_state == ComplexMoveStates.BLOCK

    def IsGettingCounterHit(self):
        return self.hit_outcome in (HitOutcome.COUNTER_HIT_CROUCHING, HitOutcome.COUNTER_HIT_STANDING)

    def IsGettingHit(self):
        return self.stun_state == StunStates.GETTING_HIT
        #return not self.is_cancelable and self.complex_state == ComplexMoveStates.RECOVERING and self.simple_state == SimpleMoveStates.STANDING_FORWARD  and self.attack_damage == 0 and self.startup == 0 #TODO: make this more accurate

    def IsHitting(self):
        return self.stun_state in (StunStates.DOING_A_PUNISH, StunStates.DOING_THE_HITTING)

    def IsAttackMid(self):
        return self.attack_type == AttackType.MID

    def IsAttackUnblockable(self):
        return self.attack_type in {AttackType.UNBLOCKABLE_HIGH, AttackType.UNBLOCKABLE_LOW, AttackType.UNBLOCKABLE_MID}

    def IsAttackThrow(self):
        return self.throw_flag == 1

    def IsAttackLow(self):
        return self.attack_type == AttackType.LOW

    def IsInThrowing(self):
        return self.attack_type == AttackType.THROWN

    def GetActiveFrames(self):
        return self.startup_end - self.startup + 1

    def IsAttackWhiffing(self):
        return self.complex_state in {ComplexMoveStates.ATTACK_ENDING, ComplexMoveStates.STILL, ComplexMoveStates.RECOVERING, ComplexMoveStates.RECOVERING_17, ComplexMoveStates.SIDESTEP, ComplexMoveStates.MOVING_BACK_OR_FORWARD}

    def IsOnGround(self):
        return self.simple_state in {SimpleMoveStates.GROUND_FACEDOWN, SimpleMoveStates.GROUND_FACEUP}

    def IsBeingJuggled(self):
        return self.simple_state == SimpleMoveStates.JUGGLED

    def IsAirborne(self):
        return self.simple_state == SimpleMoveStates.AIRBORNE

    def IsHoldingUp(self):
        return self.input_direction == InputDirectionCodes.u

    def IsHoldingUpBack(self):
        return self.input_direction == InputDirectionCodes.ub

    def IsTechnicalCrouch(self):
        return self.simple_state in (SimpleMoveStates.CROUCH, SimpleMoveStates.CROUCH_BACK, SimpleMoveStates.CROUCH_FORWARD)

    def IsTechnicalJump(self):
        return self.is_jump
        #return self.simple_state in (SimpleMoveStates.AIRBORNE, SimpleMoveStates.AIRBORNE_26, SimpleMoveStates.AIRBORNE_24)



    def IsHoming1(self):
        return self.complex_state == ComplexMoveStates.ATTACK_STARTING_1

    def IsHoming2(self):
        return self.complex_state == ComplexMoveStates.ATTACK_STARTING_2

    def IsPowerCrush(self):
        return self.power_crush_flag

    def IsBeingKnockedDown(self):
        return self.simple_state == SimpleMoveStates.KNOCKDOWN

    def IsWhileStanding(self):
        return (self.simple_state in {SimpleMoveStates.CROUCH, SimpleMoveStates.CROUCH_BACK, SimpleMoveStates.CROUCH_FORWARD})

    def IsWallSplat(self):
        return self.move_id == 2396 or self.move_id == 2387 or self.move_id == 2380 or self.move_id == 2382 #TODO: use the wall splat states in ComplexMoveStates #move ids may be different for 'big' characters

    def IsInRage(self):
        return self.rage_flag > 0

    def IsAbleToAct(self):
        #print(self.cwb)
        return self.is_cancelable

    def IsParryable1(self):
        return self.is_parry_1

    def IsParryable2(self):
        return self.is_parry_2

    def IsBufferable(self):
        return self.is_bufferable

    def IsAttackStarting(self):
        #return self.complex_state in {ComplexMoveStates.ATTACK_STARTING_1, ComplexMoveStates.ATTACK_STARTING_2, ComplexMoveStates.ATTACK_STARTING_3, ComplexMoveStates.ATTACK_STARTING_5, ComplexMoveStates.ATTACK_STARTING_6, ComplexMoveStates.ATTACK_STARTING_7} #doesn't work on several of Kazuya's moves, maybe others
        if self.startup > 0:
            is_active = self.move_timer <= self.startup
            return is_active
        else:
            return False


class GameSnapshot:
    def __init__(self, bot, opp, frame_count, facing_bool, game_snapshot_dict):
        self.bot = bot
        self.opp = opp
        self.frame_count = frame_count
        self.facing_bool = facing_bool
        self.game_snapshot_dict = game_snapshot_dict
        self.p1_wins = game_snapshot_dict[EndBlockPlayerDataAddress.p1_wins]
        self.p2_wins = game_snapshot_dict[EndBlockPlayerDataAddress.p2_wins]
        self.timer_frames_remaining = game_snapshot_dict[EndBlockPlayerDataAddress.timer_in_frames]

    def FromMirrored(self):
        return GameSnapshot(self.opp, self.bot, self.frame_count, self.facing_bool, self.game_snapshot_dict)


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

        self.futureStateLog = None

    def Update(self):
        gameData = self.gameReader.GetUpdatedState()

        if(gameData != None):
            if len(self.stateLog) == 0 or gameData.frame_count != self.stateLog[-1].frame_count: #we don't run perfectly in sync, if we get back the same frame, throw it away
                self.duplicateFrameObtained = 0

                frames_lost = 0
                if len(self.stateLog) > 0:
                    frames_lost = gameData.frame_count - self.stateLog[-1].frame_count - 1
                    if frames_lost > 0:
                        pass
                        #print("DROPPED FRAMES: " + str(frames_lost))

                for i in range(min(7, frames_lost)):
                    #print("RETRIEVING FRAMES")
                    droppedState = self.gameReader.GetUpdatedState(min(7, frames_lost) - i)
                    self.AppendGamedata(droppedState)

                self.AppendGamedata(gameData)

                return True
            elif gameData.frame_count == self.stateLog[-1].frame_count:
                self.duplicateFrameObtained += 1
        return False

    def AppendGamedata(self, gameData):
        if not self.isMirrored:
            self.stateLog.append(gameData)
            self.mirroredStateLog.append(gameData.FromMirrored())
        else:
            self.stateLog.append(gameData.FromMirrored())
            self.mirroredStateLog.append(gameData)

        if (len(self.stateLog) > 300):
            self.stateLog.pop(0)
            self.mirroredStateLog.pop(0)

    def FlipMirror(self):
        tempLog = self.mirroredStateLog
        self.mirroredStateLog = self.stateLog
        self.stateLog = tempLog
        self.isMirrored = not self.isMirrored

    def BackToTheFuture(self, frames):
        if self.futureStateLog != None:
            raise AssertionError('Already called BackToTheFuture, need to return to the present first, Marty')
        else:
            self.futureStateLog = self.stateLog[0 - frames:]
            self.stateLog = self.stateLog[:0 - frames]

    def ReturnToPresent(self):
        if self.futureStateLog == None:
            raise AssertionError("We're already in the present, Marty, what are you doing?")
        else:
            self.stateLog += self.futureStateLog
            self.futureStateLog = None

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

    def IsBotGettingCounterHit(self):
        return self.stateLog[-1].bot.IsGettingCounterHit()

    def IsOppBlocking(self):
        return self.stateLog[-1].opp.IsBlocking()

    def IsOppGettingHit(self):
        return self.stateLog[-1].opp.IsGettingHit()

    def IsBotGettingHit(self):
        return self.stateLog[-1].bot.IsGettingHit()# or self.GetFramesSinceBotTookDamage() < 15
        #return self.GetFramesSinceBotTookDamage() < 15

    def IsOppHitting(self):
        return self.stateLog[-1].opp.IsHitting()

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
            previousState = self.stateLog[-2].bot.IsBlocking()
            currentState = self.stateLog[-1].bot.IsBlocking()
            return previousState and not currentState
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

    def GetOppMoveInterruptedFrames(self): #only finds landing canceled moves?
        if len(self.stateLog) > 3:
            if self.stateLog[-1].opp.move_timer == 1:
                interruptedFrames = self.stateLog[-2].opp.move_timer - (self.stateLog[-3].opp.move_timer + 1)
                if interruptedFrames > 0: #landing animation causes move_timer to go *up* to the end of the move
                    return interruptedFrames
        return 0

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

    def IsOppWhiffingXFramesAgo(self, framesAgo):
        if len(self.stateLog) > framesAgo:
            return self.stateLog[0 - framesAgo].opp.IsAttackWhiffing()
        else:
            return False

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

    def GetLastActiveFrameHitWasOn(self, frames):
        returnNextState = False
        for state in reversed(self.stateLog[-(frames + 2):]):
            if returnNextState:
                return (state.opp.move_timer - state.opp.startup) + 1

            if state.bot.move_timer == 1:
                returnNextState = True

        return 0

        #return self.stateLog[-1].opp.move_timer - self.stateLog[-1].opp.startup
        #elapsedActiveFrames = 0
        #opp_move_timer = -1
        #for state in reversed(self.stateLog):
            #elapsedActiveFrames += 1
            #if state.bot.move_timer == 1 or state.opp.move_timer == state.opp.startup:
                #return elapsedActiveFrames
        #return -1

    def GetOppActiveFramesXFramesAgo(self, framesAgo):
        if len(self.stateLog) > framesAgo:
            return self.stateLog[0 - framesAgo].opp.GetActiveFrames()
        else:
            return 0

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

    def GetOppDamage(self):
        return self.stateLog[-1].opp.attack_damage

    def GetMostRecentOppDamage(self):
        if self.stateLog[-1].opp.attack_damage > 0:
            return self.stateLog[-1].opp.attack_damage

        currentHealth = self.stateLog[-1].bot.damage_taken

        for state in reversed(self.stateLog):
            if state.bot.damage_taken < currentHealth:
                return currentHealth - state.bot.damage_taken
        return 0

    def GetOppLatestNonZeroStartupAndDamage(self):
        for state in reversed(self.stateLog):
            damage = state.opp.attack_damage
            startup = state.opp.startup
            if damage > 0 or startup > 0:
                return (startup, damage)
        return (0, 0)


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

    def DidBotTimerInterruptXMovesAgo(self, framesAgo):
        if len(self.stateLog) > framesAgo:
            #if self.stateLog[0 - framesAgo].bot.move_id != 32769 or self.stateLog[0 - framesAgo -1].bot.move_id != 32769:
            return self.stateLog[0 - framesAgo].bot.move_timer < self.stateLog[0 - framesAgo - 1].bot.move_timer
            #print('{} {}'.format(self.stateLog[0 - framesAgo].bot.move_timer, self.stateLog[0 - framesAgo - 1].bot.move_timer))
            #return self.stateLog[0 - framesAgo].bot.move_timer != self.stateLog[0 - framesAgo - 1].bot.move_timer + 1

        return False

    def DidBotStartGettingHitXMovesAgo(self, framesAgo):
        if len(self.stateLog) > framesAgo:
            return self.stateLog[0 - framesAgo].bot.IsGettingHit() and not self.stateLog[0 - framesAgo - 1].bot.IsGettingHit()
        else:
            return False

    def DidBotIdChangeXMovesAgo(self, framesAgo):
        if len(self.stateLog) > framesAgo:
            return self.stateLog[0 - framesAgo].bot.move_id != self.stateLog[0 - framesAgo - 1].bot.move_id
        else:
            return False

    def DidOppIdChangeXMovesAgo(self, framesAgo):
        if len(self.stateLog) > framesAgo:
            return self.stateLog[0 - framesAgo].opp.move_id != self.stateLog[0 - framesAgo - 1].opp.move_id
        else:
            return False

    def GetBotElapsedFramesOfRageMove(self, rage_move_startup):
        frozenFrames = 0
        last_move_timer = -1
        for state in reversed(self.stateLog[-rage_move_startup:]):
            if state.bot.move_timer == last_move_timer:
                frozenFrames +=1
            last_move_timer = state.bot.move_timer
        return rage_move_startup - frozenFrames



    def IsOppInRage(self):
        return self.stateLog[-1].opp.IsInRage()

    def DidOpponentUseRageRecently(self, recentlyFrames):
        if not self.IsOppInRage():
            for state in reversed(self.stateLog[-recentlyFrames:]):
                if state.opp.IsInRage():
                    return True
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

    def GetOppLastMoveInput(self):
        oppMoveId = self.stateLog[-1].opp.move_id
        input = []
        for state in reversed(self.stateLog):
            if state.opp.move_id != oppMoveId and state.opp.GetInputState()[1] != InputAttackCodes.N:
                input.append(state.opp.GetInputState())
                return input

        return [(InputDirectionCodes.N, InputAttackCodes.N, False)]

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

    def IsFulfillJumpFallbackConditions(self):
        if len(self.stateLog) > 10:
            if self.stateLog[-7].bot.IsAirborne() and self.stateLog[-7].opp.IsAirborne():
                if not self.stateLog[-8].bot.IsAirborne() or not self.stateLog[-8].opp.IsAirborne():
                    for state in self.stateLog[-10:]:
                        if not(state.bot.IsHoldingUp() or state.opp.IsHoldingUp()):
                            return False
                    return True
        return False

    def IsOppAbleToAct(self):
        return self.stateLog[-1].opp.IsAbleToAct()

    def GetBotInputState(self):
        return self.stateLog[-1].bot.GetInputState()

    def GetOppInputState(self):
        return self.stateLog[-1].opp.GetInputState()

    def GetOppTechnicalStates(self, startup):
        #opp_id = self.stateLog[-1].opp.move_id
        tc_frames = []
        tj_frames = []
        cancel_frames = []
        buffer_frames = []
        pc_frames = []
        homing_frames1 = []
        homing_frames2 = []
        parryable_frames1 = []
        parryable_frames2 = []
        startup_frames = []
        #found = False
        #for state in reversed(self.stateLog):
            #if state.opp.move_id == opp_id and not state.opp.is_bufferable:
                #found = True
        previous_state = None
        for state in reversed(self.stateLog[-startup:]):
            tc_frames.append(state.opp.IsTechnicalCrouch())
            tj_frames.append(state.opp.IsTechnicalJump())
            cancel_frames.append(state.opp.IsAbleToAct())
            buffer_frames.append(state.opp.IsBufferable())
            pc_frames.append(state.opp.IsPowerCrush())
            homing_frames1.append(state.opp.IsHoming1())
            homing_frames2.append(state.opp.IsHoming2())
            parryable_frames1.append(state.opp.IsParryable1())
            parryable_frames2.append(state.opp.IsParryable2())
            if previous_state != None:
                startup_frames.append(state.opp.move_timer != previous_state.opp.move_timer - 1)
            else:
                startup_frames.append(False)
            previous_state = state
            #elif found:
            #    break

        parryable1 = MoveDataReport('PY1', parryable_frames1)
        parryable2 = MoveDataReport('PY2', parryable_frames2)
        unparryable = MoveDataReport('NO PARRY?', [not parryable1.is_present() and not parryable2.is_present()])

        return [
            MoveDataReport('TC', tc_frames),
            MoveDataReport('TJ', tj_frames),
            MoveDataReport('BUF', buffer_frames),
            MoveDataReport('xx', cancel_frames),
            MoveDataReport('PC', pc_frames),
            MoveDataReport('HOM1', homing_frames1),
            MoveDataReport('HOM2', homing_frames2),
            MoveDataReport('SKIP', startup_frames),
            #parryable1,
            #parryable2,
            #unparryable
        ]

    def IsFightOver(self):
        return self.duplicateFrameObtained > 5

    def WasFightReset(self):
        if len(self.stateLog) > 2:
            return self.stateLog[-1].frame_count < self.stateLog[-2].frame_count
        else:
            return False

    def IsForegroundPID(self):
        return self.gameReader.IsForegroundPID()