import shutil
from pathlib import Path

import yaml

from focuskeeper.constants import (
    CONFIG_FILE_PATH,
    DB_FILE_PATH,
    DEFAULT_ALARM_NAME,
    DEFAULT_AMBIENT_NAME,
    DEFAULT_SIGNAL_NAME,
    LONGS_PATH,
    MAIN_DIR_PATH,
    QUEUES_PATH,
    SHORT_PATH,
    SOUNDS_PATH,
    THEMES_PATH,
)
from focuskeeper.db import DatabaseManager
from focuskeeper.fake_api_client import FakeAPIClient

fake_api = FakeAPIClient()
db = DatabaseManager()

default_config = {
    "used_sounds": {
        "alarm": {
            "name": DEFAULT_ALARM_NAME,
        },
        "signal": {
            "name": DEFAULT_SIGNAL_NAME,
        },
        "ambient": {
            "name": DEFAULT_AMBIENT_NAME,
        },
    },
}


def setup_app() -> None:
    """Create app folder with all subfolder and files."""
    if not MAIN_DIR_PATH.exists():
        # Create app directory
        MAIN_DIR_PATH.mkdir()

    if not SOUNDS_PATH.exists():
        # Create app directory
        SOUNDS_PATH.mkdir()

    if not SHORT_PATH.exists():
        # Create shorts folder
        SHORT_PATH.mkdir()
        for sound in fake_api.get_shorts():
            shutil.copy(sound, SHORT_PATH)

    if not LONGS_PATH.exists():
        # Create longs folder
        LONGS_PATH.mkdir()
        for sound in fake_api.get_longs():
            shutil.copy(sound, LONGS_PATH)

    if not THEMES_PATH.exists():
        # Create themes folder
        THEMES_PATH.mkdir()

    if not QUEUES_PATH.exists():
        # Create queues folder
        QUEUES_PATH.mkdir()

    if not DB_FILE_PATH.exists():
        # Create SQLite database file
        Path(DB_FILE_PATH).touch()
        with open(DB_FILE_PATH, "w"):
            # This is the only place where
            # this methods should be used
            db.db_setup()

    if not CONFIG_FILE_PATH.exists():
        # Create config.yaml file
        Path(CONFIG_FILE_PATH).touch()
        with open(CONFIG_FILE_PATH, "w") as file:
            yaml.dump(default_config, file, sort_keys=False)
