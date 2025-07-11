import logging

from keyboard import on_press_key, on_release_key, unhook_all

from .config import Config
from .utils import handle_errors

logger = logging.getLogger(__name__)

class HotkeyHandler:

    def __init__(self, hotkey: str, on_press = None, on_release = None):
        self.config = Config()
        self.hotkey = hotkey
        self.update_config()
        self._held = False
        self.on_press = on_press
        self.on_release = on_release

    @handle_errors
    def update_config(self):
        unhook_all()
        if hasattr(self.config, self.hotkey):
            self.scan_code = getattr(self.config, self.hotkey)
        self.start()

    @handle_errors
    def start(self):
        logger.debug(f"Starting hotkey handler for {self.hotkey} with scan code {self.scan_code}")
        on_press_key(self.scan_code,   self._wrap_press,   suppress=False)
        on_release_key(self.scan_code, self._wrap_release, suppress=False)

    @handle_errors
    def _wrap_press(self, event):
        if not self._held:
            self._held = True
            self.on_press()

    @handle_errors
    def _wrap_release(self, event):
        self._held = False
        self.on_release()