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


def _create_dir_if_not_exist(path: Path) -> None:
    if not path.exists():
        # Create app directory
        path.mkdir()


def setup_app() -> None:
    """Create app folder with all subfolder and files."""
    _create_dir_if_not_exist(MAIN_DIR_PATH)
    _create_dir_if_not_exist(THEMES_PATH)
    _create_dir_if_not_exist(QUEUES_PATH)
    _create_dir_if_not_exist(SOUNDS_PATH)
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

    if not DB_FILE_PATH.exists():
        # Create SQLite database file
        Path(DB_FILE_PATH).touch()
        # This is the only place where
        # this methods should be used
        db.db_setup()

    if not CONFIG_FILE_PATH.exists():
        # Create config.yaml file
        Path(CONFIG_FILE_PATH).touch()
        with Path(CONFIG_FILE_PATH).open("w") as file:
            yaml.dump(default_config, file, sort_keys=False)
