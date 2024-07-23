from textual.widgets import Static, Label
from textual.containers import Horizontal

from focuskeeper.assets import NUMBERS_DICT


class ClockDisplay(Horizontal):
    DEFAULT_CSS = """
    ClockDisplay {
        width: 100%;
        align: center middle;
    }
    
    Static {
        width: auto;
        color: $warning-lighten-1;
    }
    
    """

    def __init__(self, *args, **kwargs) -> None:
        # Widgets
        super().__init__(*args, **kwargs)
        self._h_min = Static('')
        self._t_min = Static('')
        self._u_min = Static(NUMBERS_DICT['0'])
        self._t_sec = Static(NUMBERS_DICT['0'])
        self._u_sec = Static(NUMBERS_DICT['0'])

    def compose(self):
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

    def update_time(self, minutes: str, seconds: str) -> None:
        """Update clock number"""
        if len(minutes) > 2:
            self._h_min.update(NUMBERS_DICT[minutes[-3]])
        else:
            self._h_min.update('')

        if len(minutes) > 1:
            self._t_min.update(NUMBERS_DICT[minutes[-2]])
        else:
            self._t_min.update('')

        self._u_min.update(NUMBERS_DICT[minutes[-1]])
        self._t_sec.update(NUMBERS_DICT[seconds[-2]])
        self._u_sec.update(NUMBERS_DICT[seconds[-1]])

