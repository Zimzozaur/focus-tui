from textual import on
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Footer

from focuskeeper.composite_widgets import ClockDisplay
from focuskeeper.constants import MINUTE
from focuskeeper.screens import BaseScreen
from focuskeeper.widgets import AppHeader


class StopwatchScreen(BaseScreen):
    TITLE = "Stopwatch"
    BINDINGS = [
        ("ctrl+q", "quit_app", "Quit App"),
        ("ctrl+t", "timer_mode", "Timer Mode"),
        ("ctrl+s", "open_settings", "Settings"),
        ("ctrl+a", "play_ambient", "Play/Pause Ambient"),
    ]

    def action_quit_app(self) -> None:
        self.app.exit()

    def action_timer_mode(self) -> None:
        """Switch screen to Timer."""
        from focuskeeper.screens import TimerScreen
        self.app.push_screen(TimerScreen())

    def action_open_settings(self) -> None:
        """Open settings screen."""
        self.app.open_settings()

    def action_play_ambient(self):
        self._ambient_silent = not self._ambient_silent
        self._sm.toggle_ambient(self._ambient_silent)

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        """If clock is active allow to play ambient and hide rest."""
        if action == "play_ambient":
            return self._active_session
        return not self._active_session

    def __init__(self, *args: tuple, **kwargs: dict) -> None:
        super().__init__(*args, **kwargs)
        self._clock_display = ClockDisplay()
        self._focus_button = Button("Focus", variant="success", id="focus-bt")
        # Mode
        self._active_session = False
        # Stopwatch time
        self._session_len: int = 0
        # Cancel session
        self._cancel_session_remaining: int = MINUTE
        # Interval
        self._intervals = []
        self._ambient_silent: bool = True

    def compose(self):
        self.app.title = "Stopwatch"
        yield AppHeader()
        with Horizontal(id="clock-wrapper"):
            yield self._clock_display
        with Vertical(id="focus-wrapper"):
            yield self._focus_button
        yield Footer()

    @on(Button.Pressed, "#focus-bt")
    def _focus_button_clicked(self) -> None:
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
        self.app.refresh_bindings()

        # Set intervals for updating clock and managing cancel timer
        update_clock = self.screen.set_interval(1, self._clock_display_update)
        cancel_session = self.screen.set_interval(1, self._cancel_session)
        self._intervals.extend([update_clock, cancel_session])

        # Start playing ambient in the background
        self._sm.play_ambient_in_background()

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
        self._sm.play_alarm()

    def _reset_timer(self) -> None:
        """Set all clock properties to default."""
        # Reset Timer
        self._clock_display.update_time("0", "00")
        # Reset Button
        self._focus_button.variant = "success"
        self._focus_button.label = "Focus"
        # Allow user to use shorts
        self._active_session = False
        self.app.refresh_bindings()
        # Reset Counters
        self._session_len = 0
        self._cancel_session_remaining = MINUTE
        # Stop intervals
        for interval in self._intervals:
            interval.stop()
        # Restart ambient variable to not play at the start
        self._ambient_silent = True
        # Stop playing ambient in the background
        self._sm.stop_ambient_in_background()

    def _cancel_session(self) -> None:
        """Allow user to cancel session in first minute."""
        self._cancel_session_remaining -= 1
        if self._cancel_session_remaining > 0:
            self._focus_button.label = f"Cancel ({self._cancel_session_remaining})"
        else:
            # Update button when the cancel time has ended
            self._focus_button.label = "End"
            self._focus_button.variant = "error"
