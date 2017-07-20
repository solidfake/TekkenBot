from tkinter import *
from tkinter.ttk import *
import GUI_FrameDataOverlay as fdo
import ConfigReader

class GUI_TekkenBotPrime(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.wm_title("Tekken Bot Prime")
        self.iconbitmap('TekkenData/tekken_bot_close.ico')

        self.color_scheme_config = ConfigReader.ConfigReader("color_scheme")
        self.color_scheme_config.add_comment("colors with names -> http://www.science.smith.edu/dftwiki/images/3/3d/TkInterColorCharts.png")
        self.changed_color_scheme("Current", False)

        self.menu = Menu(self)
        self.configure(menu=self.menu)

        self.text = Text(self, wrap="char")
        sys.stdout = TextRedirector(self.text, "stdout")

        self.overlay = fdo.GUI_FrameDataOverlay(self)

        self.checkbox_dict = {}
        self.column_menu = Menu(self.menu)
        for i, enum in enumerate(fdo.DataColumns):
            bool = self.overlay.redirector.columns_to_print[i]
            self.add_checkbox(self.column_menu, enum, enum.name, bool, self.changed_columns)
        self.menu.add_cascade(label='Columns', menu=self.column_menu)

        self.display_menu = Menu(self.menu)
        for enum in fdo.DisplaySettings:
            default = self.overlay.tekken_config.get_property(fdo.DisplaySettings.config_name(), enum.name, False)
            self.add_checkbox(self.display_menu, enum, enum.name, default, self.changed_display)
        self.menu.add_cascade(label="Display", menu=self.display_menu)

        self.color_scheme_menu = Menu(self.menu)
        self.radio_var = StringVar()
        for section in self.color_scheme_config.parser.sections():
            if section not in ("Comments", "Current"):
                self.color_scheme_menu.add_radiobutton(label=section, variable=self.radio_var, value=section, command=lambda : self.changed_color_scheme(self.radio_var.get()))
        self.menu.add_cascade(label="Color Scheme", menu=self.color_scheme_menu)



        self.text.grid(row = 2, column = 0, columnspan=2, sticky=N+S+E+W)
        #self.grid_rowconfigure(0, weight=1)
        #self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        #self.grid_columnconfigure(1, weight=1)

        self.geometry(str(720) + 'x' + str(720))

        self.overlay.update_launcher()
        self.overlay.hide()



    def add_checkbox(self, menu, lookup_key, display_string, default_value, button_command):
        var = BooleanVar()
        var.set(default_value)
        self.checkbox_dict[lookup_key] = var
        menu.add_checkbutton(label=display_string, onvalue=True, offvalue=False, variable=var, command = button_command)

    def changed_color_scheme(self, section, do_reboot=True):
        for enum in fdo.ColorSchemeEnum:
            fdo.CurrentColorScheme.dict[enum] = self.color_scheme_config.get_property(section, enum.name, fdo.CurrentColorScheme.dict[enum])
            self.color_scheme_config.set_property("Current", enum.name, fdo.CurrentColorScheme.dict[enum])
        self.color_scheme_config.write()
        if do_reboot:
            self.reboot_overlay()

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
        self.reboot_overlay()

    def reboot_overlay(self):
        self.overlay.restore_stdout()
        self.overlay.toplevel.destroy()
        self.overlay = fdo.GUI_FrameDataOverlay(self)
        self.overlay.update_launcher()
        self.overlay.hide()

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