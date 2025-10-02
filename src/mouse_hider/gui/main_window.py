from PySide6.QtCore   import QEvent
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QStackedWidget,
    QSystemTrayIcon, QMenu
)
from PySide6.QtGui    import QIcon, QAction, QCloseEvent, QGuiApplication

from .config_page import ConfigPage


class MainWindow(QMainWindow):
    def __init__(self, restart_callback=None):
        """
        :param restart_callback: callable or None.
                                 If provided, a “Restart” item is added to
                                 the tray menu that triggers this callback.
        """
        super().__init__()
        self.setWindowTitle("Mouse Hider")
        self.setMinimumSize(400, 500)

        # ------------ stacked main GUI ------------------------
        container = QWidget()
        main_layout = QVBoxLayout(container)
        container.setLayout(main_layout)

        self.stacked = QStackedWidget()
        main_layout.addWidget(self.stacked)

        self.main_page = QWidget()
        self.main_page.setLayout(self._create_main_layout())
        self.stacked.addWidget(self.main_page)

        self.setCentralWidget(container)

        # ------------ system-tray -----------------------------
        self._create_tray_icon(restart_callback)

        # start minimised to tray
        self.hide()

    # ---------- layout helpers --------------------------------
    def _create_main_layout(self):
        layout = QVBoxLayout()
        button_layout = QHBoxLayout()

        btn_config = QPushButton("Config")
        btn_config.clicked.connect(self._open_config)
        button_layout.addWidget(btn_config)

        layout.addLayout(button_layout)
        return layout

    # ---------- page navigation --------------------------------
    def _open_main(self):
        self.stacked.setCurrentWidget(self.main_page)

    def _open_config(self):
        self.config_page = ConfigPage(parent=self)
        self.config_page.back_requested.connect(self._open_main)
        self.stacked.addWidget(self.config_page)
        self.stacked.setCurrentWidget(self.config_page)

    # ---------- tray helpers -----------------------------------
    def _create_tray_icon(self, restart_callback):
        icon = QIcon.fromTheme("input-mouse")
        self.tray = QSystemTrayIcon(icon, self)
        self.tray.setToolTip("Mouse Hider")

        menu = QMenu()

        act_show = QAction("Show window", self, triggered=self._restore_from_tray)
        menu.addAction(act_show)

        # ---- NEW: restart option -----------------------------
        if callable(restart_callback):
            act_restart = QAction("Restart", self, triggered=restart_callback)
            menu.addAction(act_restart)

        menu.addSeparator()

        act_quit = QAction("Quit", self, triggered=QGuiApplication.quit)
        menu.addAction(act_quit)

        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self._on_tray_activated)
        self.tray.show()

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self._restore_from_tray()

    def _restore_from_tray(self):
        self.showNormal()
        self.raise_()
        self.activateWindow()

    # ---------- “never close – only hide” ----------------------
    def closeEvent(self, event: QCloseEvent):
        event.ignore()
        self.hide()

    def changeEvent(self, event):
        if event.type() == QEvent.WindowStateChange and self.isMinimized():
            self.hide()
        super().changeEvent(event)
