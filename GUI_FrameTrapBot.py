"""
A GUI that launches the frame trap bot, to practice frame traps on. The move the bot does out of block can be changed.

"""


from tkinter import *
from _TekkenBotLauncher import TekkenBotLauncher
from BotFrameTrap import BotFrameTrap
import sys


class GUI_FrameTrapBot(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.wm_title("Tekken Bot: Frame Trap Bot")
        #self.attributes("-topmost", True)
        #self.attributes("-alpha", "0.75")

        self.fa_p2_var = StringVar()
        self.fa_p2_var.set('??')
        self.frame_advantage_p2 = Label(self, textvariable = self.fa_p2_var, font=("Verdana", 44))
        self.frame_advantage_p2.pack(side="right", fill="both", expand=False)

        self.fa_p1_var = StringVar()
        self.fa_p1_var.set('??')
        self.frame_advantage_p1 = Label(self, textvariable=self.fa_p1_var, font=("Verdana", 44))
        self.frame_advantage_p1.pack(side="left", fill="both", expand=False)

        self.entry_var = StringVar()
        self.entry_var.set("+4")
        self.entry = Entry(self, textvariable=self.entry_var)
        self.entry.pack(side="top", fill="both", expand=True)
        self.entry.configure(state="normal")

        self.launcher = TekkenBotLauncher(BotFrameTrap, False)


    def update_launcher(self):
        self.launcher.GetBot().SetFrameTrapCommandFromNotationString(self.entry_var.get())
        self.launcher.Update()
        self.after(7, self.update_launcher)


if __name__ == '__main__':
    app = GUI_FrameTrapBot()
    app.update_launcher()
    app.mainloop()