from focuskeeper.app import FOCUS_KEEPER, FocusKeeper
from focuskeeper.db import DatabaseManager
from focuskeeper.screens import SettingsScreen
from focuskeeper.sound_manager import SoundManager


class Controller:
    _app_instance: FocusKeeper = FOCUS_KEEPER
    _db: DatabaseManager = DatabaseManager()
    _sm: SoundManager = SoundManager()
    _ambient_silent: bool = True

    @property
    def _app(self) -> FocusKeeper:
        return self._app_instance

    def quit_app(self) -> None:
        self._app.exit()

    def open_settings(self) -> None:
        self._app.push_screen(SettingsScreen())

    def set_app_title(self, title: str) -> None:
        self._app.title = title

    def start_ambient(self) -> None:
        self._sm.play_ambient_in_background()

    def stop_ambient(self) -> None:
        self._sm.stop_ambient_in_background()

    def toggle_ambient(self) -> None:
        self._ambient_silent = not self._ambient_silent
        self._sm.toggle_ambient(self._ambient_silent)

    def play_alarm(self):
        self._sm.play_alarm()
