import tkinter as tk
import ttkbootstrap as ttk
import threading
from frames import *
from PIL import Image, ImageTk
from ttkbootstrap.publisher import Publisher
from core.utils import Utils
from core.i18n import t
from widget.toast_notification import show_success_toast, show_error_toast

class CreateCredentialFrame(tk.Toplevel):

    def __init__(self, parent, jenkins_requestor):
        super().__init__(parent)
        self.parent = parent
        self.jenkins_requestor = jenkins_requestor
        self.title(t("create.title"))
        # Scale the base size by the real DPI factor so the bigger DPI-aware
        # fonts still fit (96 dpi = 100% = factor 1.0), matching the main window.
        dpi_factor = self.winfo_fpixels('1i') / 96
        self.geometry(f"{round(400 * dpi_factor)}x{round(320 * dpi_factor)}")  # window size
        # dropdown to pick the credential type, an input for the credential id, and
        # depending on the chosen type: one input for the secret (SecretText) or two
        # inputs (UsernamePassword)
        self.create_widgets()
        self.focus_set()
        self.grab_set()
        self.center_window()

    def create_widgets(self):
        self.create_credential_type_label = ttk.Label(self, text=t("create.type"))
        self.create_credential_type_label.pack(padx=10, pady=(5, 0), anchor="w")

        icon_combo_frame = ttk.Frame(self)
        icon_combo_frame.pack(padx=10, pady=(0, 0), anchor="w")
        key_img = Image.open(Utils.resource_path("images/key-4.png")).resize((20, 20), Image.Resampling.LANCZOS)
        self.key_icon = ImageTk.PhotoImage(key_img)
        ttk.Label(icon_combo_frame, image=(self.key_icon)).pack(side="left", padx=(0, 5))
        self.create_credential_type_dropdown = ttk.Combobox(icon_combo_frame, values=["SecretText", "UsernamePassword"], font=("Segoe UI", 10), state="readonly")
        self.create_credential_type_dropdown.current(0)
        self.create_credential_type_dropdown.pack(padx=10, pady=5, anchor="w")
        self.create_credential_type_dropdown.bind("<Button-1>", self.open_dropdown)
        self.create_credential_type_dropdown.bind("<<ComboboxSelected>>", self.update_fields)

        ttk.Label(self, text=t("create.id")).pack(padx=10, pady=(5, 0), anchor="w")
        self.credential_id_entry = ttk.Entry(self)
        self.credential_id_entry.pack(padx=10, pady=(0, 10), fill="x")

        # dynamic container for the entries
        self.fields_frame = ttk.Frame(self)
        self.fields_frame.pack(padx=10, pady=(0, 10), fill="both", expand=True)

        # initialize the fields
        self.build_fields("SecretText")

        self.bottom_frame = tk.Frame(self)
        self.bottom_frame.pack(side=tk.BOTTOM, fill="x", pady=10)
        self.save_button = ttk.Button(self.bottom_frame, text=t("create.button"), width=10, command=self.save)
        self.save_button.pack(side=tk.RIGHT, padx=10)
        self.back_button = ttk.Button(self.bottom_frame, text=t("common.back"), width=10, command=self.back)
        self.back_button.pack(side=tk.LEFT, padx=10)

    def update_fields(self, event):
        selected = self.create_credential_type_dropdown.get()
        event.widget.selection_clear()
        self.build_fields(selected)

    def build_fields(self, field_type):
        # clear the old widgets
        for widget in self.fields_frame.winfo_children():
            widget.destroy()

        if field_type == "SecretText":
            ttk.Label(self.fields_frame, text=t("create.secret")).pack(anchor="w")
            ttk.Entry(self.fields_frame).pack(fill="x")
        elif field_type == "UsernamePassword":
            ttk.Label(self.fields_frame, text=t("create.username")).pack(anchor="w")
            ttk.Entry(self.fields_frame).pack(fill="x", pady=(0, 5))
            ttk.Label(self.fields_frame, text=t("create.password")).pack(anchor="w")
            ttk.Entry(self.fields_frame, show="*").pack(fill="x")
    def open_dropdown(self, event):
        self.create_credential_type_dropdown.event_generate('<Down>')

    def clear_selection(self, event):
        event.widget.selection_clear()

    def center_window(self):
        # Center over the parent window (not the whole screen), so the dialog
        # follows the app wherever it has been moved — same as the About dialog.
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        px = self.parent.winfo_rootx()
        py = self.parent.winfo_rooty()
        pw = self.parent.winfo_width()
        ph = self.parent.winfo_height()
        x = px + (pw - w) // 2
        y = py + (ph - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def save(self):
        if not self.credential_id_entry.get():
            show_error_toast(self, t("create.err_id"), t("toast.error"))
            return
        if self.create_credential_type_dropdown.get() == "SecretText" and not self.fields_frame.winfo_children()[1].get():
            show_error_toast(self, t("create.err_secret"), t("toast.error"))
            return
        if self.create_credential_type_dropdown.get() == "UsernamePassword" and not self.fields_frame.winfo_children()[1].get():
            show_error_toast(self, t("create.err_username"), t("toast.error"))
            return
        if self.create_credential_type_dropdown.get() == "UsernamePassword" and not self.fields_frame.winfo_children()[3].get():
            show_error_toast(self, t("create.err_password"), t("toast.error"))
            return
        cred_type = self.create_credential_type_dropdown.get()
        cred_id = self.credential_id_entry.get()
        if cred_type == "SecretText":
            kwargs = dict(credential_id=cred_id, secret=self.fields_frame.winfo_children()[1].get())
        else:
            kwargs = dict(credential_id=cred_id,
                          username=self.fields_frame.winfo_children()[1].get(),
                          password=self.fields_frame.winfo_children()[3].get())
        # Run the network call off the UI thread so the dialog doesn't freeze.
        self.save_button.config(state="disabled")
        threading.Thread(target=self._do_create, args=(cred_type, kwargs, cred_id), daemon=True).start()

    def _do_create(self, cred_type, kwargs, cred_id):
        success, msg = self.jenkins_requestor.post_create_credential(cred_type, **kwargs)
        self.after(0, lambda: self._create_done(success, msg, cred_id))

    def _create_done(self, success, msg, cred_id):
        if success:
            self.destroy()
            show_success_toast(self.parent, t("create.created", id=cred_id), t("toast.created"))
        else:
            self.save_button.config(state="normal")
            show_error_toast(self, msg, t("toast.error"))

    def back(self):
        self.destroy()

    def destroy(self):
        # ttkbootstrap subscribes every Combobox to the Publisher for theme
        # updates but never unsubscribes on widget destruction. Without this,
        # changing the theme later iterates the dead combobox and raises
        # "bad window path name". Unsubscribe before the widget is gone.
        try:
            Publisher.unsubscribe(self.create_credential_type_dropdown)
        except Exception:
            pass
        super().destroy()