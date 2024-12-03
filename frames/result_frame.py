from tkinter import *
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
import ttkbootstrap as ttk
from core import *
from frames.username_password_frame import UsernamePasswordFrame
from frames.secret_frame import SecretFrame
from frames.search_frame import SearchFrame

class ResultFrame(Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.grid_columnconfigure(0, weight=1, minsize=380)
        self.grid_columnconfigure(1, weight=2, minsize=420)
        self.grid_rowconfigure(0, weight=1)
        self.left = Frame(self)
        self.right = Frame(self)
        self.left.grid(row=0,column=0, sticky="nsew")
        self.right.grid(row=0,column=1, sticky="nsew")
        self.build_left_frame()
        self.build_right_frame()
    
    
    def build_right_frame(self):
        self.credential_id_label = Label(self.right, text="")
        self.file_scrolled_text = ttk.ScrolledText(self.right, wrap="word", height=10, width=50)
        self.file_scrolled_text.insert("1.0", "")
        self.label_secret = Label(self.right, text="Secret", width=6, font=("Segoe UI", 10))
        self.secret_value_entry = ttk.Entry(self.right, text="", width=40, font=("Segoe UI", 10))
        self.username_password_frame = UsernamePasswordFrame(self.right)
        self.secret_frame = SecretFrame(self.right)
        self.context_menu = Menu(self, tearoff=0)
        self.context_menu.add_command(label="download", command=self.download_text)
        self.file_scrolled_text.bind("<Button-3>", self.show_context_menu)

    def build_left_frame(self):
        self.label = Label(self.left, text="")
        self.label.pack(fill="x")
        self.frame_box = Frame(self.left)
        self.frame_box.pack(fill="both", expand=True, padx=10, pady=10)
        self.id_credentials_list_box = Listbox(self.frame_box, font=("Segoe UI", 10), selectmode=tk.SINGLE)
        self.id_credentials_list_box.pack(side="left", fill="both", expand=True, padx=(10,0), pady=10)
        scrollbar = tk.Scrollbar(self.frame_box, orient=tk.VERTICAL, command=self.id_credentials_list_box.yview)
        scrollbar.pack(side="right", fill="y", pady=10)
        self.id_credentials_list_box.config(yscrollcommand=scrollbar.set)
        self.id_credentials_list_box.bind("<<ListboxSelect>>", self.on_select)
        self.back_button = ttk.Button(self.left, text="Back", command=lambda: self.go_back())
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

    def go_back(self):
        self.file_scrolled_text.config(state=tk.NORMAL)
        self.file_scrolled_text.delete('1.0', END)
        self.file_scrolled_text.config(state=tk.DISABLED)
        self.file_scrolled_text.pack_forget()
        self.credential_id_label.pack_forget()
        self.username_password_frame.pack_forget()
        self.secret_frame.pack_forget()
        self.parent.show_frame(SearchFrame)
    
    def update_listbox(self, elements):
        self.id_credentials_list_box.delete(0, tk.END)
        self.label.config(text=elements[0])
        for element in elements[1:]:
            self.id_credentials_list_box.insert(tk.END, element)
    
    def on_select(self, event):
        self.id_credentials_list_box.config(state=tk.DISABLED)
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            self.credential_id_selected = event.widget.get(index)
            try:
                result_value = self.parent.script_executor.execute(Utils.resource_path('groovy/get_value.groovy'), {'CREDENTIAL_ID': self.credential_id_selected})
                self.credential_class, self.output_from_selected = Utils.split_type_class_from_content(result_value.text)
                if "not found" in self.credential_class or "not supported" in self.credential_class:
                    tk.messagebox.showerror("Error", self.credential_class)
                    return
                self.show_credential(self.credential_class, self.credential_id_selected, self.output_from_selected)
            except Exception as e:
                tk.messagebox.showerror("Error", f"{str(e)}")
            finally:
                self.id_credentials_list_box.config(state=tk.NORMAL)
        self.id_credentials_list_box.config(state=tk.NORMAL)
        self.credential_class = ""
    
    def show_credential(self, type, credential_id, text):
        self.credential_id_label.config(text=credential_id)
        self.credential_id_label.pack(fill="x")
        type_name = type.split("Type: ")[1]
        if type_name == "FileCredentials":
            self.username_password_frame.pack_forget()
            self.secret_frame.pack_forget()
            self.file_scrolled_text.config(state=tk.NORMAL)
            self.file_scrolled_text.delete('1.0', END)
            self.file_scrolled_text.insert("1.0",text)
            self.file_scrolled_text.config(state=tk.DISABLED)
            self.file_scrolled_text.pack(fill="both", expand=True, padx=10, pady=10)
        elif type_name == "StandardUsernamePasswordCredentials":
            self.file_scrolled_text.pack_forget()
            self.secret_frame.pack_forget()
            username_password_text = text.splitlines()
            user = username_password_text[0].replace("Username:", "").strip()
            psw = username_password_text[1].replace("Password:", "").strip()
            self.username_password_frame.set_username(user)
            self.username_password_frame.set_password(psw)
            self.username_password_frame.pack(fill=X)
        else:
            self.username_password_frame.pack_forget()
            self.file_scrolled_text.pack_forget()
            self.secret_frame.set_value(text.strip())
            self.secret_frame.pack(fill=X)