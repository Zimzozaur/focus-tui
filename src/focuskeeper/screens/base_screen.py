from textual.screen import Screen

from focuskeeper.config_manager import ConfigManager
from focuskeeper.db import DatabaseManager
from focuskeeper.sound_manager import SoundManager


class BaseScreen(Screen):
    _db: DatabaseManager = DatabaseManager()
    _sm: SoundManager = SoundManager()
    _cm: ConfigManager = ConfigManager()

