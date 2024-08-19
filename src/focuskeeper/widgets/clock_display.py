from textual.containers import Horizontal
from textual.widgets import Label, Static

from focuskeeper.assets import NUMBERS_DICT


class ClockDisplay(Horizontal):
    """Display time"""

    def __init__(self, *args, **kwargs) -> None:
        # Widgets
        super().__init__(*args, **kwargs)
        self._h_min = Static("", classes="clock-display-digit")
        self._t_min = Static("", classes="clock-display-digit")
        self._u_min = Static(NUMBERS_DICT["0"], classes="clock-display-digit")
        self._t_sec = Static(NUMBERS_DICT["0"], classes="clock-display-digit")
        self._u_sec = Static(NUMBERS_DICT["0"], classes="clock-display-digit")

    def compose(self):
        yield self._h_min
        yield Label(" ")
        yield self._t_min
        yield Label(" ")
        yield self._u_min
        yield Label(" ")
        yield Static(NUMBERS_DICT[":"], classes="clock-display-digit")
        yield Label(" ")
        yield self._t_sec
        yield Label(" ")
        yield self._u_sec

    def update_time(self, minutes: str, seconds: str) -> None:
        """Update clock number"""
        if len(minutes) > 2:
            self._h_min.update(NUMBERS_DICT[minutes[-3]])
        else:
            self._h_min.update("")

        if len(minutes) > 1:
            self._t_min.update(NUMBERS_DICT[minutes[-2]])
        else:
            self._t_min.update("")

        self._u_min.update(NUMBERS_DICT[minutes[-1]])
        self._t_sec.update(NUMBERS_DICT[seconds[-2]])
        self._u_sec.update(NUMBERS_DICT[seconds[-1]])
