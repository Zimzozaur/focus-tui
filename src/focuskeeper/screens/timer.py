from textual import on
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Footer, Input

from focuskeeper.composite_widgets import ClockDisplay
from focuskeeper.constants import MAX_SESSION_LEN, MIN_SESSION_LEN, MINUTE
from focuskeeper.modals import ConfirmPopup
from focuskeeper.screens import BaseScreen
from focuskeeper.validators import ValueFrom5to300
from focuskeeper.widgets import AppHeader

tooltip = (f"Type value between {MIN_SESSION_LEN} and "
           f"{MAX_SESSION_LEN}\nto set focus session length.")


class TimerScreen(BaseScreen):
    TITLE = "Timer"
    BINDINGS = [
        ("ctrl+q", "quit_app", "Quit App"),
        ("ctrl+t", "stopwatch_mode", "Stopwatch"),
        ("ctrl+s", "open_settings", "Settings"),
        ("ctrl+a", "play_ambient", "Play/Pause Ambient"),
    ]

    def action_quit_app(self) -> None:
        self.app.exit()

    def action_stopwatch_mode(self) -> None:
        """Switch screen to Stopwatch."""
        from focuskeeper.screens import StopwatchScreen
        self.app.switch_screen(StopwatchScreen())

    def action_open_settings(self) -> None:
        """Open settings screen."""
        self.app.open_settings()

    def action_play_ambient(self):
        self._ambient_silent = not self._ambient_silent
        self._sm.toggle_ambient(self._ambient_silent)

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        """If clock is active allow to toggle ambient and hide rest."""
        if action == "play_ambient":
            return self._active_session
        return not self._active_session

    def __init__(self) -> None:
        super().__init__()
        self._clock_display = ClockDisplay()
        self._focus_button = Button("Focus", variant="success", id="focus-bt")
        self._session_len_input = Input(
            value="45",
            placeholder=f"Type {MIN_SESSION_LEN} to {MAX_SESSION_LEN}",
            restrict=r"^\d{1,3}$",
            validators=[ValueFrom5to300()],
            id="session-duration",
            tooltip=tooltip,

        )
        # Mode
        self._active_session = False
        # Timer time
        self._session_len: int = 0
        self._remaining_session: int = 0
        # Cancel session
        self._cancel_session_remaining: int = 0
        # Intervals
        self._intervals = []
        self._ambient_silent: bool = True

    def compose(self):
        self.app.title = "Timer"
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
        # Started Session
        if self._focus_button.variant == "success":
            self._start_session()
        # Cancel Session
        elif self._focus_button.variant == "warning":
            self._reset_timer()
        # Kill Session
        else:
            popup = ConfirmPopup(message="Do you want to kill the session?")
            self.app.push_screen(popup, self._not_successful_session)

    @on(Input.Changed, "#session-duration")
    def _is_valid_session_length(self, event: Input.Changed) -> None:
        """If the session duration is not correct block start button."""
        self._focus_button.disabled = not event.input.is_valid

    def _start_session(self) -> None:
        """Start a Timer session."""
        self._active_session = True
        self.app.refresh_bindings()  # Deactivate Bindings
        self._session_len_input.visible = False

        # Initialize cancel timer counter
        self._cancel_session_remaining = MINUTE
        self._session_len = int(self.screen.query_one(Input).value) * MINUTE
        self._remaining_session = self._session_len

        # Set intervals for updating clock and managing cancel timer
        update_clock = self.screen.set_interval(1, self._clock_display_update)
        cancel_session = self.screen.set_interval(1, self._cancel_session)
        self._intervals.extend([update_clock, cancel_session])

        # Set button variant to 'warning' to indicate session is ongoing
        self._focus_button.variant = "warning"

        # Start playing ambient in the background
        self._sm.play_ambient_in_background()

    def _clock_display_update(self) -> None:
        """Update variable used by timer, update displayed time and
        call `TimerScreen._successful_session()` when self._remaining_session == 0.
        """
        self._remaining_session -= 1
        # When end of the session
        if self._remaining_session == 0:
            self._successful_session()
        else:
            minutes, seconds = divmod(self._remaining_session, 60)
            minutes_str = str(minutes).zfill(1)
            seconds_str = str(seconds).zfill(2)
            self._clock_display.update_time(minutes_str, seconds_str)

    def _successful_session(self) -> None:
        """Play song, add successful session to DB and reset clock."""
        self._db.create_session_entry(self._session_len // 60, 1)
        self._reset_timer()
        self._sm.play_alarm()

    def _not_successful_session(self, should_kill: bool) -> None:
        """Add killed session to DB and reset clock."""
        if not should_kill:
            return

        focused_for = (self._session_len - self._remaining_session) // MINUTE
        self._db.create_session_entry(focused_for, 0)
        self._reset_timer()

    def _reset_timer(self) -> None:
        """Set all clock properties to default."""
        # Reset Timer
        self._clock_display.update_time("0", "00")
        # Reset Button
        self._focus_button.variant = "success"
        self._focus_button.label = "Focus"
        # Unhidden Input
        self._session_len_input.visible = True
        # Session Variable
        self._active_session = False
        # Stop intervals
        for interval in self._intervals:
            interval.stop()
        self._intervals.clear()
        # Return which clock mode biding
        self.app.refresh_bindings()
        # Restart ambient variable to not play at the start
        self._ambient_silent = True
        # Stop playing ambient in the background
        self._sm.stop_ambient_in_background()

    def _cancel_session(self) -> None:
        """Allow user to cancel timer in first
        `self._cancel_timer_counter_default` seconds.
        """
        self._cancel_session_remaining -= 1
        if self._cancel_session_remaining > 0:
            self._focus_button.label = f"Cancel ({self._cancel_session_remaining})"
        else:
            # Set button when the cancel time has ended
            self._focus_button.label = "Kill"
            self._focus_button.variant = "error"
