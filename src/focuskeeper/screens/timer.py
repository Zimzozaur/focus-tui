from textual import on
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Input

from focuskeeper.constants import MIN_SESSION_LEN
from focuskeeper.controllers import TimerController
from focuskeeper.validators import ValueFrom5to300
from focuskeeper.widgets import AppHeader, ClockDisplay


class TimerScreen(Screen):
    TITLE = "Timer"
    BINDINGS = [
        ("ctrl+q", "quit_app", "Quit App"),
        ("ctrl+t", "stopwatch_mode", "Stopwatch"),
        ("ctrl+s", "open_settings", "Settings"),
    ]

    def action_quit_app(self) -> None:
        self._ctrl.quit_app()

    def action_stopwatch_mode(self) -> None:
        """Switch screen to Stopwatch."""
        self._ctrl.switch_to_stopwatch()

    def action_open_settings(self) -> None:
        """Open settings screen."""
        self._ctrl.open_settings()

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        """If clock is active refuse to use any shortcuts."""
        return not self._ctrl.active_session

    def __init__(self) -> None:
        super().__init__()
        self._clock_display = ClockDisplay()
        self._focus_button = Button("Focus", variant="success", id="focus-bt")
        self._session_len_input = Input(
            value="45",
            placeholder=f"Type {MIN_SESSION_LEN} to 300",
            restrict=r"^\d{1,3}$",
            validators=[ValueFrom5to300()],
            id="session-duration",
        )
        self._ctrl = TimerController(
            screen=self,
            clock=self._clock_display,
            focus_button=self._focus_button,
            session_len_input=self._session_len_input,
        )

    def compose(self):
        self._ctrl.set_app_title()
        yield AppHeader()
        with Horizontal(id="clock-wrapper"):
            yield self._clock_display
        with Vertical(id="focus-wrapper"):
            yield self._session_len_input
            yield self._focus_button
        yield Footer()

    @on(Button.Pressed, "#focus-bt")
    def _focus_button_clicked(self) -> None:
        """Start, Cancel, Kill session."""
        self._ctrl.focus_button_clicked()

    @on(Input.Changed, "#session-duration")
    def _is_valid_session_length(self, event: Input.Changed) -> None:
        """If the session duration is not correct block start button."""
        self._ctrl.is_valid_session_length(event)
