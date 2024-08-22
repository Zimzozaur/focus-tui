import pygame
from textual.app import App


class FocusKeeper(App, inherit_bindings=False):
    ENABLE_COMMAND_PALETTE = False
    CSS_PATH = "style.tcss"

    def __init__(self) -> None:
        super().__init__()
        pygame.init()

    def on_mount(self) -> None:
        from focuskeeper.screens import TimerScreen
        self.push_screen(TimerScreen())


FOCUS_KEEPER = FocusKeeper()
