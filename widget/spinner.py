from ttkbootstrap.widgets import Meter
from PIL import Image

# Pillow 10+ removed the Image.CUBIC alias that ttkbootstrap's Meter still uses.
if not hasattr(Image, "CUBIC"):
    Image.CUBIC = Image.BICUBIC


class Spinner(Meter):
    """Small indeterminate ring spinner: a Meter with a wedge that rotates.

    No percentage is shown — it just signals "working" for operations of
    unknown duration. Use start()/stop() like a Progressbar.
    """

    def __init__(self, master=None, size=32, **kwargs):
        super().__init__(
            master,
            metersize=size,
            amounttotal=100,
            amountused=0,
            wedgesize=15,
            meterthickness=3,
            showtext=False,
            bootstyle="primary",
            **kwargs,
        )
        self._spin = 0
        self._after_id = None

    def start(self):
        if self._after_id is None:
            self._tick()

    def _tick(self):
        self._spin = (self._spin + 4) % 100
        self.configure(amountused=self._spin)
        self._after_id = self.after(30, self._tick)

    def stop(self):
        if self._after_id is not None:
            self.after_cancel(self._after_id)
            self._after_id = None
