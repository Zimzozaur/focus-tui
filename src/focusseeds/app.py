import pygame

from textual.app import App
from textual.widgets import Footer

from focusseeds.clock import Clock
from focusseeds._app import AppHeader


class FocusSeeds(App):
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

    def check_action(
        self,
        action: str,
        parameters: tuple[object, ...]
    ) -> bool | None:
        print(action)
        if action == 'timer_mode':
            return not self.query_one(Clock).active_session

        # Otherwise you cannot close app LOL (ctrl+c default biding)
        return True
