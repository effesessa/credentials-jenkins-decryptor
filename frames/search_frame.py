from tkinter import *
import tkinter as tk
import threading
from frames import result_frame
from ttkbootstrap import ttk
from widget.spinner import Spinner
from core import *
from widget.toast_notification import show_warning_toast, show_error_toast, show_info_toast

class SearchFrame(Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.jenkins_requestor = parent.jenkins_requestor
        self.placeholder_text = "Insert credential ID"
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=10)
        self.build_canvas()
        self.word_entry = ttk.Entry(self, width=50, font=("Segoe UI", 10))
        self.word_entry.insert(0, self.placeholder_text)
        self.word_entry.pack(pady=10)
        self.word_entry.bind("<Return>", lambda event: self.search())
        self.word_entry.bind("<FocusOut>", lambda event: self.on_focus_out(event=event))
        self.word_entry.bind("<FocusIn>", lambda event: self.on_focus_in(event=event))
        self.spinner = Spinner(self)
        self.bind("<Button-1>", self.on_focus_out)
        self.build_footer_frame()

    def tkraise(self, aboveThis=None):
        self.server_url_footer_label.config(text=Utils.get_server_url(self.parent.config))
        self._check_connection()
        return super().tkraise(aboveThis)

    def on_focus_in(self, event):
        if self.word_entry.get() == self.placeholder_text:
            self.word_entry.delete(0, "end")

    def on_focus_out(self, event):
        if self.word_entry.get() == "":
            self.word_entry.insert(0, self.placeholder_text)
        self.focus()

    def search(self):
        if not Utils.verify_settings(self.parent.config):
            show_warning_toast(self.winfo_toplevel(), "Missing server, username and/or password", "Settings")
            return
        search_word = self.word_entry.get()
        if not search_word or search_word == self.placeholder_text:
            return
        self._show_loading(True)
        threading.Thread(target=self._do_search, args=(search_word,), daemon=True).start()

    def _do_search(self, search_word):
        try:
            response = self.parent.script_executor.execute(
                Utils.resource_path('groovy/find_contains.groovy'), {'STR': search_word}
            )
            if response.status_code != 200:
                self.after(0, lambda: self._search_error("Wrong server, username and/or password"))
                return
            self.after(0, lambda: self._search_done(response, search_word))
        except Exception as e:
            self.after(0, lambda: self._search_error(str(e)))

    def _search_done(self, response, search_word):
        self._show_loading(False)
        if "not found" in response.text.lower():
            show_info_toast(self.winfo_toplevel(), f"No credentials found for: {search_word}", "Not Found")
            return
        page2_frame = self.parent.frames[result_frame.ResultFrame]
        page2_frame.update_listbox(response.text.splitlines())
        self.parent.show_frame(result_frame.ResultFrame)

    def _search_error(self, msg):
        self._show_loading(False)
        show_error_toast(self.winfo_toplevel(), msg, "Error")

    def _show_loading(self, loading):
        if loading:
            self.word_entry.delete(0, tk.END)
            self.word_entry.config(state=tk.DISABLED)
            self.spinner.pack(pady=5)
            self.spinner.start()
        else:
            self.spinner.stop()
            self.spinner.pack_forget()
            self.word_entry.config(state=tk.NORMAL)

    def build_canvas(self):
        CANVAS_WIDTH = 192
        CANVAS_HEIGHT = 210
        LOGO_SIZE = (192, 192)
        LOGO_Y_POSITION = (CANVAS_HEIGHT - LOGO_SIZE[1]) // 2 + 20
        self.canvas = tk.Canvas(self, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="white", border=0, borderwidth=0, highlightthickness=0)
        self.canvas.pack()
        self.photo_logo = Utils.load_and_resize_image(Utils.resource_path("images/jenkinsd-transformed.webp"), LOGO_SIZE)
        self.canvas.create_image(0, LOGO_Y_POSITION, image=self.photo_logo, anchor=tk.NW)

    def build_footer_frame(self):
        self.footer_frame = Frame(self)
        self.footer_frame.pack(side=BOTTOM, fill=X, pady=10)
        Label(self.footer_frame, text=Utils.COPYRIGHT_TEXT, font=("Segoe UI", 8), fg="grey").pack(side=LEFT, padx=(10, 0))
        self.server_url_footer_label = Label(self.footer_frame, text=Utils.get_server_url(self.parent.config), font=("Segoe UI", 8), fg="grey")
        self.server_url_footer_label.pack(side=RIGHT, padx=(0, 10))
        self.status_dot = Label(self.footer_frame, text="●", font=("Segoe UI", 10), fg="grey")
        self.status_dot.pack(side=RIGHT, padx=(0, 4))
        # L'heartbeat parte dopo il primo intervallo: il check immediato di
        # avvio lo fa già tkraise(), così non c'è un doppione a t=0.
        self.after(30000, self._schedule_status_check)

    def _schedule_status_check(self):
        self._check_connection()
        self.after(30000, self._schedule_status_check)

    def _check_connection(self):
        if not Utils.verify_settings(self.parent.config):
            self.status_dot.config(fg="grey")
            return
        # Show the amber "checking" color only when the state is unknown (first
        # check / grey). On periodic re-checks keep the last known color so the
        # dot doesn't flicker amber->green every 30s (which reads as red->green).
        if self.status_dot.cget("fg") == "grey":
            self.status_dot.config(fg="#f0ad4e")
        threading.Thread(target=self._do_status_check, daemon=True).start()

    def _do_status_check(self):
        try:
            ok = bool(self.parent.jenkins_requestor.test_auth())
        except Exception:
            ok = False
        self.after(0, lambda: self.status_dot.config(fg="#5cb85c" if ok else "#d9534f"))
