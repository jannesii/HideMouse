import threading
import time
import psutil
import win32gui
import win32process
import logging

from .config import Config

logger = logging.getLogger(__name__)


class FocusWatcher:

    _instance: "FocusWatcher | None" = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, on_gain=None, on_loss=None):
        if self._initialized:
            return
        self.config = Config()
        self.update_config()
        self.on_gain = on_gain
        self.on_loss = on_loss
        self.game_focused = False
        self._thread = threading.Thread(target=self._watch_focus, daemon=True)

        self._initialized = True

    def update_config(self):
        self.exe_name = self.config.GAME_EXE_NAME.lower()

    def start(self):
        self._thread.start()

    def _is_game_focused(self):
        try:
            hwnd = win32gui.GetForegroundWindow()
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            return psutil.Process(pid).name().lower() == self.exe_name
        except Exception:
            return False

    def _watch_focus(self):
        while True:
            focused_now = self._is_game_focused()
            if focused_now and not self.game_focused:
                self.game_focused = True
                logger.info(f"{self.exe_name} focused – hot‑key active.")
                self.on_gain()
            elif not focused_now and self.game_focused:
                self.game_focused = False
                logger.info(f"{self.exe_name} lost focus – auto‑unfreeze.")
                self.on_loss()
            time.sleep(self.config.FOCUS_CHECK_INTERVAL)
