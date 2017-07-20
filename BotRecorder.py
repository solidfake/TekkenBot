from tkinter import *
from tkinter.ttk import *
import time
from datetime import date
from MatchRecorder import MatchRecorder
from TekkenGameState import TekkenGameState

from GameInputter import *
from BasicCommands import *
from NotationParser import *

class BotRecorder():
    def __init__(self):
        self.toplevel = Tk()
        self.recorder = MatchRecorder()
        self.game_state = TekkenGameState()
        self.playback("match_1500581255.50204")
        self.playback_going = False
        self.is_recording = False #set this to true to record some matches
        self.is_playback_mode = True


    def update_launcher(self):

        time1 = time.time()


        successful = self.game_state.Update()
        if successful and self.game_state.IsGameHappening():


            if self.game_state.WasTimerReset():
                print("timer reset")
                if self.is_recording:
                    self.recorder.PrintInputLog("match_" + str(time.time()))
                self.playback_going = False

            if self.game_state.DidTimerStartTicking():
                print("ticking begins")
                if self.is_recording:
                    self.recorder = MatchRecorder()
                self.playback_going = True

            if len(self.game_state.stateLog) > 2:
                self.recorder.Update(self.game_state)

            if self.playback_going and self.is_playback_mode:
                self.p1_controller.Update(self.game_state.IsForegroundPID(), self.game_state.IsBotOnLeft())
                self.p2_controller.Update(self.game_state.IsForegroundPID(), not self.game_state.IsBotOnLeft())

                self.p1_bot.Update(self.game_state)
                self.p2_bot.Update(self.game_state)

        time2 = time.time()
        elapsed_time = 1000 * (time2 - time1)
        self.toplevel.after(max(2, 8 - int(round(elapsed_time))), self.update_launcher)




    def playback(self, filename):
        p1_controller = GameControllerInputter(False)
        p2_controller = GameControllerInputter(True)

        p1_bot = BotCommands(p1_controller, True)
        p2_bot = BotCommands(p2_controller, True)

        with open("TekkenData/Replays/" + filename) as fr:
            p1_commands = fr.readline().strip()
            p2_commands = fr.readline().strip()

        p1_bot.AddCommand(ParseMoveList(p1_commands))
        p2_bot.AddCommand(ParseMoveList(p2_commands))

        self.p1_controller = p1_controller
        self.p2_controller = p2_controller

        self.p1_bot = p1_bot
        self.p2_bot = p2_bot




if __name__ == '__main__':
    app = BotRecorder()
    app.update_launcher()
    app.toplevel.mainloop()