import sys
from ttkbootstrap.tooltip import ToolTip as _ToolTip


def _monitor_work_area(x, y):
    """Return (left, top, right, bottom) of the monitor containing point (x, y).

    Uses the Win32 API so it's correct with multiple monitors (including
    secondary screens at negative coordinates). Returns None when unavailable,
    so the caller can fall back to the primary screen size.
    """
    if sys.platform == "win32":
        try:
            import ctypes
            from ctypes import wintypes

            class RECT(ctypes.Structure):
                _fields_ = [("left", wintypes.LONG), ("top", wintypes.LONG),
                            ("right", wintypes.LONG), ("bottom", wintypes.LONG)]

            class MONITORINFO(ctypes.Structure):
                _fields_ = [("cbSize", wintypes.DWORD), ("rcMonitor", RECT),
                            ("rcWork", RECT), ("dwFlags", wintypes.DWORD)]

            MONITOR_DEFAULTTONEAREST = 2
            hmon = ctypes.windll.user32.MonitorFromPoint(
                wintypes.POINT(int(x), int(y)), MONITOR_DEFAULTTONEAREST
            )
            mi = MONITORINFO()
            mi.cbSize = ctypes.sizeof(MONITORINFO)
            if ctypes.windll.user32.GetMonitorInfoW(hmon, ctypes.byref(mi)):
                r = mi.rcWork  # work area = monitor minus taskbar
                return r.left, r.top, r.right, r.bottom
        except Exception:
            pass
    return None


class ToolTip(_ToolTip):
    """App-wide tooltip: neutral dark background, 400ms delay, and kept inside
    the monitor under the cursor (flips left/up near edges instead of being
    clipped or landing on another screen)."""

    def __init__(self, widget, text):
        super().__init__(widget, text=text, bootstyle="dark-inverse", delay=400)

    def _reposition(self):
        tl = self.toplevel
        if not tl:
            return
        tl.update_idletasks()
        w = tl.winfo_reqwidth()
        h = tl.winfo_reqheight()
        px = self.widget.winfo_pointerx()
        py = self.widget.winfo_pointery()

        bounds = _monitor_work_area(px, py)
        if bounds is None:
            left, top = 0, 0
            right = self.widget.winfo_screenwidth()
            bottom = self.widget.winfo_screenheight()
        else:
            left, top, right, bottom = bounds

        x = px + 25
        y = py + 10
        if x + w > right:
            x = px - w - 5          # flip to the left of the cursor
        if y + h > bottom:
            y = py - h - 5          # flip above the cursor
        x = max(left, min(x, right - w))
        y = max(top, min(y, bottom - h))
        tl.geometry(f"+{int(x)}+{int(y)}")

    def show_tip(self, *args):
        super().show_tip(*args)
        self._reposition()

    def move_tip(self, *args):
        self._reposition()
