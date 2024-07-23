from textual import on
from textual.screen import Screen
from textual.widgets import Button, Footer
from textual.containers import Horizontal, Vertical

from focuskeeper.widgets import AppHeader
from focuskeeper.db import DatabaseManager
from focuskeeper.sound_manager import SoundManager
from focuskeeper.settings import MINUTE
from focuskeeper.widgets import ClockDisplay
from focuskeeper.screens import SettingsScreen


class StopwatchScreen(Screen):
    """
    Clock widget functionalities:
        - Time display for both timer and stopwatch modes.
        - Input field to set the timer duration.
        - Button to start, stop, or cancel the timer/stopwatch.
        - Play sound when session is successful
    """

    DEFAULT_CSS = """
    StopwatchScreen {
        width: 100%;
        height: 100%;
    }

    #focus-wrapper {
        align: center middle;
        height: 40%;
    }

    #session-duration {
        width: 21;
    }

    Button {
        align: center middle;
        margin-top: 1;
        margin-left: 2;
    }
    """
    BINDINGS = [
        ('ctrl+q', 'quit_app', 'Quit App'),
        ('ctrl+t', 'timer_mode', 'Timer Mode'),
        ('ctrl+s', 'open_settings', 'Settings'),
    ]

    def action_quit_app(self):
        self.app.exit()

    def action_timer_mode(self):
        """Change between Stopwatch and Timer"""
        from focuskeeper.screens import TimerScreen
        self.app.switch_screen(TimerScreen())

    def action_open_settings(self):
        """
        Open settings screen and dismiss clock
        When Settings are close opens new instance of clock back
        """
        def open_clock_back(result) -> None:
            """
            Result has to be passed to run callback
            but is not needed for this functino
            """
            self.app.push_screen(StopwatchScreen())

        self.dismiss()
        self.app.push_screen(SettingsScreen(), open_clock_back)

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        """If clock is active refuse to use any shortcut"""
        return not self.active_session

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Widgets
        self._clock_display = ClockDisplay()
        self._focus_button = Button('Focus', variant='success', id='focus-bt')
        # Mode
        self.active_session = False
        # Stopwatch time
        self._session_len: int = 0
        # Cancel session
        self._cancel_session_remaining: int = 0
        # Interval
        self._intervals = []
        # External classes
        self.db = DatabaseManager()
        self.sm = SoundManager()

    def compose(self):
        self.app.title = 'Stopwatch'
        yield AppHeader()
        with Horizontal(id='clock-wrapper'):
            yield self._clock_display
        with Vertical(id='focus-wrapper'):
            yield self._focus_button
        yield Footer()

    @on(Button.Pressed, '#focus-bt')
    def _focus_button_clicked(self) -> None:
        """Start, End session"""
        # Started Session
        if self._focus_button.variant == 'success':
            self.app.refresh_bindings()  # Deactivate Bindings
            self._start_session()
            self.active_session = True
        # Canceled Session
        elif self._focus_button.variant == 'warning':
            self._reset_timer()
        # Ended Session
        else:
            self._successful_session()

    def _start_session(self) -> None:
        """Start a timer session."""
        # Initialize cancel timer counter
        self._cancel_session_remaining = MINUTE

        # Set intervals for updating clock and managing cancel timer
        self._intervals.append(self.set_interval(1, self._clock_display_update))
        self._intervals.append(self.set_interval(1, self._cancel_session))

        # Set button variant to 'error' to indicate session is ongoing
        self._focus_button.variant = 'error'

    def _clock_display_update(self) -> None:
        """Update variable used by timer and update displayed time"""
        self._session_len += 1

        minutes, seconds = divmod(self._session_len, 60)
        minutes_str = str(minutes).zfill(1)
        seconds_str = str(seconds).zfill(2)
        self._clock_display.update_time(minutes_str, seconds_str)

    def _successful_session(self) -> None:
        """Play song, add successful session to DB and reset clock"""
        self.sm.play_alarm()
        self.db.create_session_entry(self._session_len // 60, 1)
        self._reset_timer()

    def _reset_timer(self) -> None:
        """Set all clock properties to default"""
        # Reset Timer
        self._clock_display.update_time('0', '00')
        # Reset Button
        self._focus_button.variant = 'success'
        self._focus_button.label = 'Focus'
        # Session Variable
        self.active_session = False
        # Stop intervals
        for interval in self._intervals:
            interval.stop()
        # Return which clock mode biding
        self.app.refresh_bindings()

    def _cancel_session(self):
        """
        Allow user to cancel timer in first
        `self._cancel_timer_counter_default` seconds
        """
        self._cancel_session_remaining -= 1
        if self._cancel_session_remaining > 0:
            self._focus_button.label = f'Cancel ({self._cancel_session_remaining})'
        else:
            # Set button when the cancel time has ended
            self._focus_button.label = 'End'
            self._focus_button.variant = 'error'
