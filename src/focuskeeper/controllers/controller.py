from focuskeeper.app import FOCUS_KEEPER, FocusKeeper
from focuskeeper.db import DatabaseManager
from focuskeeper.screens import SettingsScreen
from focuskeeper.sound_manager import SoundManager


class Controller:
    _app_instance: FocusKeeper = FOCUS_KEEPER
    _db: DatabaseManager = DatabaseManager()
    _sm: SoundManager = SoundManager()

    @property
    def app(self):
        return self._app_instance

    def quit_app(self):
        self.app.exit()

    def open_settings(self):
        self.app.push_screen(SettingsScreen())

    def set_app_title(self, title: str):
        self.app.title = title
