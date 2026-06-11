import tkinter as tk
import ttkbootstrap as ttk

class Toast:
    _BOOTSTYLE = {
        "success": "success",
        "error": "danger",
        "warning": "warning",
        "info": "info",
    }
    _ICONS = {
        "success": "✓",
        "error": "✕",
        "warning": "!",
        "info": "i",
    }

    def __init__(self, parent, message, title="Notifica", duration=2000, toast_type="success"):
        self.parent = parent
        self.message = message
        self.title = title
        self.duration = duration
        self.toast_type = toast_type
        self._closed = False
        self._create()

    @staticmethod
    def _shade(hex_color, amount):
        """Blend a hex color toward white (amount > 0) or black (amount < 0).
        amount is a 0..1 fraction. Used to derive a card surface / border that
        contrasts with the theme background in both light and dark themes."""
        h = hex_color.lstrip("#")
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        if amount >= 0:
            r = int(r + (255 - r) * amount)
            g = int(g + (255 - g) * amount)
            b = int(b + (255 - b) * amount)
        else:
            f = 1 + amount
            r, g, b = int(r * f), int(g * f), int(b * f)
        return f"#{r:02x}{g:02x}{b:02x}"

    def _create(self):
        colors = ttk.Style().colors
        bootstyle = self._BOOTSTYLE.get(self.toast_type, "info")
        accent = getattr(colors, bootstyle)

        # The toast body must NOT be the same color as the theme background,
        # otherwise the box blends into the window and only the text seems to
        # appear. Derive a "card" surface + a neutral border that contrast with
        # the bg: lighten on dark themes, darken on light themes.
        bg = colors.bg
        h = bg.lstrip("#")
        lum = 0.299 * int(h[0:2], 16) + 0.587 * int(h[2:4], 16) + 0.114 * int(h[4:6], 16)
        if lum < 128:  # dark theme -> lighter card, lighter border
            surface = self._shade(bg, 0.10)
            border = self._shade(bg, 0.35)
        else:          # light theme -> slightly darker card, visible grey border
            surface = self._shade(bg, -0.04)
            border = self._shade(bg, -0.22)

        self.toast = tk.Toplevel(self.parent)
        self.toast.wm_overrideredirect(True)
        self.toast.wm_attributes("-topmost", True)
        self.toast.resizable(False, False)
        # ttkbootstrap overrides colors passed to a classic tk widget's
        # CONSTRUCTOR, so every bg/fg below is applied AFTER creation with
        # .config()/.configure() (where it sticks) — same trick as the menubar.

        # 1-px neutral border all around -> the box is visible against the
        # window background (no longer blends in) without being heavy.
        wrapper = tk.Frame(self.toast, padx=1, pady=1)
        wrapper.pack(fill="both", expand=True)
        wrapper.config(bg=border)

        # Card surface (distinct from the window background)
        body = tk.Frame(wrapper)
        body.pack(fill="both", expand=True)
        body.config(bg=surface)

        # Left accent strip (carries the type color)
        strip = tk.Frame(body, width=4)
        strip.pack(side="left", fill="y")
        strip.config(bg=accent)

        # Content column
        right = tk.Frame(body)
        right.pack(side="left", fill="both", expand=True)
        right.config(bg=surface)

        pad = tk.Frame(right)
        pad.pack(fill="both", expand=True, padx=12, pady=10)
        pad.config(bg=surface)

        # Header: icon pill + title + close button
        hdr = tk.Frame(pad)
        hdr.pack(fill="x")
        hdr.config(bg=surface)

        icon = tk.Label(hdr, text=self._ICONS[self.toast_type],
                        font=("Segoe UI", 8, "bold"), padx=5, pady=1)
        icon.pack(side="left", padx=(0, 8))
        icon.config(bg=accent, fg="white")

        title = tk.Label(hdr, text=self.title, font=("Segoe UI", 10, "bold"), anchor="w")
        title.pack(side="left", fill="x", expand=True)
        title.config(bg=surface, fg=colors.fg)

        close = tk.Label(hdr, text="×", font=("Segoe UI", 14), cursor="hand2")
        close.pack(side="right")
        close.config(bg=surface, fg=colors.secondary)
        close.bind("<Button-1>", lambda e: self.close_toast())

        # Message text
        msg = tk.Label(pad, text=self.message, font=("Segoe UI", 9),
                       wraplength=270, justify="left", anchor="w")
        msg.pack(fill="x", pady=(5, 0))
        msg.config(bg=surface, fg=colors.fg)  # theme fg (white on dark) — readable on the card

        self._position()
        self._animate_in()
        self.toast.after(self.duration, self._animate_out)

    def _position(self):
        self.toast.update_idletasks()
        w = max(self.toast.winfo_reqwidth(), 280)
        h = self.toast.winfo_reqheight()

        # Anchor to the parent window — works on any monitor, any resolution.
        # No OS-level screen detection needed.
        px = self.parent.winfo_x()
        py = self.parent.winfo_y()
        pw = self.parent.winfo_width()
        ph = self.parent.winfo_height()

        self._fx = px + pw - w - 20
        self._fy = py + ph - h - 20

        # Start 20px lower and invisible for a slide-up + fade-in effect
        self.toast.attributes("-alpha", 0.0)
        self.toast.geometry(f"{w}x{h}+{self._fx}+{self._fy + 20}")

    def _animate_in(self):
        self._step_in(0.0, self._fy + 20)

    def _step_in(self, alpha, y):
        if self._closed or not self.toast.winfo_exists():
            return
        new_alpha = min(1.0, alpha + 0.12)
        new_y = max(self._fy, y - 4)
        self.toast.attributes("-alpha", new_alpha)
        self.toast.geometry(f"+{self._fx}+{new_y}")
        if new_alpha < 1.0 or new_y > self._fy:
            self.toast.after(12, lambda: self._step_in(new_alpha, new_y))

    def _animate_out(self):
        if self._closed:
            return
        self._step_out(1.0, self.toast.winfo_y())

    def _step_out(self, alpha, y):
        if self._closed or not self.toast.winfo_exists():
            return
        new_alpha = max(0.0, alpha - 0.12)
        self.toast.attributes("-alpha", new_alpha)
        self.toast.geometry(f"+{self._fx}+{y + 4}")
        if new_alpha > 0.0:
            self.toast.after(12, lambda: self._step_out(new_alpha, y + 4))
        else:
            self.close_toast()

    def close_toast(self):
        self._closed = True
        if self.toast.winfo_exists():
            self.toast.destroy()


def show_success_toast(parent, message, title="Successo"):
    Toast(parent, message, title, toast_type="success")

def show_error_toast(parent, message, title="Errore"):
    Toast(parent, message, title, toast_type="error")

def show_warning_toast(parent, message, title="Attenzione"):
    Toast(parent, message, title, toast_type="warning")

def show_info_toast(parent, message, title="Informazione"):
    Toast(parent, message, title, toast_type="info")
