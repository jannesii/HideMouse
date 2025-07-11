import sys
import random
import logging
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QGridLayout, QApplication, QMainWindow, QWidget, \
    QVBoxLayout, QHBoxLayout, QLabel, QTabWidget, QMenu, QSystemTrayIcon, \
    QSizePolicy, QMessageBox, QLineEdit, QPushButton, QStackedWidget
import psutil

from ..config import Config
from .process_page import ProcessPage
from .utils import HotkeyRecorder


logger = logging.getLogger(__name__)


class ConfigPage(QWidget):
    back_requested = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.cfg = Config()

        main_layout = QVBoxLayout(self)
        self.stacked = QStackedWidget()

        self.config_page = QWidget()
        self.config_page.setLayout(self._create_config_layout())
        self.stacked.addWidget(self.config_page)

        main_layout.addWidget(self.stacked)
        self.setLayout(main_layout)
        self._open_config_page()

    def _create_config_layout(self):
        cfg = self.cfg
        layout = QVBoxLayout()

        # EXE NAME -------------------------------

        exe_layout = QHBoxLayout()
        self.exe_warning_label = QLabel()
        exe_layout.addWidget(self.exe_warning_label)

        label_exe_name = QLabel("Exe name:")
        exe_layout.addWidget(label_exe_name)

        self.input_exe_name = QLineEdit(f"{cfg.GAME_EXE_NAME}")
        exe_layout.addWidget(self.input_exe_name)

        btn_choose_exe = QPushButton("Run")
        btn_choose_exe.clicked.connect(self._open_process_page)
        exe_layout.addWidget(btn_choose_exe)

        layout.addLayout(exe_layout)

        # COORDS -------------------------------

        coord_layout = QVBoxLayout()
        self.coord_warning_label = QLabel()
        coord_layout.addWidget(self.coord_warning_label)

        f_label = QLabel("Frozen coords:")
        coord_layout.addWidget(f_label)

        frozen_coord_layout = QHBoxLayout()

        fx_label = QLabel("x:")
        frozen_coord_layout.addWidget(fx_label)

        self.fx_input = QLineEdit(str(cfg.FROZEN_COORDS[0]))
        frozen_coord_layout.addWidget(self.fx_input)

        fy_label = QLabel("y:")
        frozen_coord_layout.addWidget(fy_label)

        self.fy_input = QLineEdit(str(cfg.FROZEN_COORDS[1]))
        frozen_coord_layout.addWidget(self.fy_input)

        coord_layout.addLayout(frozen_coord_layout)

        uf_label = QLabel("Unfrozen coords:")
        coord_layout.addWidget(uf_label)

        unfrozen_coord_layout = QHBoxLayout()

        ufx_label = QLabel("x:")
        unfrozen_coord_layout.addWidget(ufx_label)

        self.ufx_input = QLineEdit(str(cfg.UNFROZEN_COORDS[0]))
        unfrozen_coord_layout.addWidget(self.ufx_input)

        ufy_label = QLabel("y:")
        unfrozen_coord_layout.addWidget(ufy_label)

        self.ufy_input = QLineEdit(str(cfg.UNFROZEN_COORDS[1]))
        unfrozen_coord_layout.addWidget(self.ufy_input)

        coord_layout.addLayout(unfrozen_coord_layout)

        layout.addLayout(coord_layout)

        # KEYBIND -------------------------------

        recorder_layout = self._create_hotkey_layout()
        layout.addLayout(recorder_layout)

        # BUTTONS -------------------------------

        layout.addStretch()
        btn_layout = QHBoxLayout()
        save_button = QPushButton("Save Config")
        save_button.clicked.connect(self._save_config)
        btn_layout.addWidget(save_button)

        back_button = QPushButton("Back")
        back_button.clicked.connect(self.back_requested)
        btn_layout.addWidget(back_button)

        layout.addLayout(btn_layout)

        return layout

    def _create_hotkey_layout(self):
        # Activation hotkey
        self.recorder = HotkeyRecorder()
        self.recorder.key_pressed.connect(self._on_key)
        self.recorder.finished.connect(self._on_finished)

        self.input = QLineEdit(self)
        self.input.setReadOnly(True)
        self.button = QPushButton("Record Activation Hotkey", self)
        self.button.clicked.connect(self._toggle_recording)

        # Deactivation hotkey
        self.deactivation_recorder = HotkeyRecorder()
        self.deactivation_recorder.key_pressed.connect(
            self._on_deactivation_key)
        self.deactivation_recorder.finished.connect(
            self._on_deactivation_finished)

        self.deactivation_input = QLineEdit(self)
        self.deactivation_input.setReadOnly(True)
        self.deactivation_button = QPushButton(
            "Record Deactivation Hotkey", self)
        self.deactivation_button.clicked.connect(
            self._toggle_deactivation_recording)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Activation Hotkey:"))
        layout.addWidget(self.input)
        layout.addWidget(self.button)
        layout.addWidget(QLabel("Deactivation Hotkey:"))
        layout.addWidget(self.deactivation_input)
        layout.addWidget(self.deactivation_button)

        self._recording = False
        self._deactivation_recording = False

        return layout

    def _save_config(self):
        exe_name = self.input_exe_name.text()

        try:
            fx = int(self.fx_input.text())
            fy = int(self.fy_input.text())
            self.cfg.FROZEN_COORDS = [fx, fy]

            ufx = int(self.ufx_input.text())
            ufy = int(self.ufy_input.text())
            self.cfg.UNFROZEN_COORDS = [ufx, ufy]
        except (ValueError, TypeError) as e:
            logger.warning("Error in _save_config: ", e)
            self.coord_warning_label.setText("INVALID COORD VALUE")

        if exe_name and exe_name.lower().endswith(".exe"):
            self.cfg.GAME_EXE_NAME = exe_name
        else:
            if not exe_name:
                self.exe_warning_label.setText("404 exe name not found")
                return
            elif not exe_name.lower().endswith(".exe"):
                self.exe_warning_label.setText("Name must end with .exe")
                return

    def _open_config_page(self, exe_name: str = None):
        if exe_name:
            self.input_exe_name.setText(exe_name)

        self.stacked.setCurrentWidget(self.config_page)

    def _open_process_page(self):
        page = ProcessPage(self)
        page.back_requested.connect(self._open_config_page)
        self.stacked.addWidget(page)
        self.stacked.setCurrentWidget(page)

    def _toggle_recording(self):
        if not self._recording:
            self.input.clear()
            self.recorder.start()
            self.button.setText("Stop Recording")
            self._recording = True
        else:
            self.recorder.stop()
            self.button.setEnabled(False)

    def _toggle_deactivation_recording(self):
        if not self._deactivation_recording:
            self.deactivation_input.clear()
            self.deactivation_recorder.start()
            self.deactivation_button.setText("Stop Recording")
            self._deactivation_recording = True
        else:
            self.deactivation_recorder.stop()
            self.deactivation_button.setEnabled(False)

    @staticmethod
    def parse_hotkeys(keys) -> tuple[list[str], list[int]]:
        s = []
        codes = []
        for k, v in keys.items():
            s.append(k)
            codes.append(v)

        return s, codes

    def _on_key(self, keys):
        # update the display on each press for activation hotkey
        keys, codes = self.parse_hotkeys(self.recorder.keys)
        combo = "+".join(keys)
        self.input.setText(combo)

    def _on_finished(self, keys: dict[str, int]):
        # re‑enable button, reset text, show final combo for activation hotkey
        keys, codes = self.parse_hotkeys(self.recorder.keys)
        combo = "+".join(keys)
        self.input.setText(combo)
        self.button.setText("Record Activation Hotkey")
        self.button.setEnabled(True)
        self._recording = False
        print("Recorded activation hotkey:", combo)
        if codes:
            self.cfg.HOTKEY_SC = codes[0]

    def _on_deactivation_key(self, keys):
        # update the display on each press for deactivation hotkey
        keys, codes = self.parse_hotkeys(self.deactivation_recorder.keys)
        combo = "+".join(keys)
        self.deactivation_input.setText(combo)

    def _on_deactivation_finished(self, keys: dict[str, int]):
        # re‑enable button, reset text, show final combo for deactivation hotkey
        keys, codes = self.parse_hotkeys(self.deactivation_recorder.keys)
        combo = "+".join(keys)
        self.deactivation_input.setText(combo)
        self.deactivation_button.setText("Record Deactivation Hotkey")
        self.deactivation_button.setEnabled(True)
        self._deactivation_recording = False
        print("Recorded deactivation hotkey:", combo)
        if codes:
            self.cfg.DEACTIVATION_HOTKEY_SC = codes[0]
