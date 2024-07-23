import pygame

from textual.app import App

from focuskeeper.screens import TimerScreen


class FocusKeeper(App, inherit_bindings=False):
    DEFAULT_CSS = """
    #body {
        background: $surface;
        padding: 1 2;
        width: 100%;
        height: 100%;
    }
    """
    ENABLE_COMMAND_PALETTE = False

    def __init__(self):
        super().__init__()
        pygame.init()
        pygame.mixer.init()

    def on_mount(self):
        self.push_screen(TimerScreen())
