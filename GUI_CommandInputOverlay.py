import GUI_Overlay
from tkinter import *
from tkinter.ttk import *
from MoveInfoEnums import InputDirectionCodes
from MoveInfoEnums import InputAttackCodes



class TextRedirector(object):
    def __init__(self, canvas, height):
        pass

    def write(self, str):
        pass


class GUI_CommandInputOverlay(GUI_Overlay.Overlay):

    symbol_map = {

        #InputDirectionCodes.u: '⇑',
        #InputDirectionCodes.uf: '⇗',
        #InputDirectionCodes.f: '⇒',
        #InputDirectionCodes.df: '⇘',
        #InputDirectionCodes.d: '⇓',
        #InputDirectionCodes.db: '⇙',
        #InputDirectionCodes.b: '⇐',
        #InputDirectionCodes.ub: '⇖',
        #InputDirectionCodes.N: '★',

        InputDirectionCodes.u : '↑',
        InputDirectionCodes.uf: '↗',
        InputDirectionCodes.f: '→',
        InputDirectionCodes.df: '↘',
        InputDirectionCodes.d: '↓',
        InputDirectionCodes.db: '↙',
        InputDirectionCodes.b: '←',
        InputDirectionCodes.ub: '↖',
        InputDirectionCodes.N: '★',
        InputDirectionCodes.FIGHT_START: '!'

    }


    def __init__(self, master, launcher):
        print("Launching overlay...")

        GUI_Overlay.Overlay.__init__(self, master, (1200, 86), "Tekken Bot: Command Input Overlay")

        self.launcher = launcher

        self.canvas = Canvas(self.toplevel, width=self.w, height=self.h, bg='black')

        self.canvas.pack()

        self.length = 60
        self.step = self.w/self.length
        for i in range(self.length):
            self.canvas.create_text(i * self.step + (self.step / 2), 8, text = str(i), fill='snow')
            self.canvas.create_line(i * self.step, 0, i * self.step, self.h, fill="red")

        self.canvas

        self.redirector = TextRedirector(self.canvas, self.h)\

        self.stored_inputs = []


    def update_state(self):
        GUI_Overlay.Overlay.update_state(self)
        if self.launcher.gameState.stateLog[-1].is_player_player_one:
            input = self.launcher.gameState.stateLog[-1].bot.GetInputState()
        else:
            input = self.launcher.gameState.stateLog[-1].opp.GetInputState()
        frame_count = self.launcher.gameState.stateLog[-1].frame_count
        #print(input)
        self.update_input(input, frame_count)


    def update_input(self, input, frame_count):
        input_tag = "inputs"
        self.stored_inputs.append(input)
        if len(self.stored_inputs) >= self.length and input != self.stored_inputs[-2]:
            self.canvas.delete(input_tag)

            self.stored_inputs = self.stored_inputs[-self.length:]

            #print(self.stored_inputs)
            for i, (direction_code, attack_code, rage_flag) in enumerate(self.stored_inputs):
                self.canvas.create_text(i * self.step + (self.step / 2), 30, text=GUI_CommandInputOverlay.symbol_map[direction_code], fill='snow',  font=("Consolas", 20), tag=input_tag)
                self.canvas.create_text(i * self.step + (self.step / 2), 60, text=attack_code.name.replace('x', '').replace('N', ''), fill='snow',  font=("Consolas", 12), tag=input_tag)








