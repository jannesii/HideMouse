import logging
from time import sleep
from threading import Event

from pynput.mouse import Button

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

    cam_7_mode = False            # already there
    space_translated_down = False # NEW ➊  – did we turn Space into a right-click?
    space_physically_down = False # NEW ➋  – is the key itself still down?

    def _on_space_press(event):
        nonlocal space_translated_down, space_physically_down   # ← here
        space_physically_down = True
        if focus_watcher.game_focused and cam_7_mode:
            freezer.mouse.press(Button.right)
            space_translated_down = True
            return False        # swallow Space
        return True

    def _on_space_release(event):
        nonlocal space_translated_down, space_physically_down   # ← here
        space_physically_down = False
        if space_translated_down:
            freezer.mouse.release(Button.right)
            space_translated_down = False
            return False
        return True

    def _on_hotkey(event):        # leaves cam-7 mode
        nonlocal cam_7_mode, space_translated_down              # ← here
        if focus_watcher.game_focused:
            freezer.toggle()
            cam_7_mode = False
            if space_translated_down:          # key still held → release
                freezer.mouse.release(Button.right)
                space_translated_down = False

    def _on_deactivation_hotkey(event):   # enters cam-7 mode
        nonlocal cam_7_mode                                     # ← here
        if focus_watcher.game_focused:
            freezer.unfreeze()
            cam_7_mode = True
            
    def _on_q_or_e(event):
        nonlocal cam_7_mode, space_translated_down, space_physically_down
        if focus_watcher.game_focused:
            cam_7_mode = False
            freezer.freeze()
            if space_translated_down:          # key still held → release
                freezer.mouse.release(Button.right)
                space_translated_down = False
            if space_physically_down:          # key itself still down → release
                freezer.mouse.release(Button.right)
                space_physically_down = False

    activation_handler = HotkeyHandler(
        hotkey="HOTKEY_SC",
        on_press=_on_hotkey,
        on_release=lambda _: None
    )
    deactivation_handler = HotkeyHandler(
        hotkey="DEACTIVATION_HOTKEY_SC",
        on_press=_on_deactivation_hotkey,
        on_release=lambda _: None
    )
    space_handler = HotkeyHandler(
        hotkey="SPACE_HOTKEY_SC",
        on_press=_on_space_press,
        on_release=_on_space_release
    )
    q_handler = HotkeyHandler(
        hotkey="Q_SCAN_CODE",
        on_press=_on_q_or_e,
        on_release=lambda _: None
    )
    e_handler = HotkeyHandler(
        hotkey="E_SCAN_CODE",
        on_press=_on_q_or_e,
        on_release=lambda _: None
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
