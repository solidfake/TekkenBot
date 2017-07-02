"""
Collects information from TekkenGameState over time in hopes of synthesizing it and presenting it in a more useful way.

"""

from MoveInfoEnums import AttackType
from TekkenGameState import TekkenGameState
import sys

class TekkenEncyclopedia:
    def __init__(self, isPlayerOne = False):
        self.FrameData = {}
        self.isPlayerOne = isPlayerOne
        self.active_frame_wait = 1
        self.second_opinion = False
        self.second_opinion_timer = 0
        self.stored_opp_recovery = 0
        self.stored_bot_recovery = 0
        self.stored_opp_fa = 0
        self.stored_frame_data = ""
        self.stored_prefix = ""
        self.stored_opp_id = 0

    def GetFrameAdvantage(self, moveId, isOnBlock = True):
        if moveId in self.FrameData:
            if isOnBlock:
                return self.FrameData[moveId].onBlock
            else:
                return self.FrameData[moveId].onNormalHit
        else:
            return None



    def Update(self, gameState: TekkenGameState):
        if self.isPlayerOne:
            gameState.FlipMirror()


        opp_id = gameState.GetOppMoveId()

        #if self.isPlayerOne:
            #print(gameState.GetOppMoveTimer())


        interruptedFrames = gameState.IsOppMoveInterrupted()
        if (interruptedFrames > 0):
            pass
            #gameState.BackToTheFuture(1)
            #print("MOVE INTERRUPTED ADJUST BY: " + str(interruptedFrames))
            #print("New Recovery is off by: " + str( self.stored_opp_fa - ((gameState.GetOppRecovery() - gameState.GetOppMoveTimer()) - self.stored_opp_recovery)))
            #gameState.ReturnToPresent()

        if self.second_opinion:
            self.second_opinion_timer += 1
            if interruptedFrames > 0:
                bot_recovery = (gameState.GetBotRecovery() - gameState.GetBotMoveTimer())
                opp_recovery = (gameState.GetOppRecovery() - gameState.GetOppMoveTimer())
                #fa = (self.stored_bot_recovery - self.second_opinion_timer) - opp_recovery
                fa = bot_recovery - opp_recovery
                #if (fa <- 0 and gameState.GetOppMoveTimer() == 1) or (fa >= 0 and gameState.GetBotMoveTimer() == 1):
                fa_string = self.FrameData[self.stored_opp_id].WithPlusIfNeeded(fa)
                print(self.stored_prefix + "JUMP CANCELED -> " + fa_string + " NOW:" + fa_string)
                self.second_opinion = False
                self.second_opinion_timer = 0

            if self.second_opinion_timer > self.stored_opp_recovery:
                self.second_opinion = False
                self.second_opinion_timer = 0


        if (gameState.IsOppWhiffingXFramesAgo(self.active_frame_wait + 1)) and (gameState.IsBotBlocking()  or gameState.IsBotGettingHit() or gameState.IsBotBeingThrown() or gameState.IsBotStartedBeingJuggled() or gameState.IsBotBeingKnockedDown() or gameState.IsBotJustGrounded()):
            if gameState.DidBotIdChangeXMovesAgo(self.active_frame_wait)  or gameState.DidBotTimerReduceXMovesAgo(self.active_frame_wait):# or gameState.DidOppIdChangeXMovesAgo(self.active_frame_wait):
                gameState.BackToTheFuture(self.active_frame_wait)

                if not self.active_frame_wait >= gameState.GetOppActiveFrames() + 1:
                    self.active_frame_wait += 1
                else:
                    self.active_frame_wait = 1

                    if opp_id in self.FrameData:
                        frameDataEntry = self.FrameData[opp_id]
                    else:
                        frameDataEntry = FrameDataEntry()
                        self.FrameData[opp_id] = frameDataEntry

                    frameDataEntry.currentFrameAdvantage = '??'
                    frameDataEntry.move_id = opp_id
                    frameDataEntry.damage = gameState.GetMostRecentOppDamage()

                    if gameState.GetOppStartup() > 0:
                        frameDataEntry.startup = gameState.GetOppStartup()
                        frameDataEntry.activeFrames = gameState.GetOppActiveFrames()
                        frameDataEntry.hitType = AttackType(gameState.GetOppAttackType()).name
                        if gameState.IsOppAttackThrow():
                            frameDataEntry.hitType += "_THROW"
                        oldRecovery = 0
                    else:
                        snapshotOpp = gameState.GetLastOppWithDifferentMoveId()
                        if snapshotOpp != None:
                            frameDataEntry.startup = snapshotOpp.startup
                            frameDataEntry.activeFrames = snapshotOpp.GetActiveFrames()
                            frameDataEntry.hitType = AttackType(snapshotOpp.attack_type).name
                            if snapshotOpp.IsAttackThrow():
                                frameDataEntry.hitType += "_THROW"
                            oldRecovery = snapshotOpp.recovery

                    try:
                        frameDataEntry.recovery = gameState.GetOppRecovery() - frameDataEntry.startup - frameDataEntry.activeFrames + 1
                    except:
                        frameDataEntry.recovery = "?!"

                    gameState.ReturnToPresent()


                    time_till_recovery_opp = gameState.GetOppRecovery() - gameState.GetOppMoveTimer()
                    time_till_recovery_bot = gameState.GetBotRecovery() - gameState.GetBotMoveTimer()
                    new_frame_advantage_calc = time_till_recovery_bot - time_till_recovery_opp
                    old_frame_advantage_calc = None

                    #gameState.ReturnToPresent()
                    if gameState.IsBotBlocking():
                        old_frame_advantage_calc = gameState.GetBotRecovery() + frameDataEntry.startup - gameState.GetOppRecovery()
                        split_recovery_breakpoint = 3 #below this number are split recovery moves that don't need startup subtracted, like Steve's ff+2, above it are Lili's d/b+4 or Alisa's d+3+4
                        if oldRecovery > gameState.GetOppRecovery() + split_recovery_breakpoint:  #ankle breaker moves and a few others have a split recovery
                            old_frame_advantage_calc -= frameDataEntry.startup
                        frameDataEntry.onBlock = new_frame_advantage_calc

                        frameDataEntry.currentFrameAdvantage = frameDataEntry.WithPlusIfNeeded(frameDataEntry.onBlock)
                        frameDataEntry.blockFrames = frameDataEntry.recovery - frameDataEntry.startup

                    else:# gameState.IsBotGettingHit() or :
                        old_frame_advantage_calc = gameState.GetFrameDataOfCurrentOppMove()
                        frameDataEntry.onNormalHit = new_frame_advantage_calc
                        frameDataEntry.currentFrameAdvantage = frameDataEntry.WithPlusIfNeeded(frameDataEntry.onNormalHit)
                    #elif gameState.IsBotStartedBeingJuggled():
                        #frameDataEntry.onNormalHit = "JUGG"
                    #elif gameState.IsBotBeingKnockedDown():
                        #frameDataEntry.onNormalHit = "KDWN"
                    #elif gameState.IsBotJustGrounded():
                     #   frameDataEntry.onNormalHit = "GRND"
                    #elif gameState.IsBotBeingThrown():
                     #   pass

                    if self.isPlayerOne:
                        prefix = "p1: "
                    else:
                        prefix = 'p2: '

                    if old_frame_advantage_calc != new_frame_advantage_calc:
                        print("Frame advantage inconsistent calculation.  Old = " + str(old_frame_advantage_calc) + " New: " + str(new_frame_advantage_calc), file=sys.stderr)

                    print(prefix + str(frameDataEntry))
                    self.second_opinion = True
                    self.stored_opp_recovery = time_till_recovery_opp
                    self.stored_opp_fa = int(frameDataEntry.currentFrameAdvantage)
                    self.stored_bot_recovery = time_till_recovery_bot
                    self.stored_frame_data = prefix + str(frameDataEntry)
                    self.stored_prefix = prefix
                    self.stored_opp_id = opp_id

                    gameState.BackToTheFuture(self.active_frame_wait)
                gameState.ReturnToPresent()
        if self.isPlayerOne:
            gameState.FlipMirror()

class FrameDataEntry:
    def __init__(self):
        self.move_id = '??'
        self.startup = '??'
        self.hitType = '??'
        self.onBlock = '??'
        self.onCounterHit = '??'
        self.onNormalHit = '??'
        self.recovery = '??'
        self.damage = '??'
        self.blockFrames = '??'
        self.activeFrames = '??'
        self.currentFrameAdvantage = '??'

    def WithPlusIfNeeded(self, value):
        try:
            if value >= 0:
                return '+' + str(value)
            else:
                return str(value)
        except:
            return str(value)

    def __repr__(self):
        return "#" + str(self.move_id) + " | " + str(self.hitType)[:7] +  " | " + str(self.startup).center(len('startup')) + " | " + str(self.damage).center(len('  damage  ')) + " | " + self.WithPlusIfNeeded(self.onBlock).center(len('block')) + " | " \
               + self.WithPlusIfNeeded(self.onNormalHit) +  " | " + str(self.activeFrames).center(len(' active ')) \
               + " NOW:" + str(self.currentFrameAdvantage)

                #+ " Recovery: " + str(self.recovery)
                # + " Block Stun: " + str(self.blockFrames)
                #" CH: " + self.WithPlusIfNeeded(self.onCounterHit) +
