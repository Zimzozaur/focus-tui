import webbrowser

from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Grid
from textual.widgets import Button, Static

from focustui.constants import DISCORD_INVITATION, PROJECT_GITHUB, SIMONS_X_ACCOUNT


class AboutSettings(Container):
    def compose(self) -> ComposeResult:
        yield Static("FocusTUI is your best buddy for working or studying.")
        yield Static("If you want to learn more, share your ideas, or report bugs...")
        yield Static("Check out our media!")
        with Grid(id="get-into-social"):
            yield Button("Discord", id="discord")
            yield Button("Github", id="github")
            yield Button("X", id="x")

    @on(Button.Pressed, "#discord")
    def discord_pressed(self) -> None:
        webbrowser.open(DISCORD_INVITATION)

    @on(Button.Pressed, "#github")
    def github_pressed(self) -> None:
        webbrowser.open(PROJECT_GITHUB)

    @on(Button.Pressed, "#x")
    def x_pressed(self) -> None:
        webbrowser.open(SIMONS_X_ACCOUNT)
