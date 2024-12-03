import os
import platform
import sys
from PIL import Image, ImageTk
import requests
from ttkbootstrap import ttk
import configparser

class Utils:
    
    COPYRIGHT_TEXT = "Author: effesessa"
    
    @staticmethod
    def in_the_center_of_screen(widget, width, height):
        screen_width = widget.winfo_screenwidth()
        screen_height = widget.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        widget.geometry(f"{width}x{height}+{x}+{y}")
    
    @staticmethod
    def load_and_resize_image(image_path, size):
        image = Image.open(Utils.resource_path(image_path))
        image = image.resize(size, Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(image)

    @staticmethod
    def resource_path(relative_path):
        relative_path = relative_path.replace('/', os.sep)
        # PyInstaller
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        # Script Python
        return os.path.join(os.path.abspath("."), relative_path)

    @staticmethod
    def split_type_class_from_content(input_string):
        cred_id_index = input_string.find("Type:")
        if cred_id_index == -1:
            return input_string, ""
        newline_index = input_string.find("\n", cred_id_index)
        if newline_index != -1:
            return (input_string[:newline_index], input_string[newline_index + 1:]) 
        else:
            return (input_string, "")

    @staticmethod
    def is_connected():
        try:
            requests.get("https://www.google.com", timeout=3)
            return True
        except (requests.ConnectionError, requests.Timeout):
            return False

    @staticmethod
    def get_config_path(app_name):
        system = platform.system()  
        if system == "Windows":
            base_path = os.getenv("APPDATA")  # AppData\Roaming
        elif system == "Darwin":  # MacOS
            base_path = os.path.expanduser("~/Library/Application Support")
        else:  # Linux
            base_path = os.path.expanduser("~/.config")
        config_dir = os.path.join(base_path, app_name)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        return os.path.join(config_dir, "config.ini")
    
    @staticmethod
    def get_theme(config: configparser.ConfigParser):
        config_path = Utils.get_config_path(app_name="jenkins-decryptor")
        config.read(config_path)
        theme = config['settings'].get('theme', "darkly") if config.has_section("settings") else "darkly"
        return theme
    
    @staticmethod
    def get_server_url(config:configparser.ConfigParser):
        config_path = Utils.get_config_path(app_name="jenkins-decryptor")
        config.read(config_path)
        server_text = config['settings'].get('server_url', '') if config.has_section('settings') else ""
        return server_text

    @staticmethod
    def verify_settings(config: configparser.ConfigParser):
        config_path = Utils.get_config_path(app_name="jenkins-decryptor")
        config.read(config_path)
        if config.has_section("settings"):
            required_keys = {"token", "username", "server_url"}
            present_keys = set(config.options("settings"))
            return required_keys.issubset(present_keys)
        return False

    @staticmethod
    def copy_to_clipboard(self_widget, event, entry):
        selected_text = entry.get()
        self_widget.clipboard_clear()
        self_widget.clipboard_append(selected_text)
        button = event.widget
        xb = button.winfo_x()
        yb = button.winfo_y()
        toast = ttk.Label(button.master, text="copied!", width=7, background="lightgrey", foreground="black")
        toast.place(x=xb-20, y=yb+10)
        button.master.after(1000, toast.destroy)
