import webbrowser

from textual import on
from textual.app import ComposeResult
from textual.widgets import Button, Static
from textual.containers import Grid, Container


class AboutSettings(Container):
    DEFAULT_CSS = """
    AboutSettings {
        height: auto;
        padding: 1;    
    }

    #get-into-social {
        grid-size: 3 1;
        grid-gutter: 10;
        height: auto;
        padding-top: 1;
    }    
    """

    def compose(self) -> ComposeResult:
        yield Static('Focus Keeper is your best buddy for working or studying.')
        yield Static('If you want to learn more, share your ideas, or report bugs...')
        yield Static('Check out our media!')
        with Grid(id='get-into-social'):
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
