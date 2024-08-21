from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Static


class ConfirmPopup(ModalScreen[bool]):
    """ModalScreen to ask user for confirmation of certain action."""

    def __init__(self, *args: tuple, message: str, **kwargs: dict) -> None:
        super().__init__(*args, **kwargs)
        self.message = message

    def compose(self) -> ComposeResult:
        with Container(id="confirm-popup-body"):
            yield Static(self.message, id="confirm-popup-message")
            with Horizontal(id="confirm-popup-buttons"):
                yield Button("No", variant="error", id="no-button")
                yield Button("Yes", variant="success", id="yes-button")

    @on(Button.Pressed, "#no-button")
    def reject(self) -> None:
        """Return False to callback."""
        self.dismiss(False)

    @on(Button.Pressed, "#yes-button")
    def confirm(self) -> None:
        """Return True to callback."""
        self.dismiss(True)
