from TekkenGameState import TekkenGameState
from TekkenEncyclopedia import TekkenEncyclopedia
import time

class FrameDataLauncher:
    def __init__(self):
        self.gameState = TekkenGameState()
        self.cyclopedia_p2 = TekkenEncyclopedia(False)
        self.cyclopedia_p1 = TekkenEncyclopedia(True)


    def Update(self):
        successfulUpdate = self.gameState.Update()
        if successfulUpdate:
            self.cyclopedia_p1.Update(self.gameState)
            self.cyclopedia_p2.Update(self.gameState)

if __name__ == "__main__":
    launcher = FrameDataLauncher()
    while(True):
        launcher.Update()
        time.sleep(.05)
