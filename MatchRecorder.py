
from TekkenGameState import TekkenGameState

class MatchRecorder:
    def __init__(self):
        self.input_log = []

    def Update(self, gameState:TekkenGameState):
        bot_input = gameState.GetBotInputState()
        opp_input = gameState.GetOppInputState()
        self.input_log.append(bot_input[0].name + "," + bot_input[1].name + "|" + opp_input[0].name + "," + opp_input[1].name)


    def PrintInputLog(self, filename):
        print("Recording match...")
        with open(filename, 'w') as fw:
            for input in self.input_log:
                fw.write(input + "\n")
        print("...match recorded")


