from tkinter import *
import tkinter as tk
import threading
import ttkbootstrap as ttk
from widget.tooltip import ToolTip
from core import Utils
from widget.spinner import Spinner
from widget.toast_notification import show_success_toast, show_error_toast

class SecretFrame(Frame):

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.jenkins_requestor = parent.jenkins_requestor

        self.secret_label = Label(self, text="Secret", width=6, font=("Segoe UI", 10))
        self.container_secret_frame = Frame(self)
        self.container_secret_frame.columnconfigure(0, weight=1)

        self.secret_value_entry = ttk.Entry(self.container_secret_frame, width=40, font=("Segoe UI", 10), show="*")
        self._secret_visible = False
        self.toggle_secret_button = ttk.Button(self.container_secret_frame, text="👁", width=3, command=self._toggle_secret)
        ToolTip(self.toggle_secret_button, text="Show / hide secret")
        self.copy_secret_button = ttk.Button(self.container_secret_frame, text="📋")
        self.copy_secret_button.bind("<Button-1>", lambda event: Utils.copy_to_clipboard(self, event, self.secret_value_entry))
        ToolTip(self.copy_secret_button, text="Copy secret")
        self.delete_button = ttk.Button(self.container_secret_frame, text="🗑", bootstyle="danger", command=self._confirm_delete)
        ToolTip(self.delete_button, text="Delete credential")

        self.secret_label.pack(padx=10, pady=(10, 0), anchor="w")
        self.container_secret_frame.pack(fill="x", padx=10, pady=5)

        self.secret_value_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.toggle_secret_button.grid(row=0, column=1, padx=(0, 5))
        self.copy_secret_button.grid(row=0, column=2)
        self.delete_button.grid(row=0, column=3, padx=(5, 0))

        self.edit_button = ttk.Button(self, text="📝")
        self.edit_button.pack(padx=10, pady=(10, 0), anchor="w")
        self.edit_button.bind("<Button-1>", lambda event: self.update_mode())
        ToolTip(self.edit_button, text="Edit")

        self.save_button = ttk.Button(self, text="✅", bootstyle="success")
        self.save_button.bind("<Button-1>", lambda event: self.save())
        ToolTip(self.save_button, text="Save changes")

        self.spinner = Spinner(self)

    def update_mode(self):
        self.current_secret = self.secret_value_entry.get()
        self.secret_value_entry.config(state=tk.NORMAL)
        self.edit_button.pack_forget()
        self.save_button.pack(padx=10, pady=(10, 0), anchor="w")
        self.after(100, lambda: self.secret_value_entry.focus_set())

    def save(self):
        secret = self.secret_value_entry.get()
        self.save_button.pack_forget()
        self.spinner.pack(padx=10, pady=(10, 0), anchor="w")
        self.spinner.start()
        threading.Thread(target=self._do_save, args=(secret,), daemon=True).start()

    def _do_save(self, secret):
        success, msg = self.jenkins_requestor.update_credential(
            "SecretText", credential_id=self.id, secret=secret
        )
        self.after(0, lambda: self._save_done(success, msg))

    def _save_done(self, success, msg):
        self.spinner.stop()
        self.spinner.pack_forget()
        self.edit_button.pack(padx=10, pady=(10, 0), anchor="w")
        self.secret_value_entry.config(state="readonly")
        if success:
            show_success_toast(self.winfo_toplevel(), f"'{self.id}' updated", "Saved")
        else:
            self.set_value(self.current_secret)
            show_error_toast(self.winfo_toplevel(), msg, "Error")

    def _confirm_delete(self):
        if not Utils.confirm_delete(self.winfo_toplevel(), self.id):
            return
        self.delete_button.config(state=tk.DISABLED)
        threading.Thread(target=self._do_delete, args=(self.id,), daemon=True).start()

    def _do_delete(self, credential_id):
        success, msg = self.jenkins_requestor.delete_credential(credential_id)
        self.after(0, lambda: self._delete_done(success, msg))

    def _delete_done(self, success, msg):
        if success:
            self.parent.on_delete(self.id)
        else:
            self.delete_button.config(state=tk.NORMAL)
            show_error_toast(self.winfo_toplevel(), msg, "Error")

    def _toggle_secret(self):
        self._secret_visible = not self._secret_visible
        self.secret_value_entry.configure(show="" if self._secret_visible else "*")

    def set_id(self, id):
        self.id = id
        self.delete_button.config(state=tk.NORMAL)  # re-enable for the new credential

    def set_value(self, secret):
        self.secret_value_entry.config(state=tk.NORMAL)
        self.secret_value_entry.delete(0, END)
        self.secret_value_entry.insert(0, secret)
        self.secret_value_entry.config(state="readonly")
        self._secret_visible = False  # each new credential starts masked
        self.secret_value_entry.configure(show="*")
