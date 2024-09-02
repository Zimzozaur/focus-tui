from typing import TYPE_CHECKING

import pygame
from textual.app import App

from focustui.screens import FocusScreen, SettingsScreen

if TYPE_CHECKING:
    from focustui.config_manager import ConfigManager
    from focustui.db import DatabaseManager
    from focustui.sound_manager import SoundManager


class FocusTUI(App, inherit_bindings=False):
    ENABLE_COMMAND_PALETTE = False
    CSS_PATH = "style.tcss"

    def __init__(
        self,
        db: "DatabaseManager",
        cm: "ConfigManager",
        sm: "SoundManager",
    ) -> None:
        super().__init__()
        self._db = db
        self._cm = cm
        self._sm = sm

        pygame.init()

    def on_mount(self):
        self.push_screen(FocusScreen(cm=self._cm, db=self._db, sm=self._sm))

    def open_settings(self):
        """Switch to settings screen."""
        self.switch_screen(SettingsScreen(cm=self._cm, sm=self._sm))

    def open_focus(self):
        """Switch to focus screen."""
        self.switch_screen(FocusScreen(cm=self._cm, db=self._db, sm=self._sm))
