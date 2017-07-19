from tkinter import *
from tkinter.ttk import *
import GUI_FrameDataOverlay as fdo


class GUI_TekkenBotPrime(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.wm_title("Tekken Bot Prime")
        self.iconbitmap('TekkenData/tekken_bot_close.ico')
        self.geometry(str(720) + 'x' + str(720))

        self.menu = Menu(self)
        self.configure(menu=self.menu)

        self.text = Text(self, wrap="char")
        sys.stdout = TextRedirector(self.text, "stdout")

        self.overlay = fdo.GUI_FrameDataOverlay(self)

        self.checkbox_dict = {}
        self.column_menu = Menu(self.menu)
        for i, enum in enumerate(fdo.DataColumns):
            bool = self.overlay.redirector.columns_to_print[i]
            self.add_checkbox(self.column_menu, enum, bool, self.changed_columns)
        self.menu.add_cascade(label='Columns', menu=self.column_menu)

        self.display_menu = Menu(self.menu)
        for enum in fdo.DisplaySettings:
            default = self.overlay.tekken_config.get_property(fdo.DisplaySettings.config_name(), enum.name, False)
            self.add_checkbox(self.display_menu, enum, default, self.changed_display)
        self.menu.add_cascade(label="Display", menu=self.display_menu)

        self.text.grid()

        self.overlay.update_launcher()



    def add_checkbox(self, menu, enum, default_value, button_command):
        var = BooleanVar()
        var.set(default_value)
        self.checkbox_dict[enum] = var
        menu.add_checkbutton(label=enum.name, onvalue=True, offvalue=False, variable=var, command = button_command)
        #button.bind("<Button-1>", self.changed_columns)

    def changed_columns(self):
        generated_columns = []
        for enum in fdo.DataColumns:
            var = self.checkbox_dict[enum]
            generated_columns.append(var.get())
            self.overlay.update_column_to_print(enum, var.get())
        self.overlay.set_columns_to_print(generated_columns)

    def changed_display(self):
        for enum in fdo.DisplaySettings:
            var = self.checkbox_dict[enum]
            self.overlay.tekken_config.set_property(fdo.DisplaySettings.config_name(), enum.name, var.get())
        self.overlay.tekken_config.write()
        self.overlay.restore_stdout()
        self.overlay.toplevel.destroy()
        self.overlay = fdo.GUI_FrameDataOverlay(self)
        self.overlay.update_launcher()


class TextRedirector(object):
    def __init__(self, widget, tag="stdout"):
        self.widget = widget
        self.tag = tag

    def write(self, str):
        self.widget.configure(state="normal")
        self.widget.insert("end", str, (self.tag,))
        self.widget.configure(state="disabled")
        self.widget.see('end')

if __name__ == '__main__':
    app = GUI_TekkenBotPrime()
    #app.update_launcher()
    app.mainloop()