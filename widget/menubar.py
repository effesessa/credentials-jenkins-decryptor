import ttkbootstrap as ttk
import tkinter as tk
from frames import *

class MenuBar(ttk.Menubutton):

    def __init__(self, parent):
        super().__init__(parent, text="File")
        self.parent = parent
        self.grid(row=0, column=0, sticky="nw")
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Settings", command=self.settings)
        # associate menu with menubutton
        self['menu'] = menu
        
    def settings(self):
        self.parent.show_frame(SettingsFrame)
        