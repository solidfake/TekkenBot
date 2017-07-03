from TekkenGameState import TekkenGameState
from Bot import Bot
from MatchRecorder import MatchRecorder

class BotRecorder(Bot):

    def __init__(self, botCommands):
        super().__init__(botCommands)
        self.recorder = MatchRecorder()


    def Update(self, gameState: TekkenGameState):
        self.recorder.Update(gameState)
        if gameState.WasFightReset():
            self.recorder.PrintInputLog("test.txt")
            self.recorder = MatchRecorder()




