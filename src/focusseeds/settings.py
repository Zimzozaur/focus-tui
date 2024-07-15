from textual.app import ComposeResult
from textual.widgets import Button, Footer
from textual.screen import Screen

from focusseeds._app import AppHeader


class SettingsScreen(Screen):
    BINDINGS = [
        ('escape', 'close_settings', 'Close Settings'),
    ]

    def action_close_settings(self):
        """Method has to return anything to run callback"""
        self.dismiss(None)

    def compose(self) -> ComposeResult:
        self.app.title = 'Settings'
        yield AppHeader()
        yield Button(variant='success')
        yield Footer()
