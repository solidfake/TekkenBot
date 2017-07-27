"""
A transparent frame data display that sits on top of Tekken.exe in windowed or borderless mode.
"""


from tkinter import *
from tkinter.ttk import *
from _FrameDataLauncher import FrameDataLauncher
import sys
from ConfigReader import ConfigReader
import platform
import time
from enum import Enum



class DataColumns(Enum):
    input = 0
    type = 1
    startup = 2
    block = 3
    hit = 4
    CH = 5
    active = 6
    track = 7
    tot = 8
    rec = 9
    stun = 10
    notes = 11

    def config_name():
        return "DataColumns"


class DisplaySettings(Enum):
    overlay_on_bottom = -1
    overlay_as_draggable_window = 0
    only_appears_when_Tekken_7_has_focus = 1
    transparent_background = 2
    tiny_live_frame_data_numbers = 3

    def config_name():
        return "DisplaySettings"


class OverlayMode(Enum):
    FrameData = 0
    StatTracker = 1

class ColorSchemeEnum(Enum):
    background = 0
    transparent = 1
    p1_text = 2
    p2_text = 3
    system_text = 4
    advantage_plus = 5
    advantage_slight_minus = 6
    advantage_safe_minus = 7
    advantage_punishible = 8
    advantage_very_punishible = 9
    advantage_text = 10


class CurrentColorScheme:
    dict = {
        ColorSchemeEnum.background : 'gray10',
        ColorSchemeEnum.transparent: 'white',
        ColorSchemeEnum.p1_text: '#93A1A1',
        ColorSchemeEnum.p2_text: '#586E75',
        ColorSchemeEnum.system_text: 'lawn green',
        ColorSchemeEnum.advantage_plus: 'DodgerBlue2',
        ColorSchemeEnum.advantage_slight_minus: 'ivory2',
        ColorSchemeEnum.advantage_safe_minus: 'ivory2',
        ColorSchemeEnum.advantage_punishible: 'orchid2',
        ColorSchemeEnum.advantage_very_punishible: 'deep pink',
        ColorSchemeEnum.advantage_text: 'black',
    }


class TextRedirector(object):
    def __init__(self, stdout, widget, style, fa_p1_var, fa_p2_var):
        self.stdout = stdout
        self.widget = widget
        self.fa_p1_var = fa_p1_var
        self.fa_p2_var = fa_p2_var
        self.style = style
        self.widget.tag_config("p1", foreground=CurrentColorScheme.dict[ColorSchemeEnum.p1_text])
        self.widget.tag_config("p2", foreground=CurrentColorScheme.dict[ColorSchemeEnum.p2_text])
        self.columns_to_print = [True] * len(DataColumns)
        self.mode = OverlayMode.FrameData

        self.style.configure('.', background=CurrentColorScheme.dict[ColorSchemeEnum.advantage_slight_minus])

    def set_columns_to_print(self, booleans_for_columns):
        self.columns_to_print = booleans_for_columns
        self.populate_column_names(booleans_for_columns)

    def populate_column_names(self, booleans_for_columns):
        column_names = ""
        for i, enum in enumerate(DataColumns):
            if booleans_for_columns[i]:
                column_names += "| {} ".format(enum.name)
        self.set_first_column(column_names)

    def set_first_column(self, first_column_string):
        self.widget.configure(state="normal")
        self.widget.delete("1.0", "2.0")
        self.widget.insert("1.0", first_column_string + '\n')
        self.widget.configure(state="disabled")


    def write(self, output_str):
        self.stdout.write(output_str)

        lines = int(self.widget.index('end-1c').split('.')[0])
        max_lines = 5
        if lines > max_lines:
            r = lines - max_lines
            for _ in range(r):
                self.widget.configure(state="normal")
                self.widget.delete('2.0', '3.0')
                self.widget.configure(state="disabled")



        if 'NOW:' in output_str:

            data = output_str.split('NOW:')[0]
            fa = output_str.split('NOW:')[1][:3]
            if self.mode == OverlayMode.FrameData:
                if '?' not in fa:
                    if int(fa) <= -14:
                        self.style.configure('.', background=CurrentColorScheme.dict[ColorSchemeEnum.advantage_very_punishible])
                    elif int(fa) <= -10:
                        self.style.configure('.', background=CurrentColorScheme.dict[ColorSchemeEnum.advantage_punishible])
                    elif int(fa) <= -5:
                        self.style.configure('.', background=CurrentColorScheme.dict[ColorSchemeEnum.advantage_safe_minus])
                    elif int(fa) < 0:
                        self.style.configure('.', background=CurrentColorScheme.dict[ColorSchemeEnum.advantage_slight_minus])
                    else:
                        self.style.configure('.', background=CurrentColorScheme.dict[ColorSchemeEnum.advantage_plus])

            text_tag = None
            if "p1:" in output_str:
                self.fa_p1_var.set(fa)
                data = data.replace('p1:', '')
                text_tag = 'p1'
            else:
                self.fa_p2_var.set(fa)
                data = data.replace('p2:', '')
                text_tag = 'p2'

            out = ""
            for i, col in enumerate(data.split('|')):
                if self.columns_to_print[i]:
                    out += '|' + col

            out += "\n"
            self.widget.configure(state="normal")
            self.widget.insert("end", out, text_tag)
            self.widget.configure(state="disabled")
            self.widget.see('0.0')
            self.widget.yview('moveto', '.02')



