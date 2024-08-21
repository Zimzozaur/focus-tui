from focuskeeper.app import FOCUS_KEEPER, FocusKeeper
from focuskeeper.screens import SettingsScreen


class Controller:
    _app_instance: FocusKeeper = FOCUS_KEEPER

    @property
    def app(self):
        return self._app_instance

    def quit_app(self):
        self.app.exit()

    def open_settings(self):
        self.app.push_screen(SettingsScreen())

    def set_app_title(self, title: str):
        self.app.title = title
