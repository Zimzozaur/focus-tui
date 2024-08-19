import pygame
from textual.app import App

from focuskeeper.screens import TimerScreen


class FocusKeeper(App, inherit_bindings=False):
    ENABLE_COMMAND_PALETTE = False
    CSS_PATH = "style.tcss"

    def __init__(self) -> None:
        super().__init__()
        pygame.init()
        pygame.mixer.init()

    def on_mount(self) -> None:
        self.push_screen(TimerScreen())
