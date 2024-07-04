from datetime import datetime
from textual import on
from textual.widgets import Button, Static, Label, Input
from textual.containers import Horizontal, Container, Center, Middle

from _numbers import NUMBERS_DICT
from growbonsai._validators import ValueFrom5to300


class Clock(Static):
    DEFAULT_CSS = """
    Clock {
        border: heavy yellow;
        align: center middle;
        width: 100%;
        height: 100%;
    }
    
    Static {
        width: auto;
        color: $warning-lighten-1;
    }
    
    #session-duration {
        width: 20;
    }
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Widgets
        self.h_min = Static('')
        self.t_min = Static('')
        self.u_min = Static(NUMBERS_DICT['0'])
        self.t_sec = Static(NUMBERS_DICT['0'])
        self.u_sec = Static(NUMBERS_DICT['0'])
        self.seed_button = Button('Seed', variant='success', id='seed-bt')

        # Data
        self.clock_mode: str = 'Timer'
        self.stop_watch_started: datetime = datetime.now()
        self.timer_length: int = 0
        self._cancel_timer_counter_default = 3
        self.cancel_timer_counter: int = 0

        # Intervals
        self.intervals = []

    def compose(self):
        with Horizontal(id='clock-wrapper'):
            yield self.h_min
            yield Label(' ')
            yield self.t_min
            yield Label(' ')
            yield self.u_min
            yield Label(' ')
            yield Static(NUMBERS_DICT[':'])
            yield Label(' ')
            yield self.t_sec
            yield Label(' ')
            yield self.u_sec
        yield Input(
            value='45',
            placeholder='Type number from 5 to 300',
            restrict=r'^\d{1,3}$',
            validators=[ValueFrom5to300()],
            id='session-duration'
        )
        yield self.seed_button

    @on(Button.Pressed, '#seed-bt')
    def start_timer(self) -> None:
        """Start timer or stopwatch depend on the chosen mode"""
        if self.seed_button.variant == 'success':
            self.start_seeding()
        elif self.seed_button.variant == 'warning':
            # Reset Timer
            self.h_min.update('')
            self.t_min.update('')
            self.u_min.update(NUMBERS_DICT['0'])
            self.t_sec.update(NUMBERS_DICT['0'])
            self.u_sec.update(NUMBERS_DICT['0'])
            # Reset Button
            self.seed_button.variant = 'success'
            self.seed_button.label = 'Seed'
            # Stop intervals
            self.stop_intervals()
        else:
            pass

    def stop_intervals(self):
        """Stop all active intervals."""
        for interval in self.intervals:
            interval.stop()
        self.intervals.clear()

    def start_seeding(self) -> None:
        """Start clock"""
        self.cancel_timer_counter = self._cancel_timer_counter_default
        if self.clock_mode == 'Timer':
            self.timer_length = int(self.query_one(Input).value) * 60
            interval1 = self.set_interval(1, self.timer)
        else:
            self.stop_watch_started = datetime.now()  # Reload time
            interval1 = self.set_interval(1, self.stopwatch)

        self.seed_button.variant = 'warning'
        interval2 = self.set_interval(1, self.start_cancel_timer, repeat=30)
        self.intervals.extend((interval1, interval2))

    def stopwatch(self) -> None:
        """Update variable used by stopwatch and update displayed time"""
        elapsed_time = datetime.now() - self.stop_watch_started
        minutes, seconds = divmod(elapsed_time.total_seconds(), 60)
        self.update_clock(minutes, seconds)

    def timer(self) -> None:
        """Update variable used by timer and update displayed time"""
        self.timer_length -= 1
        minutes, seconds = divmod(self.timer_length, 60)
        self.update_clock(minutes, seconds)

    def update_clock(self, minutes, seconds):
        """Update displayed digits"""
        minutes_str = str(int(minutes)).zfill(2)
        seconds_str = str(int(seconds)).zfill(2)
        print(f"{minutes_str}:{seconds_str}")

        if int(minutes) >= 100:
            self.h_min.update(NUMBERS_DICT[minutes_str[-3]])
        else:
            self.h_min.update('')

        if int(minutes) >= 10:
            self.h_min.update(NUMBERS_DICT[minutes_str[-2]])
        else:
            self.h_min.update('')

        self.u_min.update(NUMBERS_DICT[minutes_str[-1]])
        self.t_sec.update(NUMBERS_DICT[seconds_str[-2]])
        self.u_sec.update(NUMBERS_DICT[seconds_str[-1]])

    def start_cancel_timer(self):
        """Allow user to cancel timer in first 30 seconds"""
        self.cancel_timer_counter -= 1
        if self.cancel_timer_counter > 0:
            self.seed_button.label = f'Cancel ({self.cancel_timer_counter})'
        else:
            self.seed_button.label = 'Kill'
            self.seed_button.variant = 'error'

    @on(Input.Changed, '#session-duration')
    def session_duration_changed(self, event: Input.Changed) -> None:
        """If the session duration is not correct block start button."""
        if event.input.is_valid:
            self.query_one('#seed-bt', Button).disabled = False
        else:
            self.query_one('#seed-bt', Button).disabled = True

    def change_clock_mode(self):
        """Change between `timer` and `stopwatch`"""
        if self.clock_mode == 'Timer':
            self.clock_mode = self.app.title = 'Stopwatch'
            self.query_one(Input).remove()
        else:
            self.clock_mode = self.app.title = 'Timer'
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

