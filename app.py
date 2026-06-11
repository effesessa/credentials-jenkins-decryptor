from tkinter import *
import ttkbootstrap as ttk
from frames import *
from core import *
from  widget.menubar import MenuBar
import configparser
from widget.toast_notification import show_success_toast, show_error_toast, show_warning_toast, show_info_toast

class App(Tk):
    def __init__(self):
        super().__init__()
        self.withdraw()  # hide the window until the UI is ready (avoids the flash)
        self.config = configparser.ConfigParser()
        self.style = ttk.Style(Utils.get_theme(self.config))
        self.title(f"Credentials Jenkins Decryptor v{Utils.APP_VERSION}")
        Utils.set_icon(self)
        self.geometry(Utils.in_the_center_of_screen(self, 800, 500))
        self.minsize(800, 500)
        self.frames = {}
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=10)
        self.grid_columnconfigure(0, weight=1)
        self.jenkins_requestor = JenkinsRequestor(self.config)
        self.menubar = MenuBar(self)
        self.init()
        self.init_frames()
        self.show_frame(SearchFrame)
        self.update_idletasks()  # finish the layout while the window is still hidden
        self.deiconify()  # show the window already styled and laid out
    def init(self):    
        frame = SearchFrame(self)
        self.frames[SearchFrame] = frame

    def init_frames(self):
        self.script_executor = ScriptExecutor(self.jenkins_requestor)
        for F in (SettingsFrame, ResultFrame):
            frame = F(self)
            self.frames[F] = frame
    
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.grid(row=1, column=0, sticky="nsew")
        frame.tkraise()

app = App()
app.mainloop()
