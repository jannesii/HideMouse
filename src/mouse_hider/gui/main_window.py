from PySide6.QtCore  import QEvent
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QStackedWidget,
    QSystemTrayIcon, QMenu
)
from PySide6.QtGui   import QIcon, QAction, QCloseEvent, QGuiApplication

from .config_page import ConfigPage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mouse Hider")
        self.setMinimumSize(400, 400)

        # 1) Make a container widget…
        container = QWidget()
        # 2) Give it your layout
        main_layout = QVBoxLayout(container)
        container.setLayout(main_layout)

        # 3) Build your stacked widget
        self.stacked = QStackedWidget()
        main_layout.addWidget(self.stacked)

        # 4) Create the “main page” and add it
        self.main_page = QWidget()
        self.main_page.setLayout(self._create_main_layout())
        self.stacked.addWidget(self.main_page)

        # 5) Tell QMainWindow to show that container
        self.setCentralWidget(container)

        #self._open_main()
        
        # ----- system‑tray -------------------------------------------------
        self._create_tray_icon()

        # start minimised to tray
        self.hide()
        
    def _create_main_layout(self):
        layout = QVBoxLayout()
        button_layout = QHBoxLayout()

        btn_config = QPushButton("Config")
        btn_config.clicked.connect(self._open_config)
        button_layout.addWidget(btn_config)

        layout.addLayout(button_layout)
        
        return layout
    
    def _open_main(self):
        self.stacked.setCurrentWidget(self.main_page)
        

    def _open_config(self):
        self.config_page = ConfigPage(parent=self)
        self.config_page.back_requested.connect(self._open_main)
        self.stacked.addWidget(self.config_page)
        self.stacked.setCurrentWidget(self.config_page)

    # ---------- tray helpers ---------------------------------------------
    def _create_tray_icon(self):
        # pick *any* icon you like; this just asks the desktop theme
        icon = QIcon.fromTheme("input-mouse")
        self.tray = QSystemTrayIcon(icon, self)
        self.tray.setToolTip("Mouse Hider")

        menu = QMenu()
        act_show  = QAction("Show window",  self, triggered=self._restore_from_tray)
        act_quit  = QAction("Quit",         self, triggered=QGuiApplication.quit)
        menu.addAction(act_show)
        menu.addSeparator()
        menu.addAction(act_quit)
        self.tray.setContextMenu(menu)

        self.tray.activated.connect(self._on_tray_activated)
        self.tray.show()

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self._restore_from_tray()

    def _restore_from_tray(self):
        self.showNormal()
        self.raise_()          # macOS / Wayland focus helpers
        self.activateWindow()
        
    # ---------- “never close – only hide” -------------------------------
    def closeEvent(self, event: QCloseEvent):
        event.ignore()           # stop Qt from closing
        self.hide()              # just send the window to tray

    # minimise‑button (“_”) does the same
    def changeEvent(self, event):
        if event.type() == QEvent.WindowStateChange and self.isMinimized():
            self.hide()
        super().changeEvent(event)