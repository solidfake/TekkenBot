"""
Collects information from TekkenGameState over time in hopes of synthesizing it and presenting it in a more useful way.

"""

from MoveInfoEnums import AttackType
from MoveInfoEnums import ThrowTechs
from MoveInfoEnums import ComplexMoveStates
from TekkenGameState import TekkenGameState
import sys


class TekkenEncyclopedia:
    def __init__(self, isPlayerOne = False, print_extended_frame_data = False):
        self.FrameData = {}
        self.GameEvents = []
        self.current_game_event = None
        self.isPlayerOne = isPlayerOne
        self.print_extended_frame_data = print_extended_frame_data

        self.active_frame_wait = 1
        self.second_opinion = False
        self.second_opinion_timer = 0
        self.stored_prefix = ""
        self.stored_opp_id = 0
        self.stored_opp_recovery = 0
        self.stored_bot_recovery = 0




    def GetFrameAdvantage(self, moveId, isOnBlock = True):
        if moveId in self.FrameData:
            if isOnBlock:
                return self.FrameData[moveId].onBlock
            else:
                return self.FrameData[moveId].onNormalHit
        else:
            return None


    #Set the dummy to jump and hold up and this prints the frame difference.
    def CheckJumpFrameDataFallback(self, gameState):
        if not self.isPlayerOne:
            if gameState.IsFulfillJumpFallbackConditions():
                print("p1 jump frame diff: " + str(gameState.GetBotMoveTimer() - gameState.GetOppMoveTimer()))

    def Update(self, gameState: TekkenGameState):
        if self.isPlayerOne:
            gameState.FlipMirror()
            #gameState.stateLog[-1].opp.PrintYInfo()
            #print(gameState.GetOppTechnicalStates())
            #print(gameState.stateLog[-1].opp.simple_state)
            #print(gameState.stateLog[-1].opp.complex_state)
            #print(gameState.stateLog[-1].bot.move_timer)
            #print(gameState.stateLog[-1].bot.recovery)

            if len(gameState.stateLog) > 2:
                if gameState.stateLog[-1].opp.complex_state != gameState.stateLog[-2].opp.complex_state:
                    pass
                    #print(gameState.stateLog[-1].opp.complex_state)
                if gameState.stateLog[-1].opp.simple_state != gameState.stateLog[-2].opp.simple_state:
                    #print(gameState.stateLog[-1].opp.simple_state)
                    pass
                if gameState.stateLog[-1].bot.move_id != gameState.stateLog[-2].bot.move_id:
                    #print(gameState.stateLog[-1].bot.move_id)
                    pass
                if gameState.stateLog[-1].opp.move_id != gameState.stateLog[-2].opp.move_id:
                    #print(gameState.stateLog[-1].opp.move_id)
                    pass
                if gameState.stateLog[-1].opp.throw_tech != gameState.stateLog[-2].opp.throw_tech:
                    pass
                    #print(gameState.stateLog[-1].opp.throw_tech)
                if gameState.stateLog[-1].bot.stun_state != gameState.stateLog[-2].bot.stun_state:
                    pass
                    #print(gameState.stateLog[-1].bot.stun_state)
                if gameState.stateLog[-1].bot.mystery_state != gameState.stateLog[-2].bot.mystery_state:
                    pass
                    #print(gameState.stateLog[-1].opp.mystery_state)
                    #print('b{}'.format(gameState.stateLog[-1].bot.mystery_state))
                if gameState.stateLog[-1].opp.mystery_state != gameState.stateLog[-2].opp.mystery_state:
                    pass
                    #print(gameState.stateLog[-1].opp.mystery_state)
                if gameState.stateLog[-1].bot.stun_state != gameState.stateLog[-2].bot.stun_state:
                    pass
                    #print('{}'.format(gameState.stateLog[-1].bot.stun_state))
                if gameState.stateLog[-1].bot.throw_tech != gameState.stateLog[-2].bot.throw_tech:
                    pass
                    #print(gameState.stateLog[-1].bot.throw_tech)

        #self.CheckJumpFrameDataFallback(gameState)

        self.DetermineFrameData(gameState)

        #self.DetermineGameStats(gameState)



        if self.isPlayerOne:
            gameState.FlipMirror()

    def DetermineGameStats(self, gameState: TekkenGameState):

        if gameState.WasFightReset():
            print(gameState.stateLog[-2].bot.damage_taken)
            summary = RoundSummary(self.GameEvents)
            self.GameEvents = []

        frames_ago = 4

        if self.current_game_event == None:
            if gameState.DidOppComboCounterJustStartXFramesAgo(frames_ago):  # if we operate slightly in the past, dropped frames are less of an issue since we recover them from the rollback log
                gameState.BackToTheFuture(frames_ago)

                was_block_punish = gameState.DidBotStartGettingPunishedXFramesAgo(1)
                was_counter_hit = gameState.IsBotGettingCounterHit()
                was_ground_hit = gameState.IsBotGettingHitOnGround()

                was_whiff_punish = gameState.GetBotStartupXFramesAgo(3) > 0

                was_low_hit = gameState.IsOppAttackLow()
                was_mid_hit_on_crouching = gameState.IsOppAttackMid() and gameState.IsBotCrouching()
                was_throw = gameState.IsBotBeingThrown()

                gameState.ReturnToPresent()

                if was_block_punish:
                    hit = GameStatEventEntry.EntryType.PUNISH
                elif was_counter_hit:
                    hit = GameStatEventEntry.EntryType.COUNTER
                elif was_ground_hit:
                    hit = GameStatEventEntry.EntryType.GROUND
                elif was_whiff_punish:
                    hit = GameStatEventEntry.EntryType.WHIFF_PUNISH
                elif was_low_hit:
                    hit = GameStatEventEntry.EntryType.LOW
                elif was_mid_hit_on_crouching:
                    hit = GameStatEventEntry.EntryType.MID
                elif was_throw:
                    hit = GameStatEventEntry.EntryType.THROW
                else:
                    hit = GameStatEventEntry.EntryType.NO_BLOCK
                self.current_game_event = GameStatEventEntry(hit)
        else:
            if gameState.DidOppComboCounterJustEndXFramesAgo(frames_ago):
                hits = gameState.GetOppComboHitsXFramesAgo(frames_ago + 1)
                damage = gameState.GetOppComboDamageXFramesAgo(frames_ago + 1)
                juggle = gameState.GetOppJuggleDamageXFramesAgo(frames_ago + 1)
                self.current_game_event.close_entry(hits, damage, juggle)
                self.GameEvents.append(self.current_game_event)
                self.current_game_event = None




    def DetermineFrameData(self, gameState):
        opp_id = gameState.GetOppMoveId()
        if self.second_opinion:
            self.second_opinion_timer += 1
            landingCanceledFrames = gameState.GetOppMoveInterruptedFrames()
            if landingCanceledFrames > 0:
                bot_recovery = (gameState.GetBotRecovery() - gameState.GetBotMoveTimer())
                opp_recovery = (gameState.GetOppRecovery() - gameState.GetOppMoveTimer())
                # fa = (self.stored_bot_recovery - self.second_opinion_timer) - opp_recovery
                if self.second_opinion_timer < self.stored_bot_recovery:
                    fa = bot_recovery - opp_recovery
                else:
                    fa = (self.stored_bot_recovery - self.second_opinion_timer) - opp_recovery
                fa_string = self.FrameData[self.stored_opp_id].WithPlusIfNeeded(fa)

                print(self.stored_prefix + "JUMP CANCELED -> " + fa_string + " NOW:" + fa_string)

                self.second_opinion = False
                self.second_opinion_timer = 0

            if self.second_opinion_timer > self.stored_opp_recovery:
                # print("check {}".format(self.stored_opp_recovery))
                # print(gameState.stateLog[-1].opp.IsBufferable())
                # print(gameState.GetOppTechnicalStates(self.stored_opp_recovery)[2])
                # print(gameState.GetOppTechnicalStates(self.stored_opp_recovery)[3])
                self.second_opinion = False
                self.second_opinion_timer = 0
        #if gameState.IsOppWhiffingXFramesAgo(self.active_frame_wait + 1)) and \
        if (gameState.IsBotBlocking() or gameState.IsBotGettingHit() or gameState.IsBotBeingThrown() or gameState.IsBotBeingKnockedDown()): #or  gameState.IsBotStartedBeingJuggled() or gameState.IsBotJustGrounded()):
            # print(gameState.stateLog[-1].bot.move_id)
            #print(gameState.stateLog[-1].bot.move_timer)
            #print(gameState.stateLog[-1].bot.recovery)
            #print(gameState.DidBotIdChangeXMovesAgo(self.active_frame_wait))

            if gameState.DidBotIdChangeXMovesAgo(self.active_frame_wait) or gameState.DidBotTimerInterruptXMovesAgo(
                    self.active_frame_wait):  # or gameState.DidOppIdChangeXMovesAgo(self.active_frame_wait):

                is_recovering_before_long_active_frame_move_completes = (gameState.GetBotRecovery() - gameState.GetBotMoveTimer() == 0)
                gameState.BackToTheFuture(self.active_frame_wait)

                #print(gameState.GetOppActiveFrames())
                if (not self.active_frame_wait >= gameState.GetOppActiveFrames() + 1) and not is_recovering_before_long_active_frame_move_completes:
                    self.active_frame_wait += 1
                else:
                    gameState.ReturnToPresent()

                    if opp_id in self.FrameData:
                        frameDataEntry = self.FrameData[opp_id]
                    else:
                        frameDataEntry = FrameDataEntry(self.print_extended_frame_data)
                        self.FrameData[opp_id] = frameDataEntry

                    frameDataEntry.currentActiveFrame = gameState.GetLastActiveFrameHitWasOn(self.active_frame_wait)

                    gameState.BackToTheFuture(self.active_frame_wait)

                    frameDataEntry.currentFrameAdvantage = '??'
                    frameDataEntry.move_id = opp_id
                    # frameDataEntry.damage =
                    frameDataEntry.damage = gameState.GetOppDamage()
                    frameDataEntry.startup = gameState.GetOppStartup()

                    if frameDataEntry.damage == 0 and frameDataEntry.startup == 0:
                        frameDataEntry.startup, frameDataEntry.damage = gameState.GetOppLatestNonZeroStartupAndDamage()

                    frameDataEntry.activeFrames = gameState.GetOppActiveFrames()
                    frameDataEntry.hitType = AttackType(gameState.GetOppAttackType()).name
                    if gameState.IsOppAttackThrow():
                        frameDataEntry.hitType += "_THROW"

                    #fastestRageMoveFrames = 120
                    #longestRageMoveFrames = 150
                    #if frameDataEntry.startup > fastestRageMoveFrames:  # and gameState.DidOpponentUseRageRecently(longestRageMoveFrames):
                        #frameDataEntry.startup = gameState.GetBotElapsedFramesOfRageMove(frameDataEntry.startup)

                    frameDataEntry.recovery = gameState.GetOppRecovery()

                    frameDataEntry.input = frameDataEntry.InputTupleToInputString(gameState.GetOppLastMoveInput())

                    frameDataEntry.technical_state_reports = gameState.GetOppTechnicalStates(frameDataEntry.startup - 1)

                    frameDataEntry.tracking = gameState.GetOppTrackingType(frameDataEntry.startup)

                    gameState.ReturnToPresent()

                    #frameDataEntry.throwTech = gameState.GetBotThrowTech(frameDataEntry.activeFrames + frameDataEntry.startup)
                    frameDataEntry.throwTech = gameState.GetBotThrowTech(1)

                    time_till_recovery_opp = gameState.GetOppFramesTillNextMove()
                    time_till_recovery_bot = gameState.GetBotFramesTillNextMove()

                    new_frame_advantage_calc = time_till_recovery_bot - time_till_recovery_opp

                    frameDataEntry.currentFrameAdvantage = frameDataEntry.WithPlusIfNeeded(new_frame_advantage_calc)

                    if gameState.IsBotBlocking():
                        frameDataEntry.onBlock = new_frame_advantage_calc
                    else:
                        if gameState.IsBotGettingCounterHit():
                            frameDataEntry.onCounterHit = new_frame_advantage_calc
                        else:
                            frameDataEntry.onNormalHit = new_frame_advantage_calc

                    frameDataEntry.hitRecovery = time_till_recovery_opp
                    frameDataEntry.blockRecovery = time_till_recovery_bot

                    if self.isPlayerOne:
                        prefix = "p1: "
                    else:
                        prefix = "p2: "

                    print(prefix + str(frameDataEntry))

                    # print(gameState.stateLog[-1].opp.startup)
                    # print(time_till_recovery_bot)

                    self.second_opinion = True
                    self.stored_bot_recovery = time_till_recovery_bot
                    self.stored_opp_recovery = time_till_recovery_opp
                    self.stored_prefix = prefix
                    self.stored_opp_id = opp_id
                    self.second_opinion_timer = 0

                    gameState.BackToTheFuture(self.active_frame_wait)

                    self.active_frame_wait = 1
                gameState.ReturnToPresent()


