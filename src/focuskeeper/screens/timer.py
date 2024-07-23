from textual import on
from textual.screen import Screen
from textual.widgets import Button, Input, Footer
from textual.containers import Horizontal, Vertical

from focuskeeper.widgets import AppHeader
from focuskeeper.validators import ValueFrom5to300
from focuskeeper.modals import ConfirmPopup
from focuskeeper.db import DatabaseManager
from focuskeeper.sound_manager import SoundManager
from focuskeeper.settings import MINUTE
from focuskeeper.widgets import ClockDisplay
from focuskeeper.screens import SettingsScreen


class TimerScreen(Screen):
    TITLE = 'Timer'
    BINDINGS = [
        ('ctrl+q', 'quit_app', 'Quit App'),
        ('ctrl+t', 'stopwatch_mode', 'Stopwatch'),
        ('ctrl+s', 'open_settings', 'Settings'),
    ]

    def action_quit_app(self):
        self.app.exit()

    def action_stopwatch_mode(self):
        """Switch screen to Stopwatch"""
        from focuskeeper.screens import StopwatchScreen
        self.app.switch_screen(StopwatchScreen())

    def action_open_settings(self):
        """Open settings screen"""
        self.app.push_screen(SettingsScreen())

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        """If clock is active refuse to use any shortcuts"""
        return not self.active_session

    def __init__(self):
        super().__init__()
        # Widgets
        self._clock_display = ClockDisplay()
        self._focus_button = Button('Focus', variant='success', id='focus-bt')
        self._input_filed = Input(
            value='45',
            placeholder='Type 5 to 300',
            restrict=r'^\d{1,3}$',
            validators=[ValueFrom5to300()],
            id='session-duration'
        )
        # Mode
        self.active_session = False
        # Timer time
        self._session_len: int = 0
        self._remaining_session: int = 0
        # Cancel session
        self._cancel_session_remaining: int = 0
        # Intervals
        self._intervals = []
        # External classes
        self.db = DatabaseManager()
        self.sm = SoundManager()

    def compose(self):
        self.app.title = 'Timer'
        yield AppHeader()
        with Horizontal(id='clock-wrapper'):
            yield self._clock_display
        with Vertical(id='focus-wrapper'):
            yield self._input_filed
            yield self._focus_button
        yield Footer()

    @on(Button.Pressed, '#focus-bt')
    def _focus_button_clicked(self) -> None:
        """Start, Cancel, Kill session"""
        # Started Session
        if self._focus_button.variant == 'success':
            self.active_session = True
            self.app.refresh_bindings()  # Deactivate Bindings
            self._input_filed.visible = False
            self._start_session()
        # Cancel Session
        elif self._focus_button.variant == 'warning':
            self._reset_timer()
        # Kill Session
        else:
            popup = ConfirmPopup(message='Do you want to kill the session?')
            self.app.push_screen(popup, self._not_successful_session)

    def _start_session(self) -> None:
        """Start a Timer session."""
        # Initialize cancel timer counter
        self._cancel_session_remaining = MINUTE
        self._session_len = int(self.query_one(Input).value) * MINUTE
        self._remaining_session = self._session_len

        # Set intervals for updating clock and managing cancel timer
        self._intervals.append(self.set_interval(1, self._clock_display_update))
        self._intervals.append(self.set_interval(1, self._cancel_session))

        # Set button variant to 'warning' to indicate session is ongoing
        self._focus_button.variant = 'warning'

    def _clock_display_update(self) -> None:
        """Update variable used by timer, update displayed time and
        call `TimerScreen._successful_session()` when self._remaining_session == 0"""
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
        """Play song, add successful session to DB and reset clock"""
        self.sm.play_alarm()
        self.db.create_session_entry(self._session_len // 60, 1)
        self._reset_timer()

    def _not_successful_session(self, boolean: bool) -> None:
        """Add killed session to DB and reset clock"""
        if not boolean:
            return

        focused_for = (self._session_len - self._remaining_session) // MINUTE
        self.db.create_session_entry(focused_for, 0)
        self._reset_timer()

    def _reset_timer(self) -> None:
        """Set all clock properties to default"""
        # Reset Timer
        self._clock_display.update_time('0', '00')
        # Reset Button
        self._focus_button.variant = 'success'
        self._focus_button.label = 'Focus'
        # Unhidden Input
        self._input_filed.visible = True
        # Session Variable
        self.active_session = False
        # Stop intervals
        for interval in self._intervals:
            interval.stop()
        self._intervals.clear()
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
            self._focus_button.label = 'Kill'
            self._focus_button.variant = 'error'

    @on(Input.Changed, '#session-duration')
    def _is_valid_session_length(self, event: Input.Changed) -> None:
        """If the session duration is not correct block start button."""
        self._focus_button.disabled = not event.input.is_valid
