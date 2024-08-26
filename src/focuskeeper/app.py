import pygame
from textual.app import App

from focuskeeper.screens import SettingsScreen, TimerScreen


class FocusKeeper(App, inherit_bindings=False):
    ENABLE_COMMAND_PALETTE = False
    CSS_PATH = "style.tcss"

    def __init__(self) -> None:
        super().__init__()
        pygame.init()

    def on_mount(self):
        self.push_screen(TimerScreen())

    def open_settings(self):
        self.push_screen(SettingsScreen())
