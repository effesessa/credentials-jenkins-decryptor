from tkinter import *
import tkinter as tk
import threading
import ttkbootstrap as ttk
from widget.tooltip import ToolTip
from core.utils import Utils
from widget.spinner import Spinner
from widget.toast_notification import show_success_toast, show_error_toast

class UsernamePasswordFrame(Frame):

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.jenkins_requestor = parent.jenkins_requestor

        self.username_label = Label(self, text="Username", width=8, font=("Segoe UI", 10))
        self.password_label = Label(self, text="Password", width=8, font=("Segoe UI", 10))

        self.container_username_frame = Frame(self)
        self.container_password_frame = Frame(self)
        self.container_username_frame.columnconfigure(0, weight=1)
        self.container_password_frame.columnconfigure(0, weight=1)

        self.username_value_entry = ttk.Entry(self.container_username_frame, text="", width=40, font=("Segoe UI", 10))
        self.copy_username_button = ttk.Button(self.container_username_frame, text="📋")
        self.copy_username_button.bind("<Button-1>", lambda event: Utils.copy_to_clipboard(self, event, self.username_value_entry))
        ToolTip(self.copy_username_button, text="Copy username")

        self.password_value_entry = ttk.Entry(self.container_password_frame, width=40, font=("Segoe UI", 10), show="*")
        self._password_visible = False
        self.toggle_password_button = ttk.Button(self.container_password_frame, text="👁", width=3, command=self._toggle_password)
        ToolTip(self.toggle_password_button, text="Show / hide password")
        self.copy_password_button = ttk.Button(self.container_password_frame, text="📋")
        self.copy_password_button.bind("<Button-1>", lambda event: Utils.copy_to_clipboard(self, event, self.password_value_entry))
        ToolTip(self.copy_password_button, text="Copy password")
        self.delete_button = ttk.Button(self.container_password_frame, text="🗑", bootstyle="danger", command=self._confirm_delete)
        ToolTip(self.delete_button, text="Delete credential")

        self.username_label.pack(padx=10, pady=(10, 0), anchor="w")
        self.container_username_frame.pack(fill="x", padx=10, pady=5)
        self.password_label.pack(padx=10, pady=(10, 0), anchor="w")
        self.container_password_frame.pack(fill="x", padx=10, pady=5)

        self.username_value_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.copy_username_button.grid(row=0, column=1)
        self.password_value_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.toggle_password_button.grid(row=0, column=1, padx=(0, 5))
        self.copy_password_button.grid(row=0, column=2)
        self.delete_button.grid(row=0, column=3, padx=(5, 0))

        self.edit_button = ttk.Button(self, text="📝")
        self.edit_button.pack(padx=10, pady=(10, 0), anchor="w")
        self.edit_button.bind("<Button-1>", lambda event: self.update_mode())
        ToolTip(self.edit_button, text="Edit")

        self.save_button = ttk.Button(self, text="✅", bootstyle="success")
        self.save_button.bind("<Button-1>", lambda event: self.save())
        ToolTip(self.save_button, text="Save changes")

        self.spinner = Spinner(self)

    def save(self):
        username = self.username_value_entry.get()
        password = self.password_value_entry.get()
        self.save_button.pack_forget()
        self.spinner.pack(padx=10, pady=(10, 0), anchor="w")
        self.spinner.start()
        threading.Thread(target=self._do_save, args=(username, password), daemon=True).start()

    def _do_save(self, username, password):
        success, msg = self.jenkins_requestor.update_credential(
            "UsernamePassword", credential_id=self.id,
            username=username, password=password
        )
        self.after(0, lambda: self._save_done(success, msg))

    def _save_done(self, success, msg):
        self.spinner.stop()
        self.spinner.pack_forget()
        self.edit_button.pack(padx=10, pady=(10, 0), anchor="w")
        self.username_value_entry.config(state="readonly")
        self.password_value_entry.config(state="readonly")
        if success:
            show_success_toast(self.winfo_toplevel(), f"'{self.id}' updated", "Saved")
        else:
            self.set_value(self.username_value_entry, self.current_username)
            self.set_value(self.password_value_entry, self.current_password)
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

    def _toggle_password(self):
        self._password_visible = not self._password_visible
        self.password_value_entry.configure(show="" if self._password_visible else "*")

    def update_mode(self):
        self.current_username = self.username_value_entry.get()
        self.current_password = self.password_value_entry.get()
        self.username_value_entry.config(state=tk.NORMAL)
        self.password_value_entry.config(state=tk.NORMAL)
        self.edit_button.pack_forget()
        self.save_button.pack(padx=10, pady=(10, 0), anchor="w")
        # Don't auto-focus a specific field: with two editable fields, forcing
        # focus onto the username made it easy to type the new password into the
        # wrong field. Let the user click the field they actually want to edit.

    def set_username(self, username):
        self.set_value(self.username_value_entry, username)

    def set_password(self, password):
        self.set_value(self.password_value_entry, password)
        self._password_visible = False  # each new credential starts masked
        self.password_value_entry.configure(show="*")

    def set_id(self, id):
        self.id = id
        self.delete_button.config(state=tk.NORMAL)  # re-enable for the new credential

    def set_value(self, entry, text):
        entry.config(state=tk.NORMAL)
        entry.delete(0, END)
        entry.insert(0, text)
        entry.config(state="readonly")
