import os
import platform
import sys
from PIL import Image, ImageTk
from ttkbootstrap import ttk
import configparser
from tkinter import simpledialog
from widget.confirm_dialog import ask_yes_no

# The OS keyring is optional: if the package or a backend is missing (e.g. a
# headless Linux box with no Secret Service), the app keeps working by falling
# back to the legacy plaintext token in config.ini.
try:
    import keyring
    from keyring.errors import KeyringError
    _KEYRING_AVAILABLE = True
except Exception:
    _KEYRING_AVAILABLE = False

class Utils:

    APP_VERSION = "2.0"
    COPYRIGHT_TEXT = "Author: effesessa"
    _KEYRING_SERVICE = "jenkins-decryptor"

    @staticmethod
    def confirm_delete(parent, credential_id):
        """Two-step delete confirmation. Returns True only if the user clicks
        Yes and then types 'delete' to confirm."""
        confirmed = ask_yes_no(
            parent,
            "Confirm Delete",
            f"Are you sure you want to permanently delete:\n\n    \"{credential_id}\"\n\nThis action cannot be undone.",
            confirm_style="danger",
        )
        if not confirmed:
            return False
        answer = simpledialog.askstring(
            "Confirm Delete",
            f'Type "delete" to permanently delete "{credential_id}":',
            parent=parent,
        )
        return answer == "delete"
    
    @staticmethod
    def in_the_center_of_screen(widget, width, height):
        screen_width = widget.winfo_screenwidth()
        screen_height = widget.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        return f"{width}x{height}+{x}+{y}"
    
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
    def get_token(username, config: configparser.ConfigParser):
        """Return the API token, preferring the OS keyring and falling back to
        the legacy plaintext token in config.ini, so existing setups keep
        working until the next Save migrates the token into the keyring."""
        if _KEYRING_AVAILABLE and username:
            try:
                token = keyring.get_password(Utils._KEYRING_SERVICE, username)
                if token:
                    return token
            except KeyringError:
                pass
        config_path = Utils.get_config_path(app_name="jenkins-decryptor")
        config.read(config_path)
        return config['settings'].get('token', '') if config.has_section('settings') else ""

    @staticmethod
    def set_token(username, token):
        """Store the token in the OS keyring. Returns True on success, False if
        no backend is available (the caller should then fall back to config)."""
        if not (_KEYRING_AVAILABLE and username):
            return False
        try:
            keyring.set_password(Utils._KEYRING_SERVICE, username, token)
            return True
        except KeyringError:
            return False

    @staticmethod
    def delete_token(username):
        """Remove the token from the keyring (best effort)."""
        if not (_KEYRING_AVAILABLE and username):
            return
        try:
            keyring.delete_password(Utils._KEYRING_SERVICE, username)
        except Exception:
            pass

    @staticmethod
    def verify_settings(config: configparser.ConfigParser):
        config_path = Utils.get_config_path(app_name="jenkins-decryptor")
        config.read(config_path)
        if not config.has_section("settings"):
            return False
        section = config["settings"]
        username = section.get("username", "")
        server_url = section.get("server_url", "")
        token = Utils.get_token(username, config)
        return bool(username and server_url and token)

    @staticmethod
    def set_icon(window):
        if platform.system() == "Windows":
            window.iconbitmap(Utils.resource_path("images/jenkinsd-transformed.ico"))
        else:
            icon = Utils.load_and_resize_image("images/jenkinsd-transformed.webp", (64, 64))
            window.iconphoto(True, icon)
            window._icon_ref = icon

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
