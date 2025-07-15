import json
from dataclasses import dataclass, asdict, field, fields
from typing import Any, Callable, List
import logging

logger = logging.getLogger(__name__)

class SingletonMeta(type):
    """Metaclass that ensures only one instance per class."""
    _instances: dict[type, object] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            # first time: actually create the object
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

@dataclass
class Config(metaclass=SingletonMeta):
    GAME_EXE_NAME: str
    HOTKEY_SC: int
    DEACTIVATION_HOTKEY_SC: int
    SPACE_HOTKEY_SC: int
    Q_SCAN_CODE: int
    E_SCAN_CODE: int
    FROZEN_COORDS: tuple[int, int]
    UNFROZEN_COORDS: tuple[int, int]
    POSITION_CHECK_INTERVAL: float
    FOCUS_CHECK_INTERVAL: float

    # internal:
    _on_change: List[Callable[['Config', str, Any, Any], None]] = field(
        default_factory=list, init=False, repr=False)
    _initialized: bool = field(default=False, init=False, repr=False)

    def __post_init__(self):
        # now that real fields are in place, set up your internals
        self._on_change: List[Callable[["Config", str, Any, Any], None]] = []
        self._initialized: bool = True

    def add_callback(self, fn: Callable[['Config', str, Any, Any], None]):
        """Register fn(cfg, field_name, old, new)."""
        self._on_change.append(fn)

    def __setattr__(self, name: str, value: Any):
        # if it’s one of our dataclass fields and we’re past __post_init__,
        # compare old vs. new and fire callbacks
        if (
            getattr(self, "_initialized", False)
            and name in self.__dataclass_fields__
        ):
            old = getattr(self, name)
            super().__setattr__(name, value)
            if old != value:
                for cb in self._on_change:
                    cb(self, name, old, value)
        else:
            # during __init__ or for non‑field attrs, do normal setattr
            super().__setattr__(name, value)

config_path = "config/config.json"
    
def save_config(config, field, old, new):
    logger.info("Saving config: %s changed from %s -> %s", field, old, new)
    
    # Grab only the "public" fields (i.e. skip anything beginning with "_")
    public_data = {
        f.name: getattr(config, f.name)
        for f in fields(config)
        if not f.name.startswith("_")
    }
    try:
        with open(config_path, 'w') as f:
            json.dump(public_data, f, indent=4)
    except Exception as e:
        logger.exception(e)


def load_config() -> Config:
    try:
        logger.info("Loading config from: %s", config_path)
        with open(config_path, 'r') as f:
            cfg_raw = json.load(f)
        return Config(**cfg_raw)
    except Exception as e:
        logger.exception(e)
