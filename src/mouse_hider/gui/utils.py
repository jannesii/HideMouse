import threading
import keyboard
from PySide6.QtCore import QThread, Signal

class HotkeyRecorder(QThread):
    # emit each key-name as it’s pressed
    key_pressed = Signal(str)
    # emit the full dict when recording stops
    finished    = Signal(dict)

    def __init__(self):
        super().__init__()
        # will be a dict:  { "CTRL": 29, "A": 30, ... }
        self.keys: dict[str,int] = {}
        self._stop_event = threading.Event()

    def run(self):
        # reset state
        self.keys.clear()
        self._stop_event.clear()

        # install a non‑blocking global hook
        keyboard.hook(self._on_event)

        # wait here until stop() is called
        self._stop_event.wait()

        # once stopped, unhook and emit the dict
        keyboard.unhook(self._on_event)
        self.finished.emit(self.keys)

    def _on_event(self, event):
        # only handle key‑down
        if event.event_type == keyboard.KEY_DOWN:
            name = event.name.upper()
            if name not in self.keys:
                self.keys[name] = event.scan_code
                # tell the UI which key just went in
                self.key_pressed.emit(name)

    def stop(self):
        # immediately break out of run()
        self._stop_event.set()
