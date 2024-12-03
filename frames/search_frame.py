from tkinter import *
import tkinter as tk
from frames import result_frame
from ttkbootstrap import ttk
from core import *

class SearchFrame(Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.placeholder_text = "Insert credential ID"
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=10)
        self.build_canvas()
        self.word_entry = ttk.Entry(self, width=50, font=("Segoe UI", 10))
        self.word_entry.insert(0, self.placeholder_text)
        self.word_entry.pack(pady=10)
        self.search_button = Button(self, text="Search", width=10, height=1, font=("Segoe UI", 10), command=self.search)
        self.word_entry.bind("<Return>", lambda event: self.search())
        self.word_entry.bind("<FocusOut>", lambda event: self.on_focus_out(event=event))
        self.word_entry.bind("<FocusIn>", lambda event: self.on_focus_in(event=event))
        self.search_button.pack(pady=10)
        self.bind("<Button-1>", self.on_focus_out)
        self.build_footer_frame()

    def tkraise(self, aboveThis = None):
        self.server_url_footer_label.config(text=Utils.get_server_url(self.parent.config))
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
            tk.messagebox.showwarning("Warning", "Missing server, username and/or password")
            return
        if not self.parent.jenkins_requestor.test_auth():
            tk.messagebox.showwarning("Error", "Wrong server, username and/or password")
            return
        search_word = self.word_entry.get()
        self.word_entry.delete(0, tk.END)
        if not Utils.is_connected():
            tk.messagebox.showerror("Error", "No internet connection")
            return
        response = self.parent.script_executor.execute(Utils.resource_path('groovy/find_contains.groovy'), {'STR': search_word})
        page2_frame = self.parent.frames[result_frame.ResultFrame]
        page2_frame.update_listbox(response.text.splitlines())
        self.parent.show_frame(result_frame.ResultFrame)
        

    def build_canvas(self):
        CANVAS_WIDTH = 192
        CANVAS_HEIGHT = 210
        LOGO_SIZE = (192, 192)
        LOGO_Y_POSITION = (CANVAS_HEIGHT - LOGO_SIZE[1]) // 2 + 20
        self.canvas = tk.Canvas(self, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="white", border=0, borderwidth=0, highlightthickness=0)
        self.canvas.pack()
        self.photo_logo = Utils.load_and_resize_image(Utils.resource_path("images/jenkinsd-transformed.webp"), LOGO_SIZE)
        self.update_idletasks()
        self.canvas.create_image(0, LOGO_Y_POSITION, image=self.photo_logo, anchor=tk.NW)

    def build_footer_frame(self):
        self.footer_frame = Frame(self)
        self.footer_frame.pack(side=BOTTOM, fill=X, pady=10)
        Label(self.footer_frame, text=Utils.COPYRIGHT_TEXT, font=("Segoe UI", 8), fg="grey").pack(side=LEFT, padx=(10, 0))
        self.server_url_footer_label = Label(self.footer_frame, text=Utils.get_server_url(self.parent.config), font=("Segoe UI", 8), fg="grey")
        self.server_url_footer_label.pack(side=RIGHT, padx=(0, 10))
    