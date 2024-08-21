from textual import on
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer

from focuskeeper.controllers import StopwatchController
from focuskeeper.widgets import AppHeader, ClockDisplay


class StopwatchScreen(Screen):
    TITLE = "Stopwatch"
    BINDINGS = [
        ("ctrl+q", "quit_app", "Quit App"),
        ("ctrl+t", "timer_mode", "Timer Mode"),
        ("ctrl+s", "open_settings", "Settings"),
    ]

    def action_quit_app(self) -> None:
        self._ctrl.quit_app()

    def action_timer_mode(self) -> None:
        """Switch screen to Timer."""
        self._ctrl.switch_to_timer()

    def action_open_settings(self) -> None:
        """Open settings screen."""
        self._ctrl.open_settings()

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        """If Stopwatch is active refuse to use any shortcuts."""
        return not self._ctrl.active_session

    def __init__(self, *args: tuple, **kwargs: dict) -> None:
        super().__init__(*args, **kwargs)
        self._clock_display = ClockDisplay()
        self._focus_button = Button("Focus", variant="success", id="focus-bt")
        self._ctrl = StopwatchController(
            screen=self,
            clock=self._clock_display,
            focus_button=self._focus_button,
        )

    def compose(self):
        self._ctrl.set_app_title("Stopwatch")
        yield AppHeader()
        with Horizontal(id="clock-wrapper"):
            yield self._clock_display
        with Vertical(id="focus-wrapper"):
            yield self._focus_button
        yield Footer()

    @on(Button.Pressed, "#focus-bt")
    def _focus_button_clicked(self) -> None:
        self._ctrl.focus_button_clicked()

