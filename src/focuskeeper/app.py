import pygame

from textual.app import App
from textual.widgets import Footer

from focuskeeper.clock import Clock
from focuskeeper._app import AppHeader


class FocusSeeds(App, inherit_bindings=False):
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

    def compose(self):
        yield AppHeader()
        yield Footer()
        self.push_screen(Clock())
