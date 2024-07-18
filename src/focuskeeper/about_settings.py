import webbrowser

from textual import on
from textual.app import ComposeResult
from textual.widgets import Button
from textual.containers import Grid


class AboutSettings(Grid):
    DEFAULT_CSS = """
    AboutSettings {
        grid-size: 3 1;
        grid-gutter: 10;
        height: auto;
        padding: 1;
    }    
    """

    def compose(self) -> ComposeResult:
        yield Button('Discord', id='discord')
        yield Button('Github', id='github')
        yield Button('X', id='x')

    @on(Button.Pressed, '#discord')
    def discord_pressed(self) -> None:
        webbrowser.open('https://discord.gg/a2TyMhXQ')

    @on(Button.Pressed, '#github')
    def github_pressed(self) -> None:
        webbrowser.open('https://github.com/Zimzozaur/FocusKeeper-TUI')

    @on(Button.Pressed, '#x')
    def x_pressed(self) -> None:
        webbrowser.open('https://x.com/zimzozaur')
