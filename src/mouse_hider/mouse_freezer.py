from threading import Thread
from time import sleep
import logging
from pynput.mouse import Controller, Listener as MouseListener

from .config import Config

logger = logging.getLogger(__name__)


class MouseFreezer:
    
    _instance: "MouseFreezer | None" = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.config = Config()
        self.update_config()
        self.freeze_flag = False
        self.mouse = Controller()
        self._hook = None
        self._thread = Thread(target=self._maintain_position, daemon=True)
        
        self._initialized = True

    def update_config(self):
        self.frozen_coords = self.config.FROZEN_COORDS
        self.unfrozen_coords = self.config.UNFROZEN_COORDS

    def start(self):
        self._thread.start()

    def _maintain_position(self):
        while True:
            if self.freeze_flag:
                self.mouse.position = self.frozen_coords
            sleep(self.config.POSITION_CHECK_INTERVAL)

    def _start_hook(self):
        if not self._hook:
            self._hook = MouseListener(
                on_move=lambda *a, **k: None,
                on_click=lambda *a, **k: None,
                on_scroll=lambda *a, **k: None,
                suppress=True
            )
            self._hook.start()

    def _stop_hook(self):
        if self._hook:
            self._hook.stop()
            self._hook = None

    def freeze(self):
        if not self.freeze_flag:
            self.freeze_flag = True
            self.mouse.position = self.frozen_coords
            self._start_hook()
            logger.info(f"Mouse frozen at {self.frozen_coords}.")

    def unfreeze(self):
        if self.freeze_flag:
            self.freeze_flag = False
            self._stop_hook()
            self.mouse.position = self.unfrozen_coords
            logger.info(f"Mouse unfrozen; moved to {self.unfrozen_coords}.")

    def toggle(self):
        if self.freeze_flag:
            self.unfreeze()
        else:
            self.freeze()
