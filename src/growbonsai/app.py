from textual.app import App
from textual.widgets import Footer
from textual.containers import Center

from _numbers import NUMBERS_DICT
from clock import Clock


class GrowBonsai(App):
    DEFAULT_CSS = """
    #body {
        border: heavy red;
        background: $surface;
        padding: 1 2;
        width: 100%;
        height: 100%;
    }
    """
    BINDINGS = [
        ('ctrl+m', 'timer_mode', 'Timer Mode')
    ]

    def compose(self):
        with Center(id='body'):
            yield Clock(
                '',
                '',
                NUMBERS_DICT['0'],
                NUMBERS_DICT['0'],
                NUMBERS_DICT['0']
            )
        yield Footer()


if __name__ == "__main__":
    GrowBonsai().run()
