import ttkbootstrap as ttk
from core.i18n import t


def ask_yes_no(parent, title, message, confirm_style="primary"):
    """Modal Yes/No dialog with explicit English buttons (the native messagebox
    localizes its buttons to the OS language, e.g. 'Sì'/'No'). Returns True if
    the user clicks Yes, False otherwise."""
    dialog = ttk.Toplevel(parent)
    dialog.title(title)
    dialog.resizable(False, False)
    dialog.transient(parent)

    result = {"value": False}

    container = ttk.Frame(dialog, padding=20)
    container.pack(fill="both", expand=True)
    ttk.Label(container, text=message, justify="left", wraplength=340).pack(anchor="w")

    btns = ttk.Frame(container)
    btns.pack(fill="x", pady=(20, 0))

    def choose(value):
        result["value"] = value
        dialog.destroy()

    no_btn = ttk.Button(btns, text=t("common.no"), bootstyle="secondary", width=8, command=lambda: choose(False))
    no_btn.pack(side="right")
    ttk.Button(btns, text=t("common.yes"), bootstyle=confirm_style, width=8, command=lambda: choose(True)).pack(side="right", padx=(0, 8))

    dialog.bind("<Escape>", lambda e: choose(False))
    dialog.protocol("WM_DELETE_WINDOW", lambda: choose(False))

    # Center over the parent window (multi-monitor safe).
    dialog.update_idletasks()
    w = dialog.winfo_reqwidth()
    h = dialog.winfo_reqheight()
    x = parent.winfo_rootx() + (parent.winfo_width() - w) // 2
    y = parent.winfo_rooty() + (parent.winfo_height() - h) // 2
    dialog.geometry(f"+{x}+{y}")

    no_btn.focus_set()  # safe default: Enter/space won't trigger the destructive action
    dialog.grab_set()
    parent.wait_window(dialog)
    return result["value"]
