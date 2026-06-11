import webbrowser
import ttkbootstrap as ttk
import tkinter as tk
from frames import *
from widget.about_dialog import show_about

DONATE_URL = "https://www.paypal.com/paypalme/effesessa"

class MenuBar(ttk.Frame):

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.grid(row=0, column=0, sticky="nw")

        # File menu
        self.file_button = tk.Menubutton(self, text="File", padx=8, pady=2)
        self.file_button.pack(side="left")
        self.file_menu = tk.Menu(self.file_button, tearoff=0)
        self.file_menu.add_command(label="Create Credential", command=lambda: CreateCredentialFrame(self.parent, self.parent.jenkins_requestor))
        self.file_menu.add_command(label="Settings", command=self.settings)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.parent.destroy)
        self.file_button["menu"] = self.file_menu

        # Help menu (donations / support)
        self.help_button = tk.Menubutton(self, text="Help", padx=8, pady=2)
        self.help_button.pack(side="left")
        self.help_menu = tk.Menu(self.help_button, tearoff=0)
        self.help_menu.add_command(label="♥ Donate (PayPal)", command=self.donate)
        self.help_menu.add_separator()
        self.help_menu.add_command(label="About", command=self.about)
        self.help_button["menu"] = self.help_menu

        # ttkbootstrap overrides colors passed to a classic tk widget's
        # constructor, so they must be applied AFTER creation (here they stick).
        # Also re-applied on theme change (see SettingsFrame.change_theme).
        self.after(0, self.apply_colors)

    def apply_colors(self):
        colors = ttk.Style().colors
        try:
            bg = self.parent.frames[SearchFrame].cget("background")  # blend with the home
        except Exception:
            bg = colors.bg
        for button in (self.file_button, self.help_button):
            button.config(
                bg=bg, fg=colors.fg,                       # theme fg: readable in any theme
                activebackground=colors.selectbg, activeforeground=colors.fg,
            )

    def settings(self):
        self.parent.show_frame(SettingsFrame)

    def donate(self):
        webbrowser.open_new(DONATE_URL)

    def about(self):
        show_about(self.parent)
