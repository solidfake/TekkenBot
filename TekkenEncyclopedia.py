"""
Collects information from TekkenGameState over time in hopes of synthesizing it and presenting it in a more useful way.

"""

from MoveInfoEnums import AttackType
from TekkenGameState import TekkenGameState

class TekkenEncyclopedia:
    def __init__(self, isPlayerOne = False):
        self.FrameData = {}
        self.isPlayerOne = isPlayerOne
        self.active_frame_wait = 1

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

        bot_id = gameState.GetBotMoveId()
        opp_id = gameState.GetOppMoveId()
        bot_timer = gameState.GetBotMoveTimer()
        opp_timer = gameState.GetOppMoveTimer()

        if (gameState.IsOppWhiffing()) and (gameState.IsBotBlocking()  or gameState.IsBotGettingHit() or gameState.IsBotBeingThrown() or gameState.IsBotStartedBeingJuggled() or gameState.IsBotBeingKnockedDown() or gameState.IsBotJustGrounded()):

            if gameState.DidBotIdChangeXMovesAgo(self.active_frame_wait)  or gameState.DidBotTimerReduceXMovesAgo(self.active_frame_wait): #or (opp_id != self.previous_opp_id and (100 < opp_id < 10000))
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

                    if gameState.IsBotBlocking():
                        frameDataEntry.onBlock = gameState.GetBotRecovery() + frameDataEntry.startup - gameState.GetOppRecovery()
                        if oldRecovery > gameState.GetOppRecovery():  #ankle breaker moves and a few others have a split recovery
                            frameDataEntry.onBlock -= frameDataEntry.startup


                        frameDataEntry.currentFrameAdvantage = frameDataEntry.WithPlusIfNeeded(frameDataEntry.onBlock)
                        frameDataEntry.blockFrames = frameDataEntry.recovery - frameDataEntry.startup

                    elif gameState.IsBotGettingHit():
                        frameDataEntry.onNormalHit = gameState.GetFrameDataOfCurrentOppMove()
                        frameDataEntry.currentFrameAdvantage = frameDataEntry.WithPlusIfNeeded(frameDataEntry.onNormalHit)
                    elif gameState.IsBotStartedBeingJuggled():
                        frameDataEntry.onNormalHit = "JUGG"
                    elif gameState.IsBotBeingKnockedDown():
                        frameDataEntry.onNormalHit = "KDWN"
                    elif gameState.IsBotJustGrounded():
                        frameDataEntry.onNormalHit = "GRND"
                    elif gameState.IsBotBeingThrown():
                        pass

                    if self.isPlayerOne:
                        prefix = "p1: "
                    else:
                        prefix = 'p2: '


                    print(prefix + str(frameDataEntry))

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
        return "#" + str(self.move_id) + " | " + str(self.hitType) +  " | " + str(self.startup) + " | " + str(self.damage) + " | " + self.WithPlusIfNeeded(self.onBlock) + " | " \
               + self.WithPlusIfNeeded(self.onNormalHit) +  " | " + str(self.activeFrames) \
               + " NOW:" + str(self.currentFrameAdvantage)

                #+ " Recovery: " + str(self.recovery)
                # + " Block Stun: " + str(self.blockFrames)
                #" CH: " + self.WithPlusIfNeeded(self.onCounterHit) +