class FrameDataEntry:
    def __init__(self, print_extended = False):
        self.print_extended = print_extended
        self.move_id = '??'
        self.startup = '??'
        self.calculated_startup = -1
        self.hitType = '??'
        self.onBlock = '??'
        self.onCounterHit = '??'
        self.onNormalHit = '??'
        self.recovery = '??'
        self.damage = '??'
        self.blockFrames = '??'
        self.activeFrames = '??'
        self.currentFrameAdvantage = '??'
        self.currentActiveFrame = '??'
        self.input = '??'
        self.technical_state_reports = []
        self.blockRecovery = '??'
        self.hitRecovery = '??'
        self.throwTech = None
        self.tracking = ComplexMoveStates.F_MINUS

    def WithPlusIfNeeded(self, value):
        try:
            if value >= 0:
                return '+' + str(value)
            else:
                return str(value)
        except:
            return str(value)

    def InputTupleToInputString(self, inputTuple):
        s = ""
        for input in inputTuple:
            s += (input[0].name + input[1].name.replace('x', '+')).replace('N', '')
        #if input[2]:
            #s += "+RA"
        return s

    def __repr__(self):

        notes = ''

        if self.throwTech != None and self.throwTech != ThrowTechs.NONE:
            notes += self.throwTech.name + " "

        self.calculated_startup = self.startup
        for report in self.technical_state_reports:
            #if not self.print_extended:
            if 'TC' in report.name and report.is_present():
                notes += str(report)
            elif 'TJ' in report.name and report.is_present():
                notes += str(report)
            elif 'PC' in report.name and report.is_present():
                notes += str(report)
            elif 'SKIP' in report.name and report.is_present():
                #print(report)
                self.calculated_startup -= report.total_present()
            elif 'FROZ' in report.name and report.is_present():
                #print(report)
                self.calculated_startup -= report.total_present()
            elif self.print_extended:
                if report.is_present():
                    notes += str(report)
        nerd_string = ""
        if self.print_extended:
            pass
            #notes += ' stun {}'.format(self.blockRecovery)
            #notes += ' a_recovery {}'.format(self.hitRecovery)
            #notes += "Total:" + str(self.recovery) + "f "

        if self.calculated_startup != self.startup:
            self.calculated_startup = str(self.calculated_startup) + "?"

        non_nerd_string = "{:^5}|{:^8}|{:^9}|{:^8}|{:^5}|{:^5}|{:^5}|{:^3}|{:^3}|{:^3}|{:^3}|".format(
            str(self.input),
            str(self.hitType)[:7],
            str(self.calculated_startup),
            self.WithPlusIfNeeded(self.onBlock),
            self.WithPlusIfNeeded(self.onNormalHit),
            self.WithPlusIfNeeded(self.onCounterHit),
            (str(self.currentActiveFrame) + "/" + str(self.activeFrames)),
            self.tracking.name.replace('_MINUS', '-').replace("_PLUS", '+').replace(ComplexMoveStates.UNKN.name, '?'),
            self.recovery,
            self.hitRecovery,
            self.blockRecovery
        )


        notes_string = "{}".format(notes)
        now_string = " NOW:{}".format(str(self.currentFrameAdvantage))
        return non_nerd_string + notes_string + now_string


        #return "" + str(self.input).rjust(len('input')) + " |" + str(self.hitType)[:7] +  "|" + str(self.calculated_startup).center(len('startup')) + "|" + str(self.damage).center(len('  damage ')) + "| " + self.WithPlusIfNeeded(self.onBlock).center(len('block')) + "|" \
               #+ self.WithPlusIfNeeded(self.onNormalHit) +  " |" + (str(self.currentActiveFrame) + "/" + str(self.activeFrames) ).center(len(' active ')) + '| ' + notes \
               #+ " NOW:" + str(self.currentFrameAdvantage)

                #+ " Recovery: " + str(self.recovery)
                # + " Block Stun: " + str(self.blockFrames)
                #" CH: " + self.WithPlusIfNeeded(self.onCounterHit) +

