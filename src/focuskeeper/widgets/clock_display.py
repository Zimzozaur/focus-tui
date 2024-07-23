from textual.widgets import Static, Label
from textual.containers import Horizontal

from focuskeeper.assets import NUMBERS_DICT


class ClockDisplay(Static):
    DEFAULT_CSS = """
    Clock {
        width: 100%;
        height: auto;
    }

    #clock-wrapper {
        align: center middle;
        height: 60%;
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

    def update_time(self, h_min, t_min, u_min, t_sec, u_sec):
        """Update clock number"""
        if int(h_min) >= 100:
            self._h_min.update(NUMBERS_DICT[h_min])
        else:
            self._h_min.update('')

        if int(t_min) >= 10:
            self._t_min.update(NUMBERS_DICT[t_min])
        else:
            self._t_min.update('')

        self._u_min.update(NUMBERS_DICT[u_min])
        self._t_sec.update(NUMBERS_DICT[t_sec])
        self._u_sec.update(NUMBERS_DICT[u_sec])
