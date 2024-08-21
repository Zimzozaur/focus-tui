from focuskeeper.app import FOCUS_KEEPER, FocusKeeper


class Controller:
    _app_instance: FocusKeeper = FOCUS_KEEPER

    @property
    def app(self):
        return self._app_instance

    def quit_app(self):
        self.app.exit()
