import pygame
from textual.app import App

from focustui.screens import FocusScreen, SettingsScreen


class FocusTUI(App, inherit_bindings=False):
    ENABLE_COMMAND_PALETTE = False
    CSS_PATH = "style.tcss"

    def __init__(self) -> None:
        super().__init__()
        pygame.init()

    def on_mount(self):
        self.push_screen(FocusScreen())

    def open_settings(self):
        """Push settings screen."""
        self.push_screen(SettingsScreen())
