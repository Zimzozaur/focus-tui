from textual.app import App
from textual.widgets import Footer, Header
from textual.containers import Center

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
    TITLE = 'Timer'
    BINDINGS = [
        ('ctrl+m', 'timer_mode', 'Timer Mode')
    ]

    def compose(self):
        yield Header()
        with Center(id='body'):
            yield Clock()
        yield Footer()

    def action_timer_mode(self):
        self.query_one(Clock).change_clock_mode()


if __name__ == "__main__":
    GrowBonsai().run()
