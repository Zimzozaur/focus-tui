from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Static, Button


class ConfirmPopup(ModalScreen):
    """ModalScreen to ask user for confirmation of certain action"""

    DEFAULT_CSS = """
        ConfirmPopup {
            align: center middle;
            width: auto;
            height: auto;
        }

        #confirm-popup-body {
            width: auto;
            height: auto;
            padding: 1 2;
            background: $panel;
        }

        #confirm-popup-message {
            text-style: bold;
        }

        #confirm-popup-buttons {
            width: auto;
            height: auto;
            margin-top: 1;

            & > #yes-button {
                margin-left: 10;
            }
        }
        """

    def __init__(self, *args, message: str, **kwargs):
        super().__init__(*args, **kwargs)
        self.message: str = message

    def compose(self) -> ComposeResult:
        with Container(id='confirm-popup-body'):
            yield Static(self.message, id='confirm-popup-message')
            with Horizontal(id='confirm-popup-buttons'):
                yield Button('No', variant='error', id='no-button')
                yield Button('Yes', variant='success', id='yes-button')

    @on(Button.Pressed, '#no-button')
    def reject(self):
        """Return False to callback"""
        self.dismiss(False)

    @on(Button.Pressed, '#yes-button')
    def confirm(self):
        """Return True to callback"""
        self.dismiss(True)
