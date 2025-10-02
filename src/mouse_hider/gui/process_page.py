import sys
import random
import logging
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QGridLayout, QApplication, QMainWindow, QWidget, \
    QVBoxLayout, QHBoxLayout, QLabel, QTabWidget, QMenu, QSystemTrayIcon, \
    QSizePolicy, QMessageBox, QLineEdit, QPushButton, QStackedWidget, QComboBox
import psutil

from ..config import Config

logger = logging.getLogger(__name__)


class ProcessPage(QWidget):
    back_requested = Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        main_layout = QVBoxLayout(self)
        self.stacked = QStackedWidget()

        self.process_page = QWidget()
        self.process_page.setLayout(self._create_process_layout())
        self.stacked.addWidget(self.process_page)

        main_layout.addWidget(self.stacked, 1)
        self.setLayout(main_layout)
        self.stacked.setCurrentWidget(self.process_page)

    def _create_process_layout(self):
        layout = QVBoxLayout()

        self.process_cb = QComboBox()
        self.process_cb.addItems(self._get_running_processes())
        layout.addWidget(self.process_cb)

        btn_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.clicked.connect(self._save_process)
        btn_layout.addWidget(save_button)

        back_button = QPushButton("Back")
        back_button.clicked.connect(self._back_to_conf)
        btn_layout.addWidget(back_button)

        layout.addLayout(btn_layout)

        return layout

    def _save_process(self):
        text = self.process_cb.currentText()
        self.back_requested.emit(text)

    def _back_to_conf(self):
        self.back_requested.emit("")

    def _get_running_processes(self):
        process_list = []
        for process in psutil.process_iter(['pid', 'name']):
            try:
                process_info = process.info
                process_list.append(
                    f"{process_info['pid']} - {process_info['name']}")
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        process_list = [line.split(' - ')[1] for line in process_list]
        process_list = list(set(process_list))
        process_list = [process for process in process_list]
        process_list.sort()
        return process_list
