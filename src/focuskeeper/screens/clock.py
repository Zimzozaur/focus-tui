from datetime import datetime
from textual import on
from textual.screen import Screen
from textual.widgets import Button, Static, Label, Input, Footer
from textual.containers import Horizontal, Vertical

from focuskeeper.widgets import AppHeader
from focuskeeper.assets import NUMBERS_DICT
from focuskeeper.screens.settings import SettingsScreen
from focuskeeper.validators import ValueFrom5to300
from focuskeeper.modals import ConfirmPopup
from focuskeeper.db import DatabaseManager
from focuskeeper.sound_manager import SoundManager


class Clock(Screen):
    """
    Clock widget functionalities:
        - Time display for both timer and stopwatch modes.
        - Input field to set the timer duration.
        - Button to start, stop, or cancel the timer/stopwatch.
        - Play sound when session is successful
    """

    DEFAULT_CSS = """
    Clock {
        width: 100%;
        height: 100%;
    }

    #clock-wrapper {
        align: center middle;
        height: 60%;
    }

    #seed-wrapper {
        align: center middle;
        height: 40%;
    }

    Static {
        width: auto;
        color: $warning-lighten-1;
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
        self.change_clock_mode()

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
            self.app.push_screen(Clock())

        self.dismiss()
        self.app.push_screen(SettingsScreen(), open_clock_back)

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        """If clock is active refuse to use any shortcut"""
        if self.active_session:
            return False

        return True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Widgets
        self._h_min = Static('')
        self._t_min = Static('')
        self._u_min = Static(NUMBERS_DICT['0'])
        self._t_sec = Static(NUMBERS_DICT['0'])
        self._u_sec = Static(NUMBERS_DICT['0'])
        self._seed_button = Button('Seed', variant='success', id='seed-bt')
        self._input_filed = Input(
            value='45',
            placeholder='Type 5 to 300',
            restrict=r'^\d{1,3}$',
            validators=[ValueFrom5to300()],
            id='session-duration'
        )
        # Mode
        self.active_session = False
        self._clock_mode: str = 'Timer'
        # Stopwatch
        self._stopwatch_started: datetime = datetime.now()
        # Timer - sessions are stored in seconds
        self._timer_session_len: int = 0
        self._timer_remaining_session: int = 0
        # Cancel session
        # TODO: Modify for production
        self._cancel_session_counter_default = 3
        self._cancel_session_counter: int = 0
        # Clock - When ever user start clock they get restarted
        # Used to print time on a screen
        self._minutes: float = 0
        self._seconds: float = 0
        # Intervals
        self._intervals = []
        # External classes
        self.db = DatabaseManager()
        self.sm = SoundManager()

    def compose(self):
        self.app.title = 'Timer'
        yield AppHeader()
        with Horizontal(id='clock-wrapper'):
            yield self._h_min
            yield Label(' ')
            yield self._t_min
            yield Label(' ')
            yield self._u_min
            yield Label(' ')
            yield Static(NUMBERS_DICT[':'])
            yield Label(' ')
            yield self._t_sec
            yield Label(' ')
            yield self._u_sec
        with Vertical(id='seed-wrapper'):
            yield self._input_filed
            yield self._seed_button
        yield Footer()

    @on(Button.Pressed, '#seed-bt')
    def _seed_button_clicked(self) -> None:
        """Start, Cancel, Kill timer or stopwatch depend on the chosen mode"""
        # Start timer
        if self._seed_button.variant == 'success':
            self.app.refresh_bindings()  # Remove switch clock mode biding
            self._input_filed.visible = False
            self._start_session()
            self.active_session = True
        # Cancel timer
        elif self._seed_button.variant == 'warning':
            self._reset_clock()
        # Kill/End timer
        else:
            # Timer
            if self._clock_mode == 'Timer':
                # If user accepts to kill session, `self._not_successful_session` is called
                popup = ConfirmPopup(message='Do you want to kill the session?')
                self.app.push_screen(popup, self._not_successful_session)
            # Stopwatch
            else:
                self._successful_session(self._minutes)

    def _start_session(self) -> None:
        """Start a timer or stopwatch session based on the current clock mode."""
        # Initialize cancel timer counter
        self._cancel_session_counter = self._cancel_session_counter_default

        if self._clock_mode == 'Timer':
            # TODO: Modify for production
            self._timer_session_len = int(self.query_one(Input).value) * 1
            self._timer_remaining_session = self._timer_session_len
        else:
            self._stopwatch_started = datetime.now()

        # Select appropriate clock mode function
        clock_mode_func = self._timer if self._clock_mode == 'Timer' else self._stopwatch

        # Set intervals for updating clock and managing cancel timer
        session_interval = self.set_interval(1, clock_mode_func)
        cancel_session_interval = self.set_interval(1, self._cancel_session)
        self._intervals.extend((session_interval, cancel_session_interval))

        # Set button variant to 'warning' to indicate session is ongoing
        self._seed_button.variant = 'warning'

    def _stopwatch(self) -> None:
        """Update variable used by stopwatch and update displayed time"""
        elapsed_time = datetime.now() - self._stopwatch_started
        self._minutes, self._seconds = divmod(elapsed_time.total_seconds(), 60)
        self._update_clock()

    def _timer(self) -> None:
        """Update variable used by timer and update displayed time"""
        self._timer_remaining_session -= 1
        # When end of the session
        if self._timer_remaining_session == 0:
            self._successful_session(self._timer_session_len // 60)
        else:
            self._minutes, self._seconds = divmod(self._timer_remaining_session, 60)
            self._update_clock()

    def _successful_session(self, minutes: float) -> None:
        """Play song, add successful session to DB and reset clock"""
        self.sm.play_alarm()
        self.db.create_session_entry(int(minutes), 1)
        self._reset_clock()

    def _not_successful_session(self, boolean: bool) -> None:
        """Add killed session to DB and reset clock"""
        if not boolean:
            return
        self.db.create_session_entry(int(self._minutes), 0)
        self._reset_clock()

    def _reset_clock(self) -> None:
        """Set all clock properties to default"""
        # Reset Timer
        self._h_min.update('')
        self._t_min.update('')
        self._u_min.update(NUMBERS_DICT['0'])
        self._t_sec.update(NUMBERS_DICT['0'])
        self._u_sec.update(NUMBERS_DICT['0'])
        # Reset Button
        self._seed_button.variant = 'success'
        self._seed_button.label = 'Seed'
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

    def _update_clock(self):
        """Update displayed digits"""
        minutes_str = str(int(self._minutes)).zfill(2)
        seconds_str = str(int(self._seconds)).zfill(2)

        if int(self._minutes) >= 100:
            self._h_min.update(NUMBERS_DICT[minutes_str[-3]])
        else:
            self._h_min.update('')

        if int(self._minutes) >= 10:
            self._t_min.update(NUMBERS_DICT[minutes_str[-2]])
        else:
            self._t_min.update('')

        self._u_min.update(NUMBERS_DICT[minutes_str[-1]])
        self._t_sec.update(NUMBERS_DICT[seconds_str[-2]])
        self._u_sec.update(NUMBERS_DICT[seconds_str[-1]])

    def _cancel_session(self):
        """
        Allow user to cancel timer in first
        `self._cancel_timer_counter_default` seconds
        """
        self._cancel_session_counter -= 1
        if self._cancel_session_counter > 0:
            self._seed_button.label = f'Cancel ({self._cancel_session_counter})'
        else:
            # Set button when the cancel time has ended
            self._seed_button.label = 'Kill' if self._clock_mode == 'Timer' else 'End'
            self._seed_button.variant = 'error'

    @on(Input.Changed, '#session-duration')
    def _timer_session_duration_changed(self, event: Input.Changed) -> None:
        """If the session duration is not correct block start button."""
        if event.input.is_valid:
            self.query_one('#seed-bt', Button).disabled = False
        else:
            self.query_one('#seed-bt', Button).disabled = True

    def change_clock_mode(self):
        """
        Change between `timer` and `stopwatch`
        Remove input when changing to stopwatch
        Insert input when changing to timer
        """
        if self._clock_mode == 'Timer':
            self._clock_mode = self.app.title = 'Stopwatch'
            self.query_one(Input).remove()
        else:
            self._clock_mode = self.app.title = 'Timer'
            self._input_filed = Input(
                value='45',
                placeholder='Type number from 5 to 300',
                restrict=r'^\d{1,3}$',
                validators=[ValueFrom5to300()],
                id='session-duration'
            )
            self.mount(self._input_filed, before='#seed-bt')
