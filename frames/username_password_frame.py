from tkinter import *
import tkinter as tk
import ttkbootstrap as ttk
from core.utils import Utils

class UsernamePasswordFrame(Frame):

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        
        self.username_label = Label(self, text="Username", width=8, font=("Segoe UI", 10))
        self.password_label = Label(self, text="Password", width=8, font=("Segoe UI", 10))

        self.container_username_frame = Frame(self)
        self.container_password_frame = Frame(self)
        self.container_username_frame.columnconfigure(0, weight=1)
        self.container_password_frame.columnconfigure(0, weight=1)

        self.username_value_entry = ttk.Entry(self.container_username_frame, text="", width=40, font=("Segoe UI", 10))
        self.copy_username_button = ttk.Button(self.container_username_frame, text="📋")
        self.copy_username_button.bind("<Button-1>", lambda event: Utils.copy_to_clipboard(self, event, self.username_value_entry))

        self.password_value_entry = ttk.Entry(self.container_password_frame, text="", width=40, font=("Segoe UI", 10))
        self.copy_password_button = ttk.Button(self.container_password_frame, text="📋")
        self.copy_password_button.bind("<Button-1>", lambda event: Utils.copy_to_clipboard(self, event, self.password_value_entry))

        self.username_label.pack(padx=10, pady=(10, 0), anchor="w")
        self.container_username_frame.pack(fill="x", padx=10, pady=5)
        self.password_label.pack(padx=10, pady=(10, 0), anchor="w")
        self.container_password_frame.pack(fill="x", padx=10, pady=5)

        self.username_value_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.copy_username_button.grid(row=0, column=1)
        self.password_value_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.copy_password_button.grid(row=0, column=1)

    def set_username(self, username):
        self.set_value(self.username_value_entry, username)
    
    def set_password(self, password):
        self.set_value(self.password_value_entry, password)

    def set_value(self, entry, text):
        entry.config(state=tk.NORMAL)
        entry.delete(0, END)
        entry.insert(0, text)
        entry.config(state="readonly")
