from tkinter import *
from tkinter.ttk import *
from GUI_FrameDataOverlay import *


class GUI_TekkenBotPrime(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.wm_title("Tekken Bot")
        self.geometry(str(720) + 'x' + str(720))

        self.menu = Menu(self)
        #self.menubar.add_command(label="Hello!")
        #self.menubar.add_command(label="Quit!")
        self.configure(menu=self.menu)
        #menubar.grid()

        self.checkbox_dict = {}
        self.column_menu = Menu(self.menu)
        for enum in DataColumns:
            self.add_checkbox(self.column_menu, enum)
        self.menu.add_cascade(label='Columns', menu=self.column_menu)


        self.overlay = GUI_FrameDataOverlay(self)
        self.overlay.update_launcher()



    def add_checkbox(self, menu, enum, default_value = True):
        var = BooleanVar()
        var.set(default_value)
        self.checkbox_dict[enum] = var
        button = menu.add_checkbutton(label=enum.name, onvalue=True, offvalue=False, variable=var, command = self.changed_columns)
        #button.bind("<Button-1>", self.changed_columns)

    def changed_columns(self):
        generated_columns = []
        for enum in DataColumns:
            var = self.checkbox_dict[enum]
            generated_columns.append(var.get())
        self.overlay.set_columns_to_print(generated_columns)


if __name__ == '__main__':
    app = GUI_TekkenBotPrime()
    #app.update_launcher()
    app.mainloop()