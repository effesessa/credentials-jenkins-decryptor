import tkinter as tk
import ttkbootstrap as ttk
from frames import *
import os
import configparser
from core import Utils

class SettingsFrame(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.config_path = Utils.get_config_path(app_name="jenkins-decryptor")
        self.label_frame = tk.LabelFrame(self, text="Settings")
        self.label_frame.pack(expand=True, fill="both", padx=10, pady=(0, 10))
        self.label_server_entry = tk.Label(self.label_frame, text="Server Address")
        self.label_server_entry.pack(padx=15, pady=(20, 0), anchor="w")
        self.server_stringvar = tk.StringVar()
        self.server_stringvar.trace_add("write", self.on_change)
        self.server_entry = ttk.Entry(self.label_frame, width=40, font=("Segoe UI", 10), textvariable=self.server_stringvar)
        self.server_entry.pack(padx=15, pady=10, anchor="w")
        self.label_username_entry = tk.Label(self.label_frame, text="Username")
        self.label_username_entry.pack(padx=15, anchor="w")
        self.username_stringvar = tk.StringVar()
        self.username_stringvar.trace_add("write", self.on_change)
        self.username_entry = ttk.Entry(self.label_frame, width=40, font=("Segoe UI", 10), textvariable=self.username_stringvar)
        self.username_entry.pack(padx=15, pady=10, anchor="w")
        self.label_token_entry = tk.Label(self.label_frame, text="Token")
        self.label_token_entry.pack(padx=15, anchor="w")
        self.token_stringvar = tk.StringVar()
        self.token_stringvar.trace_add("write", self.on_change)
        self.token_entry = ttk.Entry(self.label_frame, width=40, font=("Segoe UI", 10), textvariable=self.token_stringvar)
        self.token_entry.pack(padx=15, pady=10, anchor="w")
        self.test_button = ttk.Button(self.label_frame, text="Test", width=10, command=self.test)
        self.test_button.pack(padx=15, pady=10, anchor="w")
        ttk.Separator(self.label_frame, orient='horizontal', style="default").pack(fill="x", padx=15, pady=15)
        self.label_theme = tk.Label(self.label_frame, text="Theme")
        self.label_theme.pack(padx=15, anchor="w")
        self.theme_checkbutton = ttk.Checkbutton(self.label_frame, bootstyle="round-toggle", text="light", command=self.change_theme)
        self.theme_checkbutton.pack(padx=15, anchor="w", pady=10)
        self.bottom_frame = tk.Frame(self.label_frame)
        self.bottom_frame.pack(side=tk.BOTTOM, fill="x", pady=10)
        self.save_button = ttk.Button(self.bottom_frame, text="Save", width=10, command=self.save)
        self.save_button.pack(side=tk.RIGHT, padx=10)
        self.back_button = ttk.Button(self.bottom_frame, text="Back", width=10, command=self.back)
        self.back_button.pack(side=tk.LEFT, padx=10)
        self.load()
        self.tested = True
    
    def change_theme(self):
        if self.theme_checkbutton.instate(['selected']):
            self.parent.style = ttk.Style("cosmo")
        else:
            self.parent.style = ttk.Style("darkly")
    
    def on_change(self, var_name, index, mode):
        self.tested = False
        self.test_button.configure(bootstyle="default")

    def back(self):
        self.parent.show_frame(SearchFrame)

    def test(self):
        test_response = self.parent.jenkins_requestor.test(self.server_entry.get(), self.username_entry.get(), self.token_entry.get())
        if test_response:
            self.tested = True
            self.test_button.configure(bootstyle=ttk.SUCCESS)
        else:
            self.tested = False
            self.test_button.configure(bootstyle=ttk.WARNING)

    def save(self):
        if not self.tested:
            answer = tk.messagebox.askyesno(
                "Save",
                f"You have not tested the connection to the server.\nDo you want to continue?"
            )
            if not answer:
                return
        config = configparser.ConfigParser()
        theme = "cosmo" if self.theme_checkbutton.instate(['selected']) else "darkly"
        if 'settings' not in config:
            config['settings'] = {}
        config['settings']['theme'] = theme
        if self.server_entry.get().strip():
            config['settings']['server_url'] = self.server_entry.get().strip()
        if self.username_entry.get().strip():
            config['settings']['username'] = self.username_entry.get().strip()
        if self.token_entry.get().strip():
            config['settings']['token'] = self.token_entry.get().strip()
        with open(self.config_path, 'w') as configfile:
            config.write(configfile)
        self.back()

    def load(self):
        if os.path.exists(self.config_path):
            self.server_stringvar.set(self.parent.config['settings'].get('server_url', ''))
            self.username_stringvar.set(self.parent.config['settings'].get('username', ''))
            self.token_stringvar.set(self.parent.config['settings'].get('token', ''))
            theme = Utils.get_theme(self.parent.config)
            if theme == "cosmo":
                self.theme_checkbutton.state(["selected"])
