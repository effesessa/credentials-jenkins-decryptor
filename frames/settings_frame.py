import tkinter as tk
import ttkbootstrap as ttk
import threading
from frames import *
import os
import configparser
from core import Utils, t, i18n
from widget.confirm_dialog import ask_yes_no
from widget.toast_notification import show_success_toast, show_warning_toast


_ENTRY_HEIGHT = 40


def _section_label(parent, text):
    """Small uppercase section header."""
    lbl = tk.Label(
        parent,
        text=text.upper(),
        font=("Segoe UI", 8, "normal"),
        anchor="w",
    )
    lbl.pack(fill="x", padx=20, pady=(10, 6))
    return lbl


def _field_label(parent, text):
    """Standard bold field label."""
    lbl = tk.Label(parent, text=text, font=("Segoe UI", 9, "bold"), anchor="w")
    lbl.pack(fill="x", padx=20, pady=(0, 4))
    return lbl


def _hint_label(parent, text):
    """Small muted hint below a field."""
    lbl = tk.Label(parent, text=text, font=("Segoe UI", 8), anchor="w")
    lbl.pack(fill="x", padx=20, pady=(3, 0))
    return lbl


# ---------------------------------------------------------------------------
# Main frame
# ---------------------------------------------------------------------------

class SettingsFrame(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.config_path = Utils.get_config_path(app_name="jenkins-decryptor")

        # Widgets that need re-styling on theme change are registered here.
        # Each entry: dict(container=, icon=, sep=, entry=, sep2=, eye=)
        self._themed_fields = []
        self._muted_labels = []   # section labels + hints (muted fg)

        # Remove the dotted focus ring that ttk leaves around buttons after a
        # click. Must run now and again after every theme switch (ttkbootstrap
        # rebuilds widget layouts on ThemeChanged, which restores the ring).
        self._strip_button_focus_ring()

        outer = tk.Frame(self)
        outer.pack(expand=True, fill="both", padx=10, pady=(0, 0))
        self._outer = outer

        # ── Section: connection ──────────────────────────────────────────────
        self._muted_labels.append(_section_label(outer, t("settings.connection")))

        # Server address
        _field_label(outer, t("settings.server"))
        self.server_stringvar = tk.StringVar()
        self.server_stringvar.trace_add("write", self.on_change)
        self.server_entry = self._make_icon_entry(outer, self.server_stringvar, icon="🌐")
        self._muted_labels.append(_hint_label(outer, t("settings.server_hint")))

        tk.Frame(outer, height=12).pack()

        # Username
        _field_label(outer, t("settings.username"))
        self.username_stringvar = tk.StringVar()
        self.username_stringvar.trace_add("write", self.on_change)
        self.username_entry = self._make_icon_entry(outer, self.username_stringvar, icon="👤")

        tk.Frame(outer, height=12).pack()

        # API token (with show/hide eye)
        _field_label(outer, t("settings.token"))
        self.token_stringvar = tk.StringVar()
        self.token_stringvar.trace_add("write", self.on_change)
        self._token_visible = False
        self.token_entry = self._make_icon_entry(
            outer, self.token_stringvar, icon="🔑", show="*", with_eye=True
        )

        tk.Frame(outer, height=14).pack()

        # Test button + spinner
        test_row = tk.Frame(outer)
        test_row.pack(fill="x", padx=20)
        self.test_button = ttk.Button(
            test_row, text=t("settings.test_button"), width=16,
            bootstyle="secondary-outline", command=self.test,
        )
        self.test_button.pack(side="left")
        self.test_spinner = ttk.Progressbar(
            test_row, mode="indeterminate", bootstyle="primary", length=80
        )

        # ── Divider ──────────────────────────────────────────────────────────
        ttk.Separator(outer, orient="horizontal").pack(fill="x", padx=20, pady=(18, 0))

        # ── Section: appearance ───────────────────────────────────────────────
        self._muted_labels.append(_section_label(outer, t("settings.appearance")))

        theme_row = tk.Frame(outer)
        theme_row.pack(fill="x", padx=20, pady=(0, 10))
        tk.Label(theme_row, text=t("settings.theme"), font=("Segoe UI", 9, "bold")).pack(side="left")
        self._light_lbl = tk.Label(theme_row, text=t("settings.light"), font=("Segoe UI", 9))
        self._light_lbl.pack(side="left", padx=(16, 6))
        self.theme_checkbutton = ttk.Checkbutton(
            theme_row, bootstyle="round-toggle", command=self.change_theme,
            cursor="hand2",
        )
        self.theme_checkbutton.pack(side="left")
        self._dark_lbl = tk.Label(theme_row, text=t("settings.dark"), font=("Segoe UI", 9))
        self._dark_lbl.pack(side="left", padx=(6, 0))

        # Language selector (radios, not a combobox, to avoid ttkbootstrap's
        # Publisher leak). Changing it switches language live via the App.
        lang_row = tk.Frame(outer)
        lang_row.pack(fill="x", padx=20, pady=(0, 10))
        tk.Label(lang_row, text=t("settings.language"), font=("Segoe UI", 9, "bold")).pack(side="left")
        self._lang_var = tk.StringVar(value=i18n.get_language())
        for name, code in i18n.LANGUAGES.items():
            ttk.Radiobutton(
                lang_row, text=name, value=code, variable=self._lang_var,
                command=self._on_language_change,
            ).pack(side="left", padx=(16, 0))

        # ── Footer bar ────────────────────────────────────────────────────────
        footer = tk.Frame(self)
        footer.pack(side=tk.BOTTOM, fill="x")
        ttk.Separator(footer, orient="horizontal").pack(fill="x")
        btn_row = tk.Frame(footer)
        btn_row.pack(fill="x", padx=14, pady=10)
        self.back_button = ttk.Button(
            btn_row, text=t("common.back"), width=10,
            bootstyle="secondary-outline", command=self.back,
        )
        self.back_button.pack(side=tk.LEFT)
        self.save_button = ttk.Button(
            btn_row, text=t("common.save"), width=10, bootstyle="primary", command=self.save
        )
        self.save_button.pack(side=tk.RIGHT)

        self.load()
        self.tested = True
        # Apply theme-derived colors to all custom tk widgets.
        self._apply_field_styles()

    # ── Custom entry factory ────────────────────────────────────────────────

    def _make_icon_entry(self, parent, textvariable, show="", icon="⬤", with_eye=False):
        """
        Bordered row with a leading icon + borderless tk.Entry. Fixed height so
        pack() auto-centers children vertically. Registers all sub-widgets for
        theme re-styling. Returns the tk.Entry.
        """
        container = tk.Frame(parent, height=_ENTRY_HEIGHT, bd=0, highlightthickness=1)
        container.pack(fill="x", padx=20)
        container.pack_propagate(False)

        icon_lbl = tk.Label(container, text=icon, font=("Segoe UI Emoji", 11))
        icon_lbl.pack(side="left", padx=(11, 0))

        sep = tk.Frame(container, width=1)
        sep.pack(side="left", fill="y", pady=8, padx=(11, 0))

        eye = None
        if with_eye:
            # packed before the entry so side="right" reserves its space
            eye = tk.Label(container, text="👁", font=("Segoe UI Emoji", 11),
                           cursor="hand2", padx=10)
            eye.pack(side="right", fill="y")
            eye.bind("<Button-1>", lambda _: self._toggle_token())

        entry = tk.Entry(container, textvariable=textvariable, show=show,
                         font=("Segoe UI", 10), bd=0, highlightthickness=0)
        entry.configure(highlightthickness=0, bd=0, relief="flat")
        entry.pack(side="left", fill="x", expand=True, padx=(10, 10 if not with_eye else 0))

        field = dict(container=container, icon=icon_lbl, sep=sep, entry=entry, eye=eye)
        self._themed_fields.append(field)

        # Focus highlight (colors filled in by _apply_field_styles)
        entry.bind("<FocusIn>", lambda _e, f=field: self._field_focus(f, True))
        entry.bind("<FocusOut>", lambda _e, f=field: self._field_focus(f, False))
        if eye is not None:
            eye.bind("<Enter>", lambda _e, f=field: f["eye"].config(foreground=self._c["accent"]))
            eye.bind("<Leave>", lambda _e, f=field: f["eye"].config(foreground=self._c["icon"]))

        return entry

    # ── Theme styling ─────────────────────────────────────────────────────────

    def _strip_button_focus_ring(self):
        """Rebuild the TButton layout without the Button.focus element, so no
        dotted outline persists after a click. ttkbootstrap's colored button
        styles (primary.TButton, etc.) inherit this base layout, so one edit
        covers them all. Editing the *layout* (not configure) keeps colors."""
        try:
            self.parent.style.layout(
                "TButton",
                [("Button.border", {"sticky": "nswe", "border": "1", "children": [
                    ("Button.padding", {"sticky": "nswe", "children": [
                        ("Button.label", {"sticky": "nswe"})]})]})],
            )
        except tk.TclError:
            pass

    def _is_dark(self):
        """True if the active theme has a dark background (by luminance)."""
        bg = self.parent.style.colors.bg.lstrip("#")
        r, g, b = int(bg[0:2], 16), int(bg[2:4], 16), int(bg[4:6], 16)
        return (0.299 * r + 0.587 * g + 0.114 * b) < 128

    def _resolve_colors(self):
        """Derive the palette for custom widgets from the active ttk theme.
        Muted text / icons / separators must flip with the background: a grey
        that reads on white (#444) is invisible on near-black, so pick by
        luminance rather than reusing the theme's `secondary`."""
        c = self.parent.style.colors
        dark = self._is_dark()
        return {
            "field_bg": c.inputbg,
            "field_fg": c.inputfg,
            "border": "#3d3d3d" if dark else c.border,
            "accent": c.primary,
            "icon": "#9aa0a6" if dark else "#888888",
            "sep": "#3d3d3d" if dark else "#e0e0e0",
            "muted": "#9aa0a6" if dark else "#6c757d",
            "panel_bg": c.bg,
        }

    def _apply_field_styles(self):
        """(Re)apply theme colors to every custom tk widget. Safe to call after
        a theme switch, which re-injects option-DB defaults we must override."""
        self._c = self._resolve_colors()
        c = self._c

        # Outer panels / frame backgrounds follow the theme bg
        self.configure(background=c["panel_bg"])
        self._outer.configure(background=c["panel_bg"])

        for lbl in self._muted_labels:
            lbl.configure(background=c["panel_bg"], foreground=c["muted"])
        for lbl in (self._light_lbl, self._dark_lbl):
            lbl.configure(background=c["panel_bg"], foreground=c["muted"])

        for f in self._themed_fields:
            f["container"].configure(
                background=c["field_bg"],
                highlightthickness=1,
                highlightbackground=c["border"],
                highlightcolor=c["border"],
            )
            f["icon"].configure(background=c["field_bg"], foreground=c["icon"])
            f["sep"].configure(background=c["sep"])
            # Re-assert borderless: theme switch re-injects highlightThickness=1
            f["entry"].configure(
                background=c["field_bg"], foreground=c["field_fg"],
                insertbackground=c["field_fg"],
                highlightthickness=0, bd=0, relief="flat",
            )
            if f["eye"] is not None:
                f["eye"].configure(background=c["field_bg"], foreground=c["icon"])

    def _field_focus(self, field, focused):
        c = self._c
        col = c["accent"] if focused else c["border"]
        field["container"].configure(highlightbackground=col, highlightcolor=col)
        field["icon"].configure(foreground=c["accent"] if focused else c["icon"])
        field["sep"].configure(background=c["accent"] if focused else c["sep"])

    # ── Helpers ─────────────────────────────────────────────────────────────

    def _toggle_token(self):
        self._token_visible = not self._token_visible
        self.token_entry.configure(show="" if self._token_visible else "*")

    def change_theme(self):
        # Toggle layout is "Light [toggle] Dark": selected = knob on the right =
        # Dark. Keep the mapping aligned with the labels (see load()).
        theme = "darkly" if self.theme_checkbutton.instate(["selected"]) else "cosmo"
        self.parent.style.theme_use(theme)
        self.parent.after(0, self.parent.menubar.apply_colors)
        self.parent.after(150, self.parent.menubar.apply_colors)
        # Re-apply our custom widget colors AFTER the theme has been swapped
        # (theme_use re-injects option-DB defaults and recolors tk widgets).
        self.parent.after(0, self._apply_field_styles)
        self.parent.after(160, self._apply_field_styles)
        # theme_use rebuilds button layouts, restoring the focus ring; strip it.
        self.parent.after(0, self._strip_button_focus_ring)
        self.parent.after(160, self._strip_button_focus_ring)

    def on_change(self, var_name, index, mode):
        self.tested = False
        self.test_button.configure(bootstyle="secondary-outline")

    def back(self):
        self.parent.show_frame(SearchFrame)

    # ── Language ────────────────────────────────────────────────────────────

    def _on_language_change(self):
        # Defer: apply_language rebuilds the UI (destroying this frame), so let
        # the current event handler finish first.
        lang = self._lang_var.get()
        self.parent.after(0, lambda: self.parent.apply_language(lang))

    def get_form_state(self):
        """Snapshot the in-progress form so a live language switch (which rebuilds
        this frame) doesn't discard unsaved edits."""
        return {
            "server": self.server_stringvar.get(),
            "username": self.username_stringvar.get(),
            "token": self.token_stringvar.get(),
            "dark": bool(self.theme_checkbutton.instate(["selected"])),
        }

    def restore_form_state(self, state):
        self.server_stringvar.set(state["server"])
        self.username_stringvar.set(state["username"])
        self.token_stringvar.set(state["token"])
        self.theme_checkbutton.state(["selected"] if state["dark"] else ["!selected"])

    # ── Test connection ───────────────────────────────────────────────────────

    def test(self):
        self.test_button.configure(state="disabled")
        self.test_spinner.pack(side="left", padx=(10, 0))
        self.test_spinner.start(10)
        threading.Thread(target=self._do_test, daemon=True).start()

    def _do_test(self):
        result = self.parent.jenkins_requestor.test(
            self.server_entry.get(), self.username_entry.get(), self.token_entry.get()
        )
        self.after(0, lambda: self._test_done(result))

    def _test_done(self, success):
        self.test_spinner.stop()
        self.test_spinner.pack_forget()
        self.test_button.configure(state="normal")
        if success:
            self.tested = True
            self.test_button.configure(bootstyle=ttk.SUCCESS)
            show_success_toast(self.parent, t("settings.test_ok"), t("toast.test"))
        else:
            self.tested = False
            self.test_button.configure(bootstyle=ttk.WARNING)
            show_warning_toast(self.parent, t("settings.test_fail"), t("toast.test"))

    # ── Save ──────────────────────────────────────────────────────────────────

    def save(self):
        if not self.tested:
            answer = ask_yes_no(
                self.parent, t("common.save"),
                t("settings.save_untested"),
            )
            if not answer:
                return
        config = configparser.ConfigParser()
        # Toggle layout is "Light [toggle] Dark": selected = knob on the right =
        # Dark. Keep the mapping aligned with the labels (see load()).
        theme = "darkly" if self.theme_checkbutton.instate(["selected"]) else "cosmo"
        if "settings" not in config:
            config["settings"] = {}
        config["settings"]["theme"] = theme
        # Preserve the active language: save() rebuilds the config from scratch,
        # so without this the language preference (written by apply_language)
        # would be wiped on the next save and revert to English on restart.
        config["settings"]["language"] = i18n.get_language()
        server = self.server_entry.get().strip()
        username = self.username_entry.get().strip()
        token = self.token_entry.get().strip()
        if server:
            config["settings"]["server_url"] = server
        if username:
            config["settings"]["username"] = username
        token_in_keyring = Utils.set_token(username, token) if token else False
        if token and not token_in_keyring:
            config["settings"]["token"] = token
        elif not token:
            Utils.delete_token(username)
        with open(self.config_path, "w") as configfile:
            config.write(configfile)
        if token and not token_in_keyring:
            show_warning_toast(
                self.parent, t("settings.keyring_unavailable"), t("toast.settings")
            )
        show_success_toast(self.parent, t("settings.saved"), t("toast.saved"))
        self.back()

    # ── Load ──────────────────────────────────────────────────────────────────

    def load(self):
        if os.path.exists(self.config_path) and self.parent.config.has_section("settings"):
            username = self.parent.config["settings"].get("username", "")
            self.server_stringvar.set(self.parent.config["settings"].get("server_url", ""))
            self.username_stringvar.set(username)
            self.token_stringvar.set(Utils.get_token(username, self.parent.config))

        theme = Utils.get_theme(self.parent.config)
        self.theme_checkbutton.state(["selected"] if theme == "darkly" else ["!selected"])

#import tkinter as tk
#import ttkbootstrap as ttk
#import threading
#from frames import *
#import os
#import configparser
#from core import Utils
#from widget.confirm_dialog import ask_yes_no
#from widget.toast_notification import show_success_toast, show_warning_toast
#
#class SettingsFrame(tk.Frame):
#
#    def __init__(self, parent):
#        super().__init__(parent)
#        self.parent = parent
#        self.config_path = Utils.get_config_path(app_name="jenkins-decryptor")
#        self.label_frame = tk.LabelFrame(self, text="Settings")
#        self.label_frame.pack(expand=True, fill="both", padx=10, pady=(0, 10))
#
#        # Server Address
#        tk.Label(self.label_frame, text="Server Address").pack(padx=15, pady=(20, 0), anchor="w")
#        self.server_stringvar = tk.StringVar()
#        self.server_stringvar.trace_add("write", self.on_change)
#        self.server_entry = ttk.Entry(self.label_frame, width=40, font=("Segoe UI", 10), textvariable=self.server_stringvar)
#        self.server_entry.pack(padx=15, pady=(5, 0), anchor="w")
#        tk.Label(self.label_frame, text="e.g. https://jenkins.company.com", font=("Segoe UI", 8), foreground="grey").pack(padx=15, pady=(2, 10), anchor="w")
#
#        # Username
#        tk.Label(self.label_frame, text="Username").pack(padx=15, anchor="w")
#        self.username_stringvar = tk.StringVar()
#        self.username_stringvar.trace_add("write", self.on_change)
#        self.username_entry = ttk.Entry(self.label_frame, width=40, font=("Segoe UI", 10), textvariable=self.username_stringvar)
#        self.username_entry.pack(padx=15, pady=10, anchor="w")
#
#        # Token with show/hide toggle
#        tk.Label(self.label_frame, text="Token").pack(padx=15, anchor="w")
#        self.token_stringvar = tk.StringVar()
#        self.token_stringvar.trace_add("write", self.on_change)
#        token_row = tk.Frame(self.label_frame)
#        token_row.pack(padx=15, pady=10, anchor="w")
#        self.token_entry = ttk.Entry(token_row, width=37, font=("Segoe UI", 10), textvariable=self.token_stringvar, show="*")
#        self.token_entry.pack(side="left")
#        self._token_visible = False
#        self.toggle_token_btn = ttk.Button(token_row, text="👁", width=3, command=self._toggle_token)
#        self.toggle_token_btn.pack(side="left", padx=(5, 0))
#
#        # Test button + spinner (spinner inserted here when testing)
#        self.test_button = ttk.Button(self.label_frame, text="Test", width=10, command=self.test)
#        self.test_button.pack(padx=15, pady=(0, 10), anchor="w")
#        self.test_spinner = ttk.Progressbar(self.label_frame, mode="indeterminate", bootstyle="primary", length=100)
#
#        ttk.Separator(self.label_frame, orient="horizontal", style="default").pack(fill="x", padx=15, pady=15)
#
#        # Theme toggle
#        tk.Label(self.label_frame, text="Theme").pack(padx=15, anchor="w")
#        self.theme_checkbutton = ttk.Checkbutton(self.label_frame, bootstyle="round-toggle", text="light", command=self.change_theme)
#        self.theme_checkbutton.pack(padx=15, anchor="w", pady=10)
#
#        # Bottom bar
#        self.bottom_frame = tk.Frame(self.label_frame)
#        self.bottom_frame.pack(side=tk.BOTTOM, fill="x", pady=10)
#        self.save_button = ttk.Button(self.bottom_frame, text="Save", width=10, command=self.save)
#        self.save_button.pack(side=tk.RIGHT, padx=10)
#        self.back_button = ttk.Button(self.bottom_frame, text="Back", width=10, command=self.back)
#        self.back_button.pack(side=tk.LEFT, padx=10)
#
#        self.load()
#        self.tested = True
#
#    def _toggle_token(self):
#        self._token_visible = not self._token_visible
#        self.token_entry.configure(show="" if self._token_visible else "*")
#
#    def change_theme(self):
#        theme = "cosmo" if self.theme_checkbutton.instate(['selected']) else "darkly"
#        self.parent.style.theme_use(theme)
#        # ttkbootstrap re-applies default colors to the classic tk Menubuttons on
#        # theme change, sometimes asynchronously. Re-apply ours both immediately
#        # and after a short delay so we win the race regardless of ordering —
#        # otherwise, if our after(0) runs first, the wrong colors stick for the
#        # rest of the session (there's nothing to re-apply them later).
#        self.parent.after(0, self.parent.menubar.apply_colors)
#        self.parent.after(150, self.parent.menubar.apply_colors)
#
#    def on_change(self, var_name, index, mode):
#        self.tested = False
#        self.test_button.configure(bootstyle="default")
#
#    def back(self):
#        self.parent.show_frame(SearchFrame)
#
#    def test(self):
#        self.test_button.configure(state="disabled")
#        self.test_spinner.pack(padx=15, pady=(0, 10), anchor="w")
#        self.test_spinner.start(10)
#        threading.Thread(target=self._do_test, daemon=True).start()
#
#    def _do_test(self):
#        result = self.parent.jenkins_requestor.test(
#            self.server_entry.get(), self.username_entry.get(), self.token_entry.get()
#        )
#        self.after(0, lambda: self._test_done(result))
#
#    def _test_done(self, success):
#        self.test_spinner.stop()
#        self.test_spinner.pack_forget()
#        self.test_button.configure(state="normal")
#        if success:
#            self.tested = True
#            self.test_button.configure(bootstyle=ttk.SUCCESS)
#            show_success_toast(self.parent, "Connection successful", "Test")
#        else:
#            self.tested = False
#            self.test_button.configure(bootstyle=ttk.WARNING)
#            show_warning_toast(self.parent, "Could not connect to Jenkins", "Test")
#
#    def save(self):
#        if not self.tested:
#            answer = ask_yes_no(
#                self.parent,
#                "Save",
#                "You have not tested the connection to the server.\nDo you want to continue?",
#            )
#            if not answer:
#                return
#        config = configparser.ConfigParser()
#        theme = "cosmo" if self.theme_checkbutton.instate(['selected']) else "darkly"
#        if 'settings' not in config:
#            config['settings'] = {}
#        config['settings']['theme'] = theme
#        server = self.server_entry.get().strip()
#        username = self.username_entry.get().strip()
#        token = self.token_entry.get().strip()
#        if server:
#            config['settings']['server_url'] = server
#        if username:
#            config['settings']['username'] = username
#        # Token goes into the OS keyring; only fall back to plaintext config if
#        # no keyring backend is available. Rewriting the file fresh also drops
#        # any legacy plaintext token from earlier versions.
#        token_in_keyring = Utils.set_token(username, token) if token else False
#        if token and not token_in_keyring:
#            config['settings']['token'] = token
#        elif not token:
#            Utils.delete_token(username)
#        with open(self.config_path, 'w') as configfile:
#            config.write(configfile)
#        if token and not token_in_keyring:
#            show_warning_toast(self.parent, "OS keyring unavailable: token stored in config file", "Settings")
#        show_success_toast(self.parent, "Settings saved", "Saved")
#        self.back()
#
#    def load(self):
#        if os.path.exists(self.config_path) and self.parent.config.has_section('settings'):
#            username = self.parent.config['settings'].get('username', '')
#            self.server_stringvar.set(self.parent.config['settings'].get('server_url', ''))
#            self.username_stringvar.set(username)
#            self.token_stringvar.set(Utils.get_token(username, self.parent.config))
#            theme = Utils.get_theme(self.parent.config)
#            if theme == "cosmo":
#                self.theme_checkbutton.state(["selected"])
#