import webbrowser
import ttkbootstrap as ttk
from core.utils import Utils
from core.i18n import t

GITHUB_URL = "https://github.com/effesessa/credentials-jenkins-decryptor"
DONATE_URL = "https://www.paypal.com/paypalme/effesessa"


def show_about(parent):
    """Modal About dialog: app name + version, a one-line description, the
    author credit, and clickable GitHub / support links."""
    dialog = ttk.Toplevel(parent)
    dialog.title(t("about.title"))
    dialog.resizable(False, False)
    dialog.transient(parent)

    container = ttk.Frame(dialog, padding=20)
    container.pack(fill="both", expand=True)

    # App logo (best effort — never block the dialog if the asset is missing).
    try:
        logo = Utils.load_and_resize_image("images/jenkinsd-transformed.webp", (64, 64))
        logo_label = ttk.Label(container, image=logo)
        logo_label.image = logo  # keep a reference so it isn't garbage-collected
        logo_label.pack(anchor="w", pady=(0, 10))
    except Exception:
        pass

    ttk.Label(container, text="Credentials Jenkins Decryptor").pack(anchor="w")
    ttk.Label(container, text=t("about.version", version=Utils.APP_VERSION),
              bootstyle="secondary").pack(anchor="w", pady=(0, 12))

    ttk.Label(container, text=t("about.description"),
              justify="left", wraplength=320).pack(anchor="w", pady=(0, 12))

    ttk.Label(container, text=Utils.COPYRIGHT_TEXT).pack(anchor="w", pady=(0, 12))

    def _link(text, url):
        link = ttk.Label(container, text=text, bootstyle="info", cursor="hand2")
        link.pack(anchor="w", pady=2)
        link.bind("<Button-1>", lambda event: webbrowser.open_new(url))

    _link(t("about.github"), GITHUB_URL)
    _link(t("about.support"), DONATE_URL)

    ok_btn = ttk.Button(container, text=t("common.ok"), bootstyle="secondary", width=10,
                        command=dialog.destroy)
    ok_btn.pack(pady=(16, 0))

    dialog.bind("<Escape>", lambda event: dialog.destroy())
    dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)

    # Center over the parent window (multi-monitor safe).
    dialog.update_idletasks()
    w = dialog.winfo_reqwidth()
    h = dialog.winfo_reqheight()
    x = parent.winfo_rootx() + (parent.winfo_width() - w) // 2
    y = parent.winfo_rooty() + (parent.winfo_height() - h) // 2
    dialog.geometry(f"+{x}+{y}")

    # grab_set() routes events to the dialog but does not move the window/keyboard
    # focus to it, so it looks unfocused. Raise it and give it focus explicitly.
    dialog.lift()
    ok_btn.focus_set()
    dialog.grab_set()
