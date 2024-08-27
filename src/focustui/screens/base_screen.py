from textual.screen import Screen

from focustui.config_manager import ConfigManager
from focustui.db import DatabaseManager
from focustui.sound_manager import SoundManager


class BaseScreen(Screen):
    _db: DatabaseManager = DatabaseManager()
    _sm: SoundManager = SoundManager()
    _cm: ConfigManager = ConfigManager()

