#!/usr/bin/env python3
"""
Mouse-Hider launcher with self-re-exec support.

Adds a “Restart” tray-menu item that relaunches the program and exits cleanly.
"""
import os
import sys
import subprocess
import logging
from threading import Thread, Event

from PySide6.QtCore    import QTimer
from PySide6.QtWidgets import QApplication

from src.mouse_hider.config import Config, load_config, save_config
from src.mouse_hider.gui.main_window import MainWindow
from src.mouse_hider       import main as background_main


# ───────── logging ─────────
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    datefmt="%H:%M:%S",
    #filename="run.log",
    #filemode="a",
)

def restart_scheduled_task(task_path: str) -> None:
    """
    Stops the named Scheduled Task if it’s running, then starts it.
    `task_path` should be like r"\MyTasks\Hide Mouse".
    """
    # 1. Try to end it (will fail harmlessly if it's not running)
    subprocess.run(
        ["schtasks", "/End", "/TN", task_path],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # 2. Now start it
    result = subprocess.run(
        ["schtasks", "/Run", "/TN", task_path],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    print(f"Task {task_path!r} restarted. schtasks output:\n{result.stdout.strip()}")

# ───────── helper: spawn new instance & exit this one ─────────
def _restart_self(app: QApplication, stop_event: Event) -> None:
    """Launch a new copy of this program, then shut down gracefully."""
    logging.info("Restart requested – spawning replacement instance …")
    restart_scheduled_task(r"\MyTasks\Hide Mouse")
    """ python = sys.executable
    script = os.path.abspath(sys.argv[0])
    args   = sys.argv[1:]

    flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    subprocess.Popen(
        [python, script, *args],
        cwd=os.getcwd(),
        close_fds=True,
        creationflags=flags,
    ) """

    # Tell the worker thread to finish and close the GUI after the event loop ticks
    stop_event.set()
    QTimer.singleShot(0, app.quit)   # quit as soon as control returns


# ───────── main block ─────────
if __name__ == "__main__":
    # --- load & watch config ----------------------------------
    config: Config = load_config()
    config.add_callback(save_config)

    # --- background worker thread -----------------------------
    stop_event = Event()
    worker = Thread(
        target=background_main,      # long-running function
        args=(stop_event,),
        daemon=True
    )
    worker.start()

    # --- Qt application ---------------------------------------
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.aboutToQuit.connect(stop_event.set)   # ensure worker stops on exit

    # Pass restart callback to the window/tray
    window = MainWindow(restart_callback=lambda: _restart_self(app, stop_event))
    window.show()

    sys.exit(app.exec())
