from textual.screen import Screen
from textual.widgets import Button, Input

from focuskeeper.constants import MINUTE
from focuskeeper.controllers.controller import Controller
from focuskeeper.modals import ConfirmPopup
from focuskeeper.widgets import ClockDisplay


class TimerController(Controller):
    def __init__(
        self,
        screen: Screen,
        clock: ClockDisplay,
        focus_button: Button,
        session_len_input: Input,
    ) -> None:
        super().__init__()
        # External classes
        self._screen = screen
        self._clock_display = clock
        self._focus_button = focus_button
        self._session_len_input = session_len_input

        # Mode
        self._active_session = False
        # Timer time
        self._session_len: int = 0
        self._remaining_session: int = 0
        # Cancel session
        self._cancel_session_remaining: int = 0
        # Intervals
        self._intervals = []

    @property
    def active_session(self):
        return self._active_session

    def switch_to_stopwatch(self):
        from focuskeeper.screens import StopwatchScreen
        self.app.switch_screen(StopwatchScreen())

    def is_valid_session_length(self, event: Input.Changed):
        """If the session duration is not correct block start button."""
        self._focus_button.disabled = not event.input.is_valid

    def focus_button_clicked(self):
        """Start, Cancel, Kill session."""
        # Started Session
        if self._focus_button.variant == "success":
            self._active_session = True
            self.app.refresh_bindings()  # Deactivate Bindings
            self._session_len_input.visible = False
            self._start_session()
        # Cancel Session
        elif self._focus_button.variant == "warning":
            self._reset_timer()
        # Kill Session
        else:
            popup = ConfirmPopup(message="Do you want to kill the session?")
            self.app.push_screen(popup, self._not_successful_session)

    def _start_session(self) -> None:
        """Start a Timer session."""
        # Initialize cancel timer counter
        self._cancel_session_remaining = MINUTE
        self._session_len = int(self._screen.query_one(Input).value) * MINUTE
        self._remaining_session = self._session_len

        # Set intervals for updating clock and managing cancel timer
        update_clock = self._screen.set_interval(1, self._clock_display_update)
        cancel_session = self._screen.set_interval(1, self._cancel_session)
        self._intervals.extend([update_clock, cancel_session])

        # Set button variant to 'warning' to indicate session is ongoing
        self._focus_button.variant = "warning"

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
        self._sm.play_alarm()
        self._db.create_session_entry(self._session_len // 60, 1)
        self._reset_timer()

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
