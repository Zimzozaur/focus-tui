from datetime import datetime
from textual import on
from textual.widgets import Button, Static, Label, Input
from textual.containers import Horizontal, Container, Center, Middle, Vertical

from _numbers import NUMBERS_DICT
from growbonsai._validators import ValueFrom5to300


class Clock(Static):
    DEFAULT_CSS = """
    Clock {
        border: heavy yellow;
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Widgets
        self._h_min = Static('')
        self._t_min = Static('')
        self._u_min = Static(NUMBERS_DICT['0'])
        self._t_sec = Static(NUMBERS_DICT['0'])
        self._u_sec = Static(NUMBERS_DICT['0'])
        self._seed_button = Button('Seed', variant='success', id='seed-bt')

        # Data
        self._clock_mode: str = 'Timer'
        self._stop_watch_started: datetime = datetime.now()
        self._timer_length: int = 0
        self._cancel_timer_counter_default = 3
        self._cancel_timer_counter: int = 0

        # Intervals
        self._intervals = []

    def compose(self):
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
            yield Input(
                value='45',
                placeholder='Type 5 to 300',
                restrict=r'^\d{1,3}$',
                validators=[ValueFrom5to300()],
                id='session-duration'
            )
            yield self._seed_button

    @on(Button.Pressed, '#seed-bt')
    def _start_timer(self) -> None:
        """Start timer or stopwatch depend on the chosen mode"""
        if self._seed_button.variant == 'success':
            self._start_seeding()
        elif self._seed_button.variant == 'warning':
            # Reset Timer
            self._h_min.update('')
            self._t_min.update('')
            self._u_min.update(NUMBERS_DICT['0'])
            self._t_sec.update(NUMBERS_DICT['0'])
            self._u_sec.update(NUMBERS_DICT['0'])
            # Reset Button
            self._seed_button.variant = 'success'
            self._seed_button.label = 'Seed'
            # Stop intervals
            self._stop_intervals()
        else:
            # TODO: Add popup asking to stop
            # TODO: Add record to DB
            pass

    def _stop_intervals(self):
        """Stop all active intervals."""
        for interval in self._intervals:
            interval.stop()
        self._intervals.clear()

    def _start_seeding(self) -> None:
        """Start clock"""
        self._cancel_timer_counter = self._cancel_timer_counter_default
        if self._clock_mode == 'Timer':
            self._timer_length = int(self.query_one(Input).value) * 60
            interval1 = self.set_interval(1, self._timer)
        else:
            self._stop_watch_started = datetime.now()  # Reload time
            interval1 = self.set_interval(1, self._stopwatch)

        self._seed_button.variant = 'warning'
        interval2 = self.set_interval(1, self._start_cancel_timer, repeat=30)
        self._intervals.extend((interval1, interval2))

    def _stopwatch(self) -> None:
        """Update variable used by stopwatch and update displayed time"""
        elapsed_time = datetime.now() - self._stop_watch_started
        minutes, seconds = divmod(elapsed_time.total_seconds(), 60)
        self._update_clock(minutes, seconds)

    def _timer(self) -> None:
        """Update variable used by timer and update displayed time"""
        self._timer_length -= 1
        minutes, seconds = divmod(self._timer_length, 60)
        self._update_clock(minutes, seconds)

    def _update_clock(self, minutes, seconds):
        """Update displayed digits"""
        minutes_str = str(int(minutes)).zfill(2)
        seconds_str = str(int(seconds)).zfill(2)
        print(int(minutes))

        if int(minutes) >= 100:
            self._h_min.update(NUMBERS_DICT[minutes_str[-3]])
        else:
            self._h_min.update('')

        if int(minutes) >= 10:
            self._t_min.update(NUMBERS_DICT[minutes_str[-2]])
        else:
            self._t_min.update('')

        self._u_min.update(NUMBERS_DICT[minutes_str[-1]])
        self._t_sec.update(NUMBERS_DICT[seconds_str[-2]])
        self._u_sec.update(NUMBERS_DICT[seconds_str[-1]])

    def _start_cancel_timer(self):
        """Allow user to cancel timer in first 30 seconds"""
        self._cancel_timer_counter -= 1
        if self._cancel_timer_counter > 0:
            self._seed_button.label = f'Cancel ({self._cancel_timer_counter})'
        else:
            self._seed_button.label = 'Kill'
            self._seed_button.variant = 'error'

    @on(Input.Changed, '#session-duration')
    def _session_duration_changed(self, event: Input.Changed) -> None:
        """If the session duration is not correct block start button."""
        if event.input.is_valid:
            self.query_one('#seed-bt', Button).disabled = False
        else:
            self.query_one('#seed-bt', Button).disabled = True

    def change_clock_mode(self):
        """Change between `timer` and `stopwatch`"""
        if self._clock_mode == 'Timer':
            self._clock_mode = self.app.title = 'Stopwatch'
            self.query_one(Input).remove()
        else:
            self._clock_mode = self.app.title = 'Timer'
            self.mount(
                Input(
                    value='45',
                    placeholder='Type number from 5 to 300',
                    restrict=r'^\d{1,3}$',
                    validators=[ValueFrom5to300()],
                    id='session-duration'
                ),
                before='#seed-bt',
            )

