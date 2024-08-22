from textual.screen import Screen
from textual.widgets import Button

from focuskeeper.constants import MINUTE
from focuskeeper.controllers.controller import Controller
from focuskeeper.widgets import ClockDisplay


class StopwatchController(Controller):
    def __init__(
        self,
        screen: Screen,
        clock: ClockDisplay,
        focus_button: Button,
    ) -> None:
        super().__init__()
        # External classes
        self._screen = screen
        self._clock_display = clock
        self._focus_button = focus_button
        # Mode
        self._active_session = False
        # Stopwatch time
        self._session_len: int = 0
        # Cancel session
        self._cancel_session_remaining: int = MINUTE
        # Interval
        self._intervals = []

    @property
    def active_session(self):
        return self._active_session

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        """If clock is active allow to play ambient and hide rest."""
        if action == "play_ambient":
            return self.active_session
        return not self.active_session

    def switch_to_timer(self):
        from focuskeeper.screens import TimerScreen
        self._app.switch_screen(TimerScreen())

    def focus_button_clicked(self):
        """Start, Cancel, End session."""
        # Started Session
        if self._focus_button.variant == "success":
            self._start_session()
        # Canceled Session
        elif self._focus_button.variant == "warning":
            self._reset_timer()
        # Ended Session
        else:
            self._successful_session()

    def _start_session(self) -> None:
        """Start a stopwatch session."""
        # Set button variant to 'error' to indicate session is ongoing
        self._focus_button.variant = "warning"

        # Deactivate Bindings
        self._active_session = True
        self._app.refresh_bindings()

        # Set intervals for updating clock and managing cancel timer
        update_clock = self._screen.set_interval(1, self._clock_display_update)
        cancel_session = self._screen.set_interval(1, self._cancel_session)
        self._intervals.extend([update_clock, cancel_session])

        # Start playing ambient in the background
        self.start_ambient()

    def _clock_display_update(self) -> None:
        """Update variable used by timer and update displayed time."""
        # Update session length
        self._session_len += 1
        # Update clock display
        minutes, seconds = divmod(self._session_len, 60)
        minutes_str = str(minutes).zfill(1)
        seconds_str = str(seconds).zfill(2)
        self._clock_display.update_time(minutes_str, seconds_str)

    def _successful_session(self) -> None:
        """Play song, add successful session to DB and reset clock."""
        self._db.create_session_entry(self._session_len // 60, 1)
        self._reset_timer()
        self.play_alarm()

    def _reset_timer(self) -> None:
        """Set all clock properties to default."""
        # Reset Timer
        self._clock_display.update_time("0", "00")
        # Reset Button
        self._focus_button.variant = "success"
        self._focus_button.label = "Focus"
        # Allow user to use shorts
        self._active_session = False
        self._app.refresh_bindings()
        # Reset Counters
        self._session_len = 0
        self._cancel_session_remaining = MINUTE
        # Stop intervals
        for interval in self._intervals:
            interval.stop()
        # Restart ambient variable to not play at the start
        self._ambient_silent = True
        # Stop playing ambient in the background
        self.stop_ambient()

    def _cancel_session(self) -> None:
        """Allow user to cancel session in first minute."""
        self._cancel_session_remaining -= 1
        if self._cancel_session_remaining > 0:
            self._focus_button.label = f"Cancel ({self._cancel_session_remaining})"
        else:
            # Update button when the cancel time has ended
            self._focus_button.label = "End"
            self._focus_button.variant = "error"
