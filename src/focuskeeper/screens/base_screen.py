from textual.screen import Screen

from focuskeeper.db import DatabaseManager
from focuskeeper.sound_manager import SoundManager
from focuskeeper.config import ConfigManager


class BaseScreen(Screen):
    _db: DatabaseManager = DatabaseManager()
    _sm: SoundManager = SoundManager()
    _cm: ConfigManager = ConfigManager()

