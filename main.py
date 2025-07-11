import sys
from threading import Thread, Event
import logging

from PySide6.QtWidgets import QApplication

from src.mouse_hider.config import Config, load_config, save_config
from src.mouse_hider.gui.main_window import MainWindow
from src.mouse_hider import main

logging.basicConfig(
    level=logging.DEBUG,      # show INFO+ from the root
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    datefmt="%H:%M:%S"
)


if __name__ == "__main__":
    config: Config = load_config()
    config.add_callback(save_config)
    
    stop_event = Event()
    worker = Thread(
        target=main,      # function imported from src/mouse_hider/__init__.py
        args=(stop_event,),      # pass the event!
        daemon=True              # die automatically if GUI exits abnormally
    )
    worker.start()


    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False) 
    app.aboutToQuit.connect(stop_event.set)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
