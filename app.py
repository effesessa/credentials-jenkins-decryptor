from tkinter import *
import ttkbootstrap as ttk
from frames import *
from core import *
from  widget.menubar import MenuBar
import configparser
import threading

class App(Tk):
    def __init__(self):
        super().__init__()
        self.config = configparser.ConfigParser()
        self.style = ttk.Style(Utils.get_theme(self.config))
        self.title("Credentials Jenkins Decryptor v1.0")
        self.iconbitmap(Utils.resource_path("images/jenkinsd-transformed.ico"))
        self.geometry(Utils.in_the_center_of_screen(self, 800, 500))
        self.minsize(800, 500)
        self.frames = {}
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=10)
        self.grid_columnconfigure(0, weight=1)
        self.menubar = MenuBar(self)
        self.init()
        self.show_frame(SearchFrame)
        thread = threading.Thread(target=self.init_frames)
        thread.start()

    def init(self):    
        frame = SearchFrame(self)
        self.frames[SearchFrame] = frame

    def init_frames(self):
        self.jenkins_requestor = JenkinsRequestor(self.config)
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
