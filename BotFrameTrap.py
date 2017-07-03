"""
A simple bot that presses buttons when emerging from block or hit stun.

"""

from Bot import Bot
from TekkenGameState import TekkenGameState
from BotData import BotBehaviors
from NotationParser import ParseMoveList


class BotFrameTrap(Bot):

    def __init__(self, botCommands):
        super().__init__(botCommands)
        self.SetFrameTrapCommandFromNotationString("+4")


    def Update(self, gameState: TekkenGameState):
        BotBehaviors.Basic(gameState, self.botCommands)

        if self.botCommands.IsAvailable():
            BotBehaviors.BlockAllAttacks(gameState, self.botCommands)
            if gameState.IsBotBlocking() or gameState.IsBotGettingHit():
                self.botCommands.AddCommand(self.response)


    def SetFrameTrapCommandFromNotationString(self, notation: str):
        try:
            self.response = ParseMoveList(">, " + notation + ", >>")
        except:
            print("Could not parse move: " + notation)

