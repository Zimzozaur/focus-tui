from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Container, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Footer, Static

from focustui.composite_widgets import AboutSettings, SoundSettings

if TYPE_CHECKING:
    from focustui.config_manager import ConfigManager
    from focustui.sound_manager import SoundManager


class SettingsScreen(Screen):
    TITLE = "Settings"
    BINDINGS = [
        ("ctrl+q", "quit_app", "Quit App"),
        ("escape", "close_settings", "Close Settings"),
    ]

    def action_quit_app(self) -> None:
        self.app.exit()

    def action_close_settings(self) -> None:
        """Return anything to run callback."""
        self._sm.stop_sound()
        self.app.open_focus()

    def __init__(
        self,
        cm: "ConfigManager",
        sm: "SoundManager",
    ) -> None:
        super().__init__()
        self._cm = cm
        self._sm = sm

        self.account_settings_border = Static(classes="settings-section")
        self.account_settings_border.border_title = "Account"

        self.social_settings_border = Static(classes="settings-section")
        self.social_settings_border.border_title = "Social"

        self.sound_settings_border = Static(classes="settings-section")
        self.sound_settings_border.border_title = "Sound"

        self.theme_settings_border = Static(classes="settings-section")
        self.theme_settings_border.border_title = "Theme"

        self.theme_store_settings_border = Static(classes="settings-section")
        self.theme_store_settings_border.border_title = "Theme Store"

        self.about = Static(classes="settings-section")
        self.about.border_title = "About"

    def compose(self) -> ComposeResult:
        with VerticalScroll(id="settings-wrapper"):
            with Container(id="settings-body"):
                with self.account_settings_border:
                    yield Button("PLACEHOLDER")
                with self.social_settings_border:
                    yield Button("PLACEHOLDER")
                with self.sound_settings_border:
                    yield SoundSettings(cm=self._cm, sm=self._sm)
                with self.theme_settings_border:
                    yield Button("PLACEHOLDER")
                with self.theme_store_settings_border:
                    yield Button("PLACEHOLDER")
                with self.about:
                    yield AboutSettings()
        yield Footer()