class GUI_FrameDataOverlay():
    def __init__(self, master):
        print("Tekken Bot Starting...")

        is_windows_7 = 'Windows-7' in platform.platform()
        self.tekken_config = ConfigReader("frame_data_overlay")
        self.is_draggable_window = self.tekken_config.get_property(DisplaySettings.config_name(), DisplaySettings.overlay_as_draggable_window.name, False)
        self.is_minimize_on_lost_focus = self.tekken_config.get_property(DisplaySettings.config_name(), DisplaySettings.only_appears_when_Tekken_7_has_focus.name, True)
        self.is_transparency = self.tekken_config.get_property(DisplaySettings.config_name(), DisplaySettings.transparent_background.name, not is_windows_7)
        self.is_overlay_on_top = not self.tekken_config.get_property(DisplaySettings.config_name(), DisplaySettings.overlay_on_bottom.name, False)
        self.enable_nerd_data = self.tekken_config.get_property(DisplaySettings.config_name(), "data_for_nerds", False)
        self.show_live_framedata = self.tekken_config.get_property(DisplaySettings.config_name(), DisplaySettings.tiny_live_frame_data_numbers.name, True)
        self.mode = OverlayMode.FrameData

        self.launcher = FrameDataLauncher(self.enable_nerd_data)

        self.overlay_visible = False
        if master == None:
            self.toplevel = Tk()
        else:
            self.toplevel = Toplevel()

        self.toplevel.wm_title("Tekken Bot: Frame Data Overlay")

        self.toplevel.attributes("-topmost", True)

        self.background_color = CurrentColorScheme.dict[ColorSchemeEnum.background]

        if self.is_transparency:
            self.tranparency_color = CurrentColorScheme.dict[ColorSchemeEnum.transparent]
            self.toplevel.wm_attributes("-transparentcolor", self.tranparency_color)
            self.toplevel.attributes("-alpha", "0.75")
        else:
            if is_windows_7:
                print("Windows 7 detected. Disabling transparency.")
            self.tranparency_color = self.background_color
        self.toplevel.configure(background=self.tranparency_color)



        self.w = 1000
        self.h = 86

        if self.enable_nerd_data:
            self.w += 400

        self.toplevel.geometry( str(self.w) + 'x' + str(self.h))

        self.toplevel.iconbitmap('TekkenData/tekken_bot_close.ico')
        if not self.is_draggable_window:
            self.toplevel.overrideredirect(True)


        self.s = Style()
        self.s.theme_use('alt')
        self.s.configure('.', background=self.background_color)
        self.s.configure('.', foreground=CurrentColorScheme.dict[ColorSchemeEnum.advantage_text])

        Grid.columnconfigure(self.toplevel, 0, weight=0)
        Grid.columnconfigure(self.toplevel, 1, weight=0)
        Grid.columnconfigure(self.toplevel, 2, weight=0)
        Grid.columnconfigure(self.toplevel, 3, weight=1)
        Grid.columnconfigure(self.toplevel, 4, weight=0)
        Grid.columnconfigure(self.toplevel, 5, weight=0)
        Grid.columnconfigure(self.toplevel, 6, weight=0)
        Grid.rowconfigure(self.toplevel, 0, weight=1)
        Grid.rowconfigure(self.toplevel, 1, weight=0)

        self.s.configure('TFrame', background=self.tranparency_color)
        self.fa_p1_var, fa_p1_label = self.create_frame_advantage_label(1)
        self.fa_p2_var, fa_p2_label = self.create_frame_advantage_label(5)

        self.l_margin = self.create_padding_frame(0)
        self.r_margin = self.create_padding_frame(6)
        self.l_seperator = self.create_padding_frame(2)
        self.r_seperator = self.create_padding_frame(4)

        if self.show_live_framedata:
            self.l_live_recovery = self.create_live_recovery(fa_p1_label, 0)
            self.r_live_recovery = self.create_live_recovery(fa_p2_label, 0)


        self.text = self.create_textbox(3)

        self.stdout = sys.stdout
        self.redirector = TextRedirector(self.stdout, self.text, self.s, self.fa_p1_var, self.fa_p2_var)
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        #self.text.insert("1.0", "{:^5}|{:^8}|{:^9}|{:^7}|{:^5}|{:^5}|{:^8}|{:^5}|{:^5}|{:^7}|{:^5}|{}\n".format(" input ", "type", "startup", "block", "hit", "CH", "active", "track", "tot", "rec", "stun", "notes"))
        #self.redirector.populate_column_names(self.get_data_columns())
        self.redirector.set_columns_to_print(self.get_data_columns())

        self.text.configure(state="disabled")

    def get_data_columns(self):
        booleans_for_columns = []
        for enum in DataColumns:
            bool = self.tekken_config.get_property(DataColumns.config_name(), enum.name, True)
            booleans_for_columns.append(bool)
        return booleans_for_columns


    def redirect_stdout(self):
        sys.stdout = self.redirector

    def restore_stdout(self):
        sys.stdout = self.stdout

    def create_padding_frame(self, col):
        padding = Frame(self.toplevel, width=10)
        padding.grid(row=0, column=col, rowspan=2, sticky=N + S + W + E)
        return padding

    def create_live_recovery(self, parent, col):
        live_recovery_var = StringVar()
        live_recovery_var.set('??')
        live_recovery_label = Label(parent, textvariable=live_recovery_var, font=("Segoe UI", 12), width=5, anchor='c')
        #live_recovery_label.grid(row=0, column=col, sticky =S+W)
        live_recovery_label.place(rely=0.0, relx=0.0, x=4, y=4, anchor=NW)
        return live_recovery_var

    def create_frame_advantage_label(self, col):
        frame_advantage_var = StringVar()
        frame_advantage_var.set('?')
        frame_advantage_label = Label(self.toplevel, textvariable=frame_advantage_var, font=("Consolas", 44), width=4, anchor='c',
                                        borderwidth=4, relief='ridge')
        frame_advantage_label.grid(row=0, column=col)
        return frame_advantage_var, frame_advantage_label

    def create_attack_type_label(self, col):
        attack_type_var = StringVar()
        attack_type_var.set('?')
        attack_type_label = Label(self.toplevel, textvariable=attack_type_var, font=("Verdana", 12), width=10, anchor='c',
                                    borderwidth=4, relief='ridge')
        attack_type_label.grid(row=1, column=col)
        return attack_type_var

    def create_textbox(self, col):
        textbox = Text(self.toplevel, font=("Consolas, 14"), wrap=NONE, highlightthickness=0, pady=0, relief='flat')
        # self.text.pack(side="top", fill="both", expand=True)
        textbox.grid(row=0, column=col, rowspan=2, sticky=N + S + W + E)
        #textbox.configure(background='black')
        #textbox.configure(background='white')
        textbox.configure(background=self.background_color)

        textbox.configure(foreground=CurrentColorScheme.dict[ColorSchemeEnum.system_text])
        #textbox.configure(foreground='dark khaki')
        #textbox.configure(foreground='#839496')
        #textbox.configure(foreground='#657B83')
        return textbox


    def update_launcher(self):
        time1 = time.time()
        self.launcher.Update()

        if self.show_live_framedata:
            if len(self.launcher.gameState.stateLog) > 1:
                l_recovery = str(self.launcher.gameState.GetOppFramesTillNextMove() - self.launcher.gameState.GetBotFramesTillNextMove())
                r_recovery = str(self.launcher.gameState.GetBotFramesTillNextMove() - self.launcher.gameState.GetOppFramesTillNextMove())
                if not '-' in l_recovery:
                    l_recovery = '+' + l_recovery
                if not '-' in r_recovery:
                    r_recovery = '+' + r_recovery
                self.l_live_recovery.set(l_recovery)
                self.r_live_recovery.set(r_recovery)


        if not self.is_draggable_window:
            tekken_rect = self.launcher.gameState.gameReader.GetWindowRect()
            if tekken_rect != None:
                x = (tekken_rect.right + tekken_rect.left)/2 - self.w/2
                if self.is_overlay_on_top:
                    y = tekken_rect.top
                else:
                    y = tekken_rect.bottom - self.h - 10
                self.toplevel.geometry('%dx%d+%d+%d' % (self.w, self.h, x, y))
                if not self.overlay_visible:
                    self.show()
            else:
                if self.overlay_visible:
                    self.hide()

        if self.launcher.gameState.gameReader.GetNeedReacquireState():
            self.restore_stdout()
        else:
            self.redirect_stdout()


        time2 = time.time()
        elapsed_time = 1000 * (time2 - time1)
        self.toplevel.after(max(2, 8 - int(round(elapsed_time))), self.update_launcher)

    def hide(self):
        if self.is_minimize_on_lost_focus and not self.is_draggable_window:
            self.toplevel.withdraw()
            self.overlay_visible = False

    def show(self):
        self.toplevel.deiconify()
        self.overlay_visible = True

    def set_columns_to_print(self, columns_to_print):
        self.redirector.set_columns_to_print(columns_to_print)

    def update_column_to_print(self, enum, value):
        self.tekken_config.set_property(DataColumns.config_name(), enum.name, value)
        self.write_config_file()


    def write_config_file(self):
        self.tekken_config.write()





if __name__ == '__main__':
    #root = Tk()
    app = GUI_FrameDataOverlay(None)
    app.update_launcher()
    app.hide()
    app.write_config_file()
    app.toplevel.mainloop()