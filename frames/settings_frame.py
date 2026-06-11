import tkinter as tk
import ttkbootstrap as ttk
import threading
from frames import *
import os
import configparser
from core import Utils
from widget.confirm_dialog import ask_yes_no
from widget.toast_notification import show_success_toast, show_warning_toast

class SettingsFrame(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.config_path = Utils.get_config_path(app_name="jenkins-decryptor")
        self.label_frame = tk.LabelFrame(self, text="Settings")
        self.label_frame.pack(expand=True, fill="both", padx=10, pady=(0, 10))

        # Server Address
        tk.Label(self.label_frame, text="Server Address").pack(padx=15, pady=(20, 0), anchor="w")
        self.server_stringvar = tk.StringVar()
        self.server_stringvar.trace_add("write", self.on_change)
        self.server_entry = ttk.Entry(self.label_frame, width=40, font=("Segoe UI", 10), textvariable=self.server_stringvar)
        self.server_entry.pack(padx=15, pady=(5, 0), anchor="w")
        tk.Label(self.label_frame, text="e.g. https://jenkins.company.com", font=("Segoe UI", 8), foreground="grey").pack(padx=15, pady=(2, 10), anchor="w")

        # Username
        tk.Label(self.label_frame, text="Username").pack(padx=15, anchor="w")
        self.username_stringvar = tk.StringVar()
        self.username_stringvar.trace_add("write", self.on_change)
        self.username_entry = ttk.Entry(self.label_frame, width=40, font=("Segoe UI", 10), textvariable=self.username_stringvar)
        self.username_entry.pack(padx=15, pady=10, anchor="w")

        # Token with show/hide toggle
        tk.Label(self.label_frame, text="Token").pack(padx=15, anchor="w")
        self.token_stringvar = tk.StringVar()
        self.token_stringvar.trace_add("write", self.on_change)
        token_row = tk.Frame(self.label_frame)
        token_row.pack(padx=15, pady=10, anchor="w")
        self.token_entry = ttk.Entry(token_row, width=37, font=("Segoe UI", 10), textvariable=self.token_stringvar, show="*")
        self.token_entry.pack(side="left")
        self._token_visible = False
        self.toggle_token_btn = ttk.Button(token_row, text="👁", width=3, command=self._toggle_token)
        self.toggle_token_btn.pack(side="left", padx=(5, 0))

        # Test button + spinner (spinner inserted here when testing)
        self.test_button = ttk.Button(self.label_frame, text="Test", width=10, command=self.test)
        self.test_button.pack(padx=15, pady=(0, 10), anchor="w")
        self.test_spinner = ttk.Progressbar(self.label_frame, mode="indeterminate", bootstyle="primary", length=100)

        ttk.Separator(self.label_frame, orient="horizontal", style="default").pack(fill="x", padx=15, pady=15)

        # Theme toggle
        tk.Label(self.label_frame, text="Theme").pack(padx=15, anchor="w")
        self.theme_checkbutton = ttk.Checkbutton(self.label_frame, bootstyle="round-toggle", text="light", command=self.change_theme)
        self.theme_checkbutton.pack(padx=15, anchor="w", pady=10)

        # Bottom bar
        self.bottom_frame = tk.Frame(self.label_frame)
        self.bottom_frame.pack(side=tk.BOTTOM, fill="x", pady=10)
        self.save_button = ttk.Button(self.bottom_frame, text="Save", width=10, command=self.save)
        self.save_button.pack(side=tk.RIGHT, padx=10)
        self.back_button = ttk.Button(self.bottom_frame, text="Back", width=10, command=self.back)
        self.back_button.pack(side=tk.LEFT, padx=10)

        self.load()
        self.tested = True

    def _toggle_token(self):
        self._token_visible = not self._token_visible
        self.token_entry.configure(show="" if self._token_visible else "*")

    def change_theme(self):
        theme = "cosmo" if self.theme_checkbutton.instate(['selected']) else "darkly"
        self.parent.style.theme_use(theme)
        # ttkbootstrap re-applies default colors to the classic tk Menubuttons on
        # theme change, sometimes asynchronously. Re-apply ours both immediately
        # and after a short delay so we win the race regardless of ordering —
        # otherwise, if our after(0) runs first, the wrong colors stick for the
        # rest of the session (there's nothing to re-apply them later).
        self.parent.after(0, self.parent.menubar.apply_colors)
        self.parent.after(150, self.parent.menubar.apply_colors)

    def on_change(self, var_name, index, mode):
        self.tested = False
        self.test_button.configure(bootstyle="default")

    def back(self):
        self.parent.show_frame(SearchFrame)

    def test(self):
        self.test_button.configure(state="disabled")
        self.test_spinner.pack(padx=15, pady=(0, 10), anchor="w")
        self.test_spinner.start(10)
        threading.Thread(target=self._do_test, daemon=True).start()

    def _do_test(self):
        result = self.parent.jenkins_requestor.test(
            self.server_entry.get(), self.username_entry.get(), self.token_entry.get()
        )
        self.after(0, lambda: self._test_done(result))

    def _test_done(self, success):
        self.test_spinner.stop()
        self.test_spinner.pack_forget()
        self.test_button.configure(state="normal")
        if success:
            self.tested = True
            self.test_button.configure(bootstyle=ttk.SUCCESS)
            show_success_toast(self.parent, "Connection successful", "Test")
        else:
            self.tested = False
            self.test_button.configure(bootstyle=ttk.WARNING)
            show_warning_toast(self.parent, "Could not connect to Jenkins", "Test")

    def save(self):
        if not self.tested:
            answer = ask_yes_no(
                self.parent,
                "Save",
                "You have not tested the connection to the server.\nDo you want to continue?",
            )
            if not answer:
                return
        config = configparser.ConfigParser()
        theme = "cosmo" if self.theme_checkbutton.instate(['selected']) else "darkly"
        if 'settings' not in config:
            config['settings'] = {}
        config['settings']['theme'] = theme
        server = self.server_entry.get().strip()
        username = self.username_entry.get().strip()
        token = self.token_entry.get().strip()
        if server:
            config['settings']['server_url'] = server
        if username:
            config['settings']['username'] = username
        # Token goes into the OS keyring; only fall back to plaintext config if
        # no keyring backend is available. Rewriting the file fresh also drops
        # any legacy plaintext token from earlier versions.
        token_in_keyring = Utils.set_token(username, token) if token else False
        if token and not token_in_keyring:
            config['settings']['token'] = token
        elif not token:
            Utils.delete_token(username)
        with open(self.config_path, 'w') as configfile:
            config.write(configfile)
        if token and not token_in_keyring:
            show_warning_toast(self.parent, "OS keyring unavailable: token stored in config file", "Settings")
        show_success_toast(self.parent, "Settings saved", "Saved")
        self.back()

    def load(self):
        if os.path.exists(self.config_path) and self.parent.config.has_section('settings'):
            username = self.parent.config['settings'].get('username', '')
            self.server_stringvar.set(self.parent.config['settings'].get('server_url', ''))
            self.username_stringvar.set(username)
            self.token_stringvar.set(Utils.get_token(username, self.parent.config))
            theme = Utils.get_theme(self.parent.config)
            if theme == "cosmo":
                self.theme_checkbutton.state(["selected"])
