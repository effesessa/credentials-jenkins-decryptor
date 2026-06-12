from tkinter import *
import sys
import ttkbootstrap as ttk
from frames import *
from core import *
from  widget.menubar import MenuBar
import configparser
from widget.toast_notification import show_success_toast, show_error_toast, show_warning_toast, show_info_toast


def _enable_dpi_awareness():
    # Must run BEFORE the Tk() root is created: Tk reads the screen DPI at
    # interpreter startup. Declaring the process DPI-aware stops Windows from
    # bitmap-stretching the window (which blurs all text), so Tk renders crisp
    # at the real pixel density. Windows-only; degrades gracefully elsewhere.
    if sys.platform != "win32":
        return
    import ctypes
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)  # System DPI Aware (Win 8.1+)
    except (AttributeError, OSError):
        try:
            ctypes.windll.user32.SetProcessDPIAware()  # fallback for older Windows
        except (AttributeError, OSError):
            pass


class App(Tk):
    def __init__(self):
        _enable_dpi_awareness()
        super().__init__()
        self.withdraw()  # hide the window until the UI is ready (avoids the flash)
        self.config = configparser.ConfigParser()
        i18n.set_language(Utils.get_language(self.config))  # load saved language first
        self.style = ttk.Style(Utils.get_theme(self.config))
        self.title(f"Credentials Jenkins Decryptor v{Utils.APP_VERSION}")
        Utils.set_icon(self)
        # Scale the base window by the real DPI factor so the bigger DPI-aware
        # fonts still fit (96 dpi = 100% = factor 1.0).
        dpi_factor = self.winfo_fpixels('1i') / 96
        width, height = round(800 * dpi_factor), round(500 * dpi_factor)
        self.geometry(Utils.in_the_center_of_screen(self, width, height))
        self.minsize(width, height)
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

    def apply_language(self, language):
        """Switch language live: persist the choice, set the active language and
        rebuild the whole UI so every widget is recreated reading the new texts.
        In-progress Settings edits are preserved across the rebuild."""
        if language == i18n.get_language():
            return
        Utils.set_language(self.config, language)
        i18n.set_language(language)
        settings = self.frames.get(SettingsFrame)
        form_state = settings.get_form_state() if settings else None
        self.rebuild_ui(form_state)

    def rebuild_ui(self, settings_state=None):
        # Destroy menubar + every frame and recreate them. The ttk Style (and
        # thus the live theme) lives on App, so it survives the rebuild.
        self.menubar.destroy()
        for frame in self.frames.values():
            frame.destroy()
        self.frames = {}
        self.menubar = MenuBar(self)
        self.init()
        self.init_frames()
        if settings_state is not None:
            self.frames[SettingsFrame].restore_form_state(settings_state)
        # Stay on Settings: the language switch happens there.
        self.show_frame(SettingsFrame)

app = App()
app.mainloop()
