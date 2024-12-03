from tkinter import *
import tkinter as tk
import ttkbootstrap as ttk
from core import Utils

class SecretFrame(Frame):

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        
        self.secret_label = Label(self, text="Secret", width=6, font=("Segoe UI", 10))
        self.container_secret_frame = Frame(self)
        self.container_secret_frame.columnconfigure(0, weight=1)

        self.secret_value_entry = ttk.Entry(self.container_secret_frame, text="", width=40, font=("Segoe UI", 10))
        self.copy_secret_button = ttk.Button(self.container_secret_frame, text="📋")
        self.copy_secret_button.bind("<Button-1>", lambda event: Utils.copy_to_clipboard(self, event, self.secret_value_entry))

        self.secret_label.pack(padx=10, pady=(10, 0), anchor="w")
        self.container_secret_frame.pack(fill="x", padx=10, pady=5)

        self.secret_value_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.copy_secret_button.grid(row=0, column=1)

    def set_value(self, secret):
        self.secret_value_entry.config(state=tk.NORMAL)
        self.secret_value_entry.delete(0, END)
        self.secret_value_entry.insert(0, secret)
        self.secret_value_entry.config(state="readonly")