from enum import Enum

class GameStatEventEntry:
    class EntryType(Enum):
        COUNTER = 1
        PUNISH = 2
        WHIFF_PUNISH = 3
        LOW = 4
        MID = 5
        THROW = 6
        GROUND = 7
        NO_BLOCK = 8


        #Not implemented
        LOW_PARRY = 9
        ARMORED = 10
        CRUSHED = 11
        UNBLOCKABLE = 12
        OUT_OF_THE_AIR = 13



    def __init__(self, hit_type : EntryType):
        self.hit_type = hit_type

    def close_entry(self, total_hits, total_damage, juggle_damage):
        self.total_hits = total_hits
        self.total_damage = total_damage
        self.juggle_damage = juggle_damage



class RoundSummary:
    def __init__(self, events):
        self.events = events
        self.collated_events = self.collate_events(events)
        print(self.collated_events)


    def collate_events(self, events):
        damage_from_juggles = 0
        damage_from_pokes = 0
        sources = []

        for entry in GameStatEventEntry.EntryType:
            occurances = 0
            damage = 0
            for event in events:
                if entry == event.hit_type:
                    occurances += 1
                    damage += event.total_damage
                    if event.juggle_damage > 0:
                        damage_from_juggles += event.total_damage
                    else:
                        damage_from_pokes += event.total_damage
            sources.append((entry, occurances, damage))

        sources.sort(key=lambda x: x[2], reverse=True)
        return sources





    def __repr__(self):
        pass




