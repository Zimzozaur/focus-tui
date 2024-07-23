from textual.app import ComposeResult
from textual.widgets import Button, Footer, Static
from textual.screen import Screen
from textual.containers import Container, VerticalScroll

from focuskeeper.widgets import (
    AppHeader, SoundSettings, AboutSettings
)


class SettingsScreen(Screen):
    TITLE = 'Settings'
    DEFAULT_CSS = """
    #settings-wrapper {
        align: center top; 
    }
    
    #settings-body {
        margin: 2 0;
        width: 70;
        height: auto;
    }
    
    .settings-section {
        border: round white;
        height: auto;
        padding: 0 1;
    }
    """
    BINDINGS = [
        ('ctrl+q', 'quit_app', 'Quit App'),
        ('escape', 'close_settings', 'Close Settings'),
    ]

    def action_quit_app(self):
        self.app.exit()

    def action_close_settings(self):
        """Method has to return anything to run callback"""
        self.dismiss()

    def __init__(self):
        super().__init__()
        self.account_settings = Static(classes='settings-section')
        self.account_settings.border_title = 'Account'

        self.social_settings = Static(classes='settings-section')
        self.social_settings.border_title = 'Social'

        self.sound_settings = Static(classes='settings-section')
        self.sound_settings.border_title = 'Sound'

        self.theme_settings = Static(classes='settings-section')
        self.theme_settings.border_title = 'Theme'

        self.theme_store_settings = Static(classes='settings-section')
        self.theme_store_settings.border_title = 'Theme Store'

        self.about = Static(classes='settings-section')
        self.about.border_title = 'About'

    def compose(self) -> ComposeResult:
        self.app.title = 'Settings'
        yield AppHeader()
        with (VerticalScroll(id='settings-wrapper')):
            with Container(id='settings-body'):
                with self.account_settings:
                    yield Button('PLACEHOLDER')
                with self.social_settings:
                    yield Button('PLACEHOLDER')
                with self.sound_settings:
                    yield SoundSettings()
                with self.theme_settings:
                    yield Button('PLACEHOLDER')
                with self.theme_store_settings:
                    yield Button('PLACEHOLDER')
                with self.about:
                    yield AboutSettings()
        yield Footer()
