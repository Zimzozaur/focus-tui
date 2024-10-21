import json
import shutil
from pathlib import Path

from focustui.config_manager import ConfigModel
from focustui.constants import (
    CONFIG_FILE_PATH,
    LONGS_PATH,
    MAIN_DIR_PATH,
    QUEUES_PATH,
    SHORTS_PATH,
    SOUNDS_PATH,
    THEMES_PATH,
)
from focustui.db import DatabaseManager
from focustui.sound_file_manager import SoundFileManager

sfm = SoundFileManager()
db = DatabaseManager()


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
    if not SHORTS_PATH.exists():
        # Create shorts folder
        SHORTS_PATH.mkdir()
        for sound in sfm.get_shorts():
            shutil.copy(sound, SHORTS_PATH)

    if not LONGS_PATH.exists():
        # Create longs folder
        LONGS_PATH.mkdir()
        for sound in sfm.get_longs():
            shutil.copy(sound, LONGS_PATH)

    # if not DB_FILE_PATH.exists():
    # Create SQLite database file
    # Path(DB_FILE_PATH).touch()  # noqa: ERA001
    # This is the only place where
    # this methods should be used
    # db.db_setup()  # noqa: ERA001

    if not CONFIG_FILE_PATH.exists():
        # Create config.json file
        Path(CONFIG_FILE_PATH).touch()
        with Path(CONFIG_FILE_PATH).open("w") as file:
            json_config = json.loads(ConfigModel().model_dump_json())
            json.dump(json_config, file, sort_keys=False, indent=4)
