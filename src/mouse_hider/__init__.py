import logging
from time import sleep
from threading import Event

from .focus_watcher import FocusWatcher
from .mouse_freezer import MouseFreezer
from .hotkey_handler import HotkeyHandler
from .config import Config

logger = logging.getLogger(__name__)
shutdown_flag = False


def update_all_configs(config, field, old, new):
    FocusWatcher().update_config()
    MouseFreezer().update_config()
    HotkeyHandler().update_config()


def main(stop_event: Event | None = None):
    config = Config()
    freezer = MouseFreezer()
    # On focus loss, auto‑unfreeze
    focus_watcher = FocusWatcher(
        on_gain=lambda: None,
        on_loss=freezer.unfreeze
    )

    def _on_hotkey():
        if focus_watcher.game_focused:
            logger.info("test")
            freezer.toggle()
        else:
            logger.info(
                f"{config.GAME_EXE_NAME} not focused, mouse not frozen")

    def _on_deactivation_hotkey():
        if focus_watcher.game_focused:
            logger.info("Deactivating mouse hider")
            freezer.unfreeze()

    activation_handler = HotkeyHandler(
        hotkey="HOTKEY_SC",
        on_press=_on_hotkey,
        on_release=lambda: None
    )
    deactivation_handler = HotkeyHandler(
        hotkey="DEACTIVATION_HOTKEY_SC",
        on_press=_on_deactivation_hotkey,
        on_release=lambda: None
    )

    def update_all_configs(config, field, old, new):
        FocusWatcher().update_config()
        MouseFreezer().update_config()
        activation_handler.update_config()
        deactivation_handler.update_config()

    config.add_callback(update_all_configs)

    logger.info(
        f"Ready. NumPad / toggles freeze (only while {config.GAME_EXE_NAME} runs).")
    logger.info(
        f"Frozen → {config.FROZEN_COORDS} | Unfrozen → {config.UNFROZEN_COORDS}")
    logger.info("Exit with Ctrl+C.")
    freezer.start()
    focus_watcher.start()
    try:
        # run until Ctrl‑C *or* GUI tells us to stop
        while stop_event is None or not stop_event.is_set():
            sleep(1)
    finally:
        freezer.unfreeze()      # always clean up
        logger.info("Stopped.")
