import logging

from keyboard import on_press_key, on_release_key, unhook_all, unhook_key

from .config import Config
from .utils import handle_errors

logger = logging.getLogger(__name__)


class HotkeyHandler:
    _initialized = False

    def __init__(self, hotkey: str, on_press=None, on_release=None):
        self.config = Config()
        self.hotkey = hotkey
        self._held = False
        self.on_press = on_press
        self.on_release = on_release
        self._press_hook = None
        self._release_hook = None
        self.update_config()

    @handle_errors
    def update_config(self):
        # Unhook only this handler's hooks
        if self._press_hook:
            self._press_hook()
            self._press_hook = None
        # Use scan code
        if hasattr(self.config, self.hotkey):
            self.scan_code = getattr(self.config, self.hotkey)
        else:
            self.scan_code = None
        self.start()

    @handle_errors
    def start(self):
        logger.debug(
            f"Starting hotkey handler for {self.hotkey} with scan code {self.scan_code}")
        if self.scan_code is not None:
            self._press_hook = on_press_key(
                self.scan_code,   self._wrap_press,   suppress=False)
            self._release_hook = on_release_key(
                self.scan_code, self._wrap_release, suppress=False)

    @handle_errors
    def _wrap_press(self, event):
        if not self._held:
            self._held = True
            self.on_press()

    @handle_errors
    def _wrap_release(self, event):
        self._held = False
        self.on_release()
