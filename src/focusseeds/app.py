import pygame

from textual.app import App
from textual.widgets import Footer, Header
from textual.containers import Center
from textual.widgets._header import HeaderTitle

from focusseeds.clock import Clock
from focusseeds.settings import SettingsScreen


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
        ('ctrl+t', 'timer_mode', 'Timer Mode'),
        ('ctrl+s', 'open_settings', 'Settings')
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
        clock = self.query_one(Clock)
        clock.change_clock_mode()

    def action_open_settings(self):
        self.push_screen(SettingsScreen())

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
