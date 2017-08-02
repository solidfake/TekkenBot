"""
Collects information from TekkenGameState over time in hopes of synthesizing it and presenting it in a more useful way.

"""

from MoveInfoEnums import AttackType
from MoveInfoEnums import ThrowTechs
from MoveInfoEnums import ComplexMoveStates
from TekkenGameState import TekkenGameState
import time
from enum import Enum

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

        self.was_fight_being_reacquired = True
        self.is_match_recorded = False

        self.stat_filename = "TekkenData/matches.txt"
        if self.isPlayerOne:
            self.LoadStats()


    def LoadStats(self):
        self.stat_dict = {}
        self.stat_dict['char_stats'] = {}
        self.stat_dict['matchup_stats'] = {}
        self.stat_dict['opponent_stats'] = {}
        with open(self.stat_filename, 'r', encoding='utf-8') as fr:
            lines = fr.readlines()
        for line in lines:
            if '|' in line:
                args = line.split('|')
                result = args[0].strip()
                player_char = args[2].strip()
                opponent_name = args[4].strip()
                opponent_char = args[5].strip()
                self.AddStat(result, player_char, opponent_name, opponent_char)

    def AddStat(self, result, player_char, opponent_name, opponent_char):

        if not opponent_char in self.stat_dict['char_stats']:
            self.stat_dict['char_stats'][opponent_char] = [0, 0, 0]
        if not opponent_name in self.stat_dict['opponent_stats']:
            self.stat_dict['opponent_stats'][opponent_name] = [0, 0, 0]
        matchup_string = "{} vs {}".format(player_char, opponent_char)
        if not matchup_string in self.stat_dict['matchup_stats']:
            self.stat_dict['matchup_stats'][matchup_string] = [0, 0, 0]

        if 'WIN' in result:
            index = 0
        elif 'LOSS' in result:
            index = 1
        else:
            index = 2

        self.stat_dict['char_stats'][opponent_char][index] += 1
        self.stat_dict['opponent_stats'][opponent_name][index] += 1
        self.stat_dict['matchup_stats'][matchup_string][index] += 1

    def RecordFromStat(self, catagory, lookup):
        try:

            stats = self.stat_dict[catagory][lookup]
            wins = stats[0]
            losses = stats[1]
            draws= stats[2]

        except:
            wins = 0
            losses = 0
            draws = 0

        if draws <= 0:
            return "{} - {}".format(wins, losses)
        else:
            return "{} - {} - {}".format(wins, losses, draws)

    def GetPlayerString(self, reverse = False):
        if (self.isPlayerOne and not reverse) or (not self.isPlayerOne and reverse):
            return "p1: "
        else:
            return "p2: "


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
                if gameState.stateLog[-1].bot.simple_state != gameState.stateLog[-2].bot.simple_state :
                    pass
                    #print(gameState.stateLog[-1].bot.simple_state )
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
                if gameState.stateLog[-1].opp.active_xyz != gameState.stateLog[-2].opp.active_xyz:
                    pass
                    #print(gameState.stateLog[-1].opp.active_xyz)
                #for i, (h1, h2) in enumerate(zip(gameState.stateLog[-1].opp.hitboxes, gameState.stateLog[-2].opp.hitboxes)):
                #    if h1 != h2:
                #        for j, (b1, b2) in enumerate(zip(h1, h2)):
                #            if b1 != b2:
                #                print('{}, {}: {}'.format(j, i, b1))
                #        print('------')

        #self.CheckJumpFrameDataFallback(gameState)

        self.DetermineFrameData(gameState)

        self.DetermineGameStats(gameState)



        if self.isPlayerOne:
            gameState.FlipMirror()

    def DetermineGameStats(self, gameState: TekkenGameState):
        frames_ago = 4
        if self.current_game_event == None:
            if gameState.DidOppComboCounterJustStartXFramesAgo(frames_ago):
                gameState.BackToTheFuture(frames_ago)

                combo_counter_damage = gameState.GetOppComboDamageXFramesAgo(1)

                was_unblockable = gameState.IsOppAttackUnblockable()
                was_antiair = gameState.IsOppAttackAntiair()
                was_block_punish = gameState.DidBotStartGettingPunishedXFramesAgo(1)
                perfect_punish = False
                if was_block_punish:
                    perfect_punish = gameState.WasBotMoveOnLastFrameXFramesAgo(2)
                was_counter_hit = gameState.IsBotGettingCounterHit()
                was_ground_hit = gameState.IsBotGettingHitOnGround()

                was_whiff_punish = gameState.GetBotStartupXFramesAgo(2) > 0

                was_low_hit = gameState.IsOppAttackLow()
                was_mid_hit_on_crouching = gameState.IsOppAttackMid() and gameState.IsBotCrouching()
                was_throw = gameState.IsBotBeingThrown()

                was_damaged_during_attack = gameState.DidOppTakeDamageDuringStartup()



                gameState.ReturnToPresent()

                if was_unblockable:
                    hit = GameStatEventEntry.EntryType.UNBLOCKABLE
                elif was_antiair:
                    hit = GameStatEventEntry.EntryType.ANTIAIR
                elif was_throw:
                    hit = GameStatEventEntry.EntryType.THROW
                elif was_damaged_during_attack:
                    hit = GameStatEventEntry.EntryType.POWER_CRUSHED
                elif was_block_punish:
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
                else:
                    hit = GameStatEventEntry.EntryType.NO_BLOCK
                self.current_game_event = GameStatEventEntry(gameState.stateLog[-1].timer_frames_remaining, self.GetPlayerString(True), hit, combo_counter_damage)

                #print("event open")
            else:
                bot_damage_taken = gameState.DidBotJustTakeDamage(frames_ago + 1)
                if bot_damage_taken > 0:
                    #print('armored')
                    game_event = GameStatEventEntry(gameState.stateLog[-1].timer_frames_remaining, self.GetPlayerString(True), GameStatEventEntry.EntryType.ARMORED, 0) #this is probably gonna break for Yoshimitsu's self damage moves
                    game_event.close_entry(gameState.stateLog[-1].timer_frames_remaining, 1, bot_damage_taken, 0, len(self.GameEvents))

                    self.GameEvents.append(game_event)



        else:
            if gameState.DidOppComboCounterJustEndXFramesAgo(frames_ago) or gameState.WasFightReset():
                hits = gameState.GetOppComboHitsXFramesAgo(frames_ago + 1)
                damage = gameState.GetOppComboDamageXFramesAgo(frames_ago + 1)
                juggle = gameState.GetOppJuggleDamageXFramesAgo(frames_ago + 1)
                self.current_game_event.close_entry(gameState.stateLog[-1].timer_frames_remaining, hits, damage, juggle, len(self.GameEvents))
                self.GameEvents.append(self.current_game_event)
                self.current_game_event = None
                #print("event closed")





        if gameState.WasFightReset():
            #print("p1: NOW:0")
            #print("p2: NOW:0")
            if self.isPlayerOne:
                if gameState.gameReader.flagToReacquireNames == False and self.was_fight_being_reacquired:
                    self.is_match_recorded = False

                    for entry in self.get_matchup_record(gameState):
                        print(entry)


                round_number = gameState.GetRoundNumber()
                print("!ROUND | {} | HIT".format(round_number))
                if (gameState.stateLog[-1].bot.wins == 3 or gameState.stateLog[-1].opp.wins == 3) and not self.is_match_recorded:
                    self.is_match_recorded = True

                    player_name = "You"
                    p1_char_name = gameState.stateLog[-1].opp.character_name
                    p1_wins = gameState.stateLog[-1].opp.wins

                    opponent_name = gameState.stateLog[-1].opponent_name
                    p2_char_name = gameState.stateLog[-1].bot.character_name
                    p2_wins = gameState.stateLog[-1].bot.wins

                    if gameState.stateLog[-1].is_player_player_one:
                        player_char, player_wins = p1_char_name, p1_wins
                        opponent_char, opponent_wins = p2_char_name, p2_wins
                    else:
                        player_char, player_wins = p2_char_name, p2_wins
                        opponent_char, opponent_wins = p1_char_name, p1_wins

                    if player_wins == opponent_wins:
                        result = 'DRAW'
                    elif player_wins > opponent_wins:
                        result = 'WIN'
                    else:
                        result = "LOSS"

                    match_result = '{} | {} | {} | vs | {} | {} | {}-{} | {}'.format(result, player_name, player_char, opponent_name, opponent_char, player_wins, opponent_wins, time.strftime('%Y_%m_%d_%H.%M'))
                    print("{}".format(match_result))
                    self.AddStat(result, player_char, opponent_name, opponent_char)
                    with open(self.stat_filename, "a", encoding='utf-8') as fa:
                        fa.write(match_result + '\n')
            if (gameState.GetTimer(frames_ago) < 3600 and len(self.GameEvents) > 0) or True:
                summary = RoundSummary(self.GameEvents, gameState.GetOppRoundSummary(frames_ago))

            self.GameEvents = []

        self.was_fight_being_reacquired = gameState.gameReader.flagToReacquireNames

    def get_matchup_record(self, gameState):
        if gameState.stateLog[-1].is_player_player_one:
            opponent_char = gameState.stateLog[-1].bot.character_name
            player_char = gameState.stateLog[-1].opp.character_name
        else:
            opponent_char = gameState.stateLog[-1].opp.character_name
            player_char = gameState.stateLog[-1].bot.character_name
        opponent_name = gameState.stateLog[-1].opponent_name
        return [
                ("!RECORD | vs {}: {}".format(opponent_char, self.RecordFromStat('char_stats', opponent_char))),
                ("!RECORD | vs {}: {}".format(opponent_name, self.RecordFromStat('opponent_stats', opponent_name))),
                ("!RECORD | {} vs {}: {}".format(player_char, opponent_char, self.RecordFromStat("matchup_stats", "{} vs {}".format(player_char, opponent_char))))
            ]

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
        if (gameState.IsBotBlocking() or gameState.IsBotGettingHit() or gameState.IsBotBeingThrown() or gameState.IsBotBeingKnockedDown() or gameState.IsBotBeingWallSplatted()): #or  gameState.IsBotStartedBeingJuggled() or gameState.IsBotJustGrounded()):
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

                    #print(gameState.GetRangeOfMove())

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


                    prefix = self.GetPlayerString()

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
        if input[2]:
            s += "+R"
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

        ARMORED = 10

        UNBLOCKABLE = 12

        ANTIAIR = 14
        POWER_CRUSHED = 15

        #Not implemented
        LOW_PARRY = 9
        OUT_OF_THE_AIR = 13



    class PunishType(Enum):
        NONE = 0
        PERFECT = 1
        JAB = 2
        JAB_ON_LAUNCH_PUNISHIBLE = 3




    def __init__(self, time_in_frames, player_string, hit_type : EntryType, combo_counter_damage):
        self.start_time = time_in_frames
        self.player_string = player_string
        self.hit_type = hit_type
        self.damage_already_on_combo_counter = combo_counter_damage


    def close_entry(self, time_in_frames, total_hits, total_damage, juggle_damage, times_hit):
        self.end_time = time_in_frames
        self.total_hits = total_hits
        self.total_damage = max(0, total_damage - self.damage_already_on_combo_counter)
        self.juggle_damage = juggle_damage

        print('{} {} | {} | {} | {} | {} | HIT'.format(self.player_string, self.hit_type.name, self.total_damage, self.total_hits, self.start_time, self.end_time))



class RoundSummary:
    def __init__(self, events, round_variables):
        self.events = events
        self.collated_events = self.collate_events(events)
        total_damage = 0
        sources, types = self.collated_events
        #print('{} combos for {} damage'.format(types[0][0], types[0][1]))
        #print('{} pokes for {} damage'.format(types[1][0], types[1][1]))
        for event, hits, damage in sources:
            if damage > 0:
                #print('{} {} for {} damage'.format(hits, event.name, damage))
                total_damage += damage


        #print('total damage dealt {} ({})'.format(round_variables[1], total_damage))


    def collate_events(self, events):
        hits_into_juggles = 0
        hits_into_pokes = 0
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
                        hits_into_juggles += 1
                    else:
                        damage_from_pokes += event.total_damage
                        hits_into_pokes += 1
            sources.append((entry, occurances, damage))

        sources.sort(key=lambda x: x[2], reverse=True)
        types = [(hits_into_juggles, damage_from_juggles), (hits_into_pokes, damage_from_pokes)]
        return sources, types





    def __repr__(self):
        pass




