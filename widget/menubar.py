import webbrowser
import threading
import ttkbootstrap as ttk
import tkinter as tk
from frames import *
from core import Utils, check_for_update, t
from widget.about_dialog import show_about
from widget.confirm_dialog import ask_yes_no
from widget.toast_notification import show_success_toast, show_error_toast

DONATE_URL = "https://www.paypal.com/paypalme/effesessa"

class MenuBar(ttk.Frame):

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.grid(row=0, column=0, sticky="nw")

        # File menu
        self.file_button = tk.Menubutton(self, text=t("menu.file"), padx=8, pady=2)
        self.file_button.pack(side="left")
        self.file_menu = tk.Menu(self.file_button, tearoff=0)
        self.file_menu.add_command(label=t("menu.create_credential"), command=lambda: CreateCredentialFrame(self.parent, self.parent.jenkins_requestor))
        self.file_menu.add_command(label=t("menu.settings"), command=self.settings)
        self.file_menu.add_separator()
        self.file_menu.add_command(label=t("menu.exit"), command=self.parent.destroy)
        self.file_button["menu"] = self.file_menu

        # Help menu (donations / support)
        self.help_button = tk.Menubutton(self, text=t("menu.help"), padx=8, pady=2)
        self.help_button.pack(side="left")
        self.help_menu = tk.Menu(self.help_button, tearoff=0)
        self.help_menu.add_command(label=t("menu.check_updates"), command=self.check_updates)
        self.help_menu.add_command(label=t("menu.donate"), command=self.donate)
        self.help_menu.add_command(label=t("menu.about"), command=self.about)
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

    def check_updates(self):
        # Run the network call off the UI thread; report back via self.after.
        threading.Thread(target=self._do_check_updates, daemon=True).start()

    def _do_check_updates(self):
        result = check_for_update(Utils.APP_VERSION)
        self.after(0, lambda: self._check_updates_done(result))

    def _check_updates_done(self, result):
        top = self.winfo_toplevel()
        if result["available"]:
            open_page = ask_yes_no(
                top,
                t("update.available_title"),
                t("update.available_msg", version=result["latest"]),
            )
            if open_page:
                webbrowser.open_new(result["url"])
        elif result["latest"] is not None:
            show_success_toast(top, t("update.uptodate_msg"), t("update.uptodate_title"))
        else:
            show_error_toast(top, t("update.failed_msg"), t("update.failed_title"))

    def donate(self):
        webbrowser.open_new(DONATE_URL)

    def about(self):
        show_about(self.parent)
