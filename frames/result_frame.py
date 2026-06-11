from tkinter import *
import tkinter as tk
import threading
from tkinter import messagebox
from tkinter import filedialog
import ttkbootstrap as ttk
from widget.tooltip import ToolTip
from core import *
from frames.username_password_frame import UsernamePasswordFrame
from frames.secret_frame import SecretFrame
from frames.search_frame import SearchFrame
from widget.spinner import Spinner
from widget.toast_notification import show_success_toast, show_error_toast

class ResultFrame(Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.jenkins_requestor = parent.jenkins_requestor
        self.grid_columnconfigure(0, weight=1, minsize=380)
        self.grid_columnconfigure(1, weight=2, minsize=420)
        self.grid_rowconfigure(0, weight=1)
        self.left = Frame(self)
        self.right = Frame(self)
        self.right.jenkins_requestor = self.jenkins_requestor
        self.right.on_delete = self._on_credential_deleted
        self.left.grid(row=0, column=0, sticky="nsew")
        self.right.grid(row=0, column=1, sticky="nsew")
        self.build_left_frame()
        self.build_right_frame()

    def build_right_frame(self):
        self.id_label = Label(self.right, text="ID", font=("Segoe UI", 10))
        self.container_id_frame = Frame(self.right)
        self.container_id_frame.columnconfigure(0, weight=1)
        self.id_value_entry = ttk.Entry(self.container_id_frame, width=40, font=("Segoe UI", 10))
        self.copy_id_button = ttk.Button(self.container_id_frame, text="📋")
        self.copy_id_button.bind("<Button-1>", lambda event: Utils.copy_to_clipboard(self, event, self.id_value_entry))
        ToolTip(self.copy_id_button, text="Copy ID")
        self.id_value_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.copy_id_button.grid(row=0, column=1)
        self.file_scrolled_text = ttk.ScrolledText(self.right, wrap="word", height=10, width=50)
        self.file_scrolled_text.insert("1.0", "")
        self.username_password_frame = UsernamePasswordFrame(self.right)
        self.secret_frame = SecretFrame(self.right)
        self.file_delete_button = ttk.Button(self.right, text="🗑", bootstyle="danger", command=self._confirm_file_delete)
        ToolTip(self.file_delete_button, text="Delete credential")
        self.detail_spinner = Spinner(self.right)
        self.context_menu = Menu(self, tearoff=0)
        self.context_menu.add_command(label="download", command=self.download_text)
        self.file_scrolled_text.bind("<Button-3>", self.show_context_menu)

    def build_left_frame(self):
        self.frame_box = Frame(self.left)
        self.frame_box.pack(fill="both", expand=True, padx=10, pady=10)
        self.id_credentials_list_box = Listbox(self.frame_box, font=("Segoe UI", 10), selectmode=tk.SINGLE)
        self.id_credentials_list_box.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar = tk.Scrollbar(self.frame_box, orient=tk.VERTICAL, command=self.id_credentials_list_box.yview)
        scrollbar.pack(side="right", fill="y", pady=10)
        self.id_credentials_list_box.config(yscrollcommand=scrollbar.set)
        self.id_credentials_list_box.bind("<<ListboxSelect>>", self.on_select)
        self.back_button = ttk.Button(self.left, text="◀", width=5, command=lambda: self.go_back())
        self.back_button.pack(pady=10)

    def download_text(self):
        file_path = filedialog.asksaveasfilename(defaultextension="",
            initialfile=self.credential_id_selected,
            filetypes=[("All files", "*.*")],
            title="Save file")
        if file_path:
            with open(file_path, "w", newline="\n") as file:
                file.write(self.output_from_selected)

    def show_context_menu(self, event):
        self.context_menu.post(event.x_root, event.y_root)

    def _confirm_file_delete(self):
        credential_id = self.credential_id_selected
        if not Utils.confirm_delete(self.winfo_toplevel(), credential_id):
            return
        self.file_delete_button.config(state=tk.DISABLED)
        threading.Thread(target=self._do_file_delete, args=(credential_id,), daemon=True).start()

    def _do_file_delete(self, credential_id):
        success, msg = self.jenkins_requestor.delete_credential(credential_id)
        self.after(0, lambda: self._file_delete_done(success, msg, credential_id))

    def _file_delete_done(self, success, msg, credential_id):
        if success:
            self._on_credential_deleted(credential_id)
        else:
            self.file_delete_button.config(state=tk.NORMAL)
            show_error_toast(self.winfo_toplevel(), msg, "Error")

    def _on_credential_deleted(self, credential_id):
        items = list(self.id_credentials_list_box.get(0, tk.END))
        if credential_id in items:
            self.id_credentials_list_box.delete(items.index(credential_id))
        self._hide_id_field()
        self.username_password_frame.pack_forget()
        self.secret_frame.pack_forget()
        self.file_scrolled_text.pack_forget()
        self.file_delete_button.pack_forget()
        show_success_toast(self.winfo_toplevel(), f"'{credential_id}' deleted", "Deleted")

    def go_back(self):
        self.file_scrolled_text.config(state=tk.NORMAL)
        self.file_scrolled_text.delete('1.0', END)
        self.file_scrolled_text.config(state=tk.DISABLED)
        self.file_scrolled_text.pack_forget()
        self._hide_id_field()
        self.username_password_frame.pack_forget()
        self.secret_frame.pack_forget()
        self.file_delete_button.pack_forget()
        self.parent.show_frame(SearchFrame)

    def update_listbox(self, elements):
        self.id_credentials_list_box.delete(0, tk.END)
        items = elements[1:]
        if items:
            self.id_credentials_list_box.insert(tk.END, *items)

    def on_select(self, event):
        selection = event.widget.curselection()
        if not selection:
            return
        index = selection[0]
        self.credential_id_selected = event.widget.get(index)
        self.id_credentials_list_box.config(state=tk.DISABLED)
        self._show_detail_loading(True)
        threading.Thread(
            target=self._do_load_credential, args=(self.credential_id_selected,), daemon=True
        ).start()

    def _do_load_credential(self, credential_id):
        try:
            result_value = self.parent.script_executor.execute(
                Utils.resource_path('groovy/get_value.groovy'), {'CREDENTIAL_ID': credential_id}
            )
            self.after(0, lambda: self._load_credential_done(credential_id, result_value))
        except Exception as e:
            self.after(0, lambda: self._load_credential_error(str(e)))

    def _load_credential_done(self, credential_id, result_value):
        self._show_detail_loading(False)
        self.id_credentials_list_box.config(state=tk.NORMAL)
        try:
            self.credential_class, self.output_from_selected = Utils.split_type_class_from_content(result_value.text)
            if "not found" in self.credential_class or "not supported" in self.credential_class:
                show_error_toast(self.winfo_toplevel(), self.credential_class, "Error")
                return
            self.show_credential(self.credential_class, credential_id, self.output_from_selected)
        except Exception as e:
            show_error_toast(self.winfo_toplevel(), str(e), "Error")
        finally:
            self.credential_class = ""

    def _load_credential_error(self, msg):
        self._show_detail_loading(False)
        self.id_credentials_list_box.config(state=tk.NORMAL)
        show_error_toast(self.winfo_toplevel(), msg, "Error")

    def _show_detail_loading(self, loading):
        if loading:
            self._hide_id_field()
            self.username_password_frame.pack_forget()
            self.secret_frame.pack_forget()
            self.file_scrolled_text.pack_forget()
            self.file_delete_button.pack_forget()
            self.detail_spinner.pack(pady=20)
            self.detail_spinner.start()
        else:
            self.detail_spinner.stop()
            self.detail_spinner.pack_forget()

    def _set_id_field(self, credential_id):
        self.id_value_entry.config(state=tk.NORMAL)
        self.id_value_entry.delete(0, END)
        self.id_value_entry.insert(0, credential_id)
        self.id_value_entry.config(state="readonly")
        self.id_label.pack(padx=10, pady=(10, 0), anchor="w")
        self.container_id_frame.pack(fill="x", padx=10, pady=5)

    def _hide_id_field(self):
        self.id_label.pack_forget()
        self.container_id_frame.pack_forget()

    def show_credential(self, type, credential_id, text):
        self._set_id_field(credential_id)
        type_name = type.split("Type: ")[1]
        if type_name == "FileCredentials":
            self.username_password_frame.pack_forget()
            self.secret_frame.pack_forget()
            self.file_scrolled_text.config(state=tk.NORMAL)
            self.file_scrolled_text.delete('1.0', END)
            self.file_scrolled_text.insert("1.0", text)
            self.file_scrolled_text.config(state=tk.DISABLED)
            self.file_scrolled_text.pack(fill="both", expand=True, padx=10, pady=10)
            self.file_delete_button.config(state=tk.NORMAL)  # re-enable for the new credential
            self.file_delete_button.pack(padx=10, pady=(5, 10), anchor="w")
        elif type_name == "StandardUsernamePasswordCredentials":
            self.file_scrolled_text.pack_forget()
            self.file_delete_button.pack_forget()
            self.secret_frame.pack_forget()
            username_password_text = text.splitlines()
            user = username_password_text[0].replace("Username:", "").strip()
            psw = username_password_text[1].replace("Password:", "").strip()
            self.username_password_frame.set_username(user)
            self.username_password_frame.set_password(psw)
            self.username_password_frame.set_id(credential_id)
            self.username_password_frame.pack(fill=X)
        else:
            self.username_password_frame.pack_forget()
            self.file_scrolled_text.pack_forget()
            self.file_delete_button.pack_forget()
            self.secret_frame.set_id(credential_id)
            self.secret_frame.set_value(text.strip())
            self.secret_frame.pack(fill=X)
