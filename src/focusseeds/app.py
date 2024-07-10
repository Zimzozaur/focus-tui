import pygame

from textual.app import App
from textual.widgets import Footer, Header
from textual.containers import Center
from textual.widgets._header import HeaderTitle

from focusseeds.clock import Clock


class AppHeader(Header):
    def compose(self):
        yield HeaderTitle()


class FocusSeeds(App):
    DEFAULT_CSS = """
    #body {
        background: $surface;
        padding: 1 2;
        width: 100%;
        height: 100%;
    }
    """
    TITLE = 'Timer'
    BINDINGS = [
        ('ctrl+t', 'timer_mode', 'Timer Mode')
    ]
    ENABLE_COMMAND_PALETTE = False

    def __init__(self):
        super().__init__()
        pygame.init()
        pygame.mixer.init()

    def compose(self):
        yield AppHeader()
        with Center(id='body'):
            yield Clock()
        yield Footer()

    def action_timer_mode(self):
        self.query_one(Clock).change_clock_mode()

