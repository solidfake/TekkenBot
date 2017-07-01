"""
A transparent frame data display that sits on top of Tekken.exe in windowed or borderless mode.
"""


from tkinter import *
from tkinter.ttk import *
from _FrameDataLauncher import FrameDataLauncher
import sys
from ConfigReader import ConfigReader



class TextRedirector(object):
    def __init__(self, stdout, widget, style, fa_p1_var, fa_p2_var, at_p1_var, at_p2_var):
        self.stdout = stdout
        self.widget = widget
        self.fa_p1_var = fa_p1_var
        self.fa_p2_var = fa_p2_var
        self.at_p1_var = at_p1_var
        self.at_p2_var = at_p2_var
        self.style = style

    def write(self, output_str):
        self.stdout.write(output_str)

        lines = int(self.widget.index('end-1c').split('.')[0])
        if lines > 4:
            r = lines - 4
            for _ in range(r):
                self.widget.configure(state="normal")
                self.widget.delete('2.0', '3.0')
                self.widget.configure(state="disabled")

        if 'NOW:' in output_str:

            attack_type = output_str.split('|')[1]
            #if 'p1' in output_str:
                #self.at_p1_var.set(attack_type)
            #else:
                #self.at_p2_var.set(attack_type)
            out = output_str.split('NOW:')[0]
            fa = output_str.split('NOW:')[1][:3]
            if '?' not in fa:
                if int(fa) <= -14:
                    self.style.configure('.', background='#ff0066')
                elif int(fa) <= -10:
                    self.style.configure('.', background='#ff6600')
                elif int(fa) <= -5:
                    self.style.configure('.', background='#cca300')

                elif int(fa) <= 0:
                    self.style.configure('.', background='#ccff33')
                else:
                    self.style.configure('.', background='#0099ff')
                if "p1" in output_str:
                    self.fa_p1_var.set(fa)
                else:
                    self.fa_p2_var.set(fa)

        else:
            out = output_str

        self.widget.configure(state="normal")
        self.widget.insert("end", out)
        self.widget.configure(state="disabled")
        self.widget.see('0.0')



class GUI_FrameDataOverlay(Tk):
    def __init__(self):
        print("Tekken Bot Starting...")

        self.tekken_config = ConfigReader("frame_data_overlay")
        self.is_draggable_window = self.tekken_config.get_property("indepedent_window_mode", True, lambda x: not "0" in str(x))
        self.is_minimize_on_lost_focus = self.tekken_config.get_property("minimize_on_lost_focus", True, lambda x: not "0" in str(x))
        self.is_transparency = self.tekken_config.get_property("transparency", True, lambda x: not "0" in str(x))

        self.launcher = FrameDataLauncher()

        self.overlay_visible = False

        Tk.__init__(self)

        self.wm_title("Tekken Bot: Frame Data Overlay")

        self.attributes("-topmost", True)

        if self.is_transparency:
            self.wm_attributes("-transparentcolor", "white")
            self.attributes("-alpha", "0.75")

        self.w = 820
        self.h = 100
        self.geometry( str(self.w) + 'x' + str(self.h))

        self.iconbitmap('TekkenData/tekken_bot_close.ico')
        if not self.is_draggable_window:
            self.overrideredirect(True)
        self.configure(background='white')

        self.s = Style()
        self.s.theme_use('alt')
        self.s.configure('.', background='black')
        self.s.configure('.', foreground='black')

        Grid.columnconfigure(self, 0, weight=0)
        Grid.columnconfigure(self, 1, weight=1)
        Grid.columnconfigure(self, 2, weight=0)
        Grid.rowconfigure(self, 0, weight=1)
        Grid.rowconfigure(self, 1, weight=0)

        self.fa_p1_var = self.create_frame_advantage_label(0)
        self.fa_p2_var = self.create_frame_advantage_label(2)


        #self.at_p1_var = self.create_attack_type_label(0)
        #self.at_p2_var = self.create_attack_type_label(2)

        self.text = self.create_textbox()

        self.stdout = sys.stdout
        self.redirector = TextRedirector(self.stdout, self.text, self.s, self.fa_p1_var, self.fa_p2_var, None, None)
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        self.text.insert("1.0", "id                | type | startup | damage | block | hit | active\n")

        self.text.configure(state="disabled")

    def redirect_stdout(self):
        sys.stdout = self.redirector

    def restore_stdout(self):
        sys.stdout = self.stdout

    def create_frame_advantage_label(self, col):
        frame_advantage_var = StringVar()
        frame_advantage_var.set('??')
        frame_advantage_label = Label(self, textvariable=frame_advantage_var, font=("Consolas", 44), width=4, anchor='c',
                                        borderwidth=4, relief='ridge')
        frame_advantage_label.grid(row=0, column=col, sticky=E + W )
        return frame_advantage_var

    def create_attack_type_label(self, col):
        attack_type_var = StringVar()
        attack_type_var.set('??')
        attack_type_label = Label(self, textvariable=attack_type_var, font=("Verdana", 12), width=10, anchor='c',
                                    borderwidth=4, relief='ridge')
        attack_type_label.grid(row=1, column=col)
        return attack_type_var

    def create_textbox(self):
        textbox = Text(self, font=("Consolas, 14"), wrap=NONE, highlightthickness=0, relief='flat')
        # self.text.pack(side="top", fill="both", expand=True)
        textbox.grid(row=0, column=1, rowspan=2, sticky=N + S + W + E)
        textbox.configure(background='black')
        #textbox.configure(background='white')
        textbox.configure(foreground='green')
        return textbox


    def update_launcher(self):
        self.launcher.Update()

        if not self.is_draggable_window:
            tekken_rect = self.launcher.gameState.gameReader.GetWindowRect()
            if tekken_rect != None:
                x = (tekken_rect.right + tekken_rect.left)/2 - self.w/2
                y = tekken_rect.top
                self.geometry('%dx%d+%d+%d' % (self.w, self.h, x, y))
                if not self.overlay_visible:
                    self.show()
            else:
                if self.overlay_visible:
                    self.hide()

        if self.launcher.gameState.gameReader.GetNeedReacquireState():
            self.restore_stdout()
        else:
            self.redirect_stdout()

        self.after(7, self.update_launcher)

    def hide(self):
        if self.is_minimize_on_lost_focus and not self.is_draggable_window:
            self.withdraw()
            self.overlay_visible = False

    def show(self):
        self.deiconify()
        self.overlay_visible = True

if __name__ == '__main__':
    app = GUI_FrameDataOverlay()
    app.update_launcher()
    app.hide()
    app.mainloop()