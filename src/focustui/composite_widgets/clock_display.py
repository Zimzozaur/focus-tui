from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Label, Static

from focustui.assets import NUMBERS_DICT

if TYPE_CHECKING:
    from focustui.config_manager import ConfigManager


class ClockDisplay(Horizontal):
    """Display time."""

    def __init__(self, cm: "ConfigManager", *args: tuple, **kwargs: dict) -> None:
        super().__init__(*args, **kwargs)
        self._cm = cm

        if self._cm.get_clock_display_hours():
            self._ones_hour = Static(NUMBERS_DICT["0"], classes="clock-digit")
            self._hour_separator = Static(
                NUMBERS_DICT[":"],
                classes="clock-digit",
            )
        else:
            self._ones_hour = Static("", classes="clock-digit")
            self._hour_separator = Static("", classes="clock-digit")

        self._hundreds_min = Static("", classes="clock-digit")
        self._tens_min = Static(NUMBERS_DICT["0"], classes="clock-digit")
        self._ones_min = Static(NUMBERS_DICT["0"], classes="clock-digit")

        if self._cm.get_clock_display_seconds():
            self._sec_separator = Static(NUMBERS_DICT[":"], classes="clock-digit")
            self._tens_sec = Static(NUMBERS_DICT["0"], classes="clock-digit")
            self._ones_sec = Static(NUMBERS_DICT["0"], classes="clock-digit")
        else:
            self._sec_separator = Static("", classes="clock-digit")
            self._tens_sec = Static("", classes="clock-digit")
            self._ones_sec = Static("", classes="clock-digit")

    def compose(self) -> ComposeResult:
        yield self._ones_hour
        yield Label(" ")
        yield self._hour_separator
        yield self._hundreds_min
        yield Label(" ")
        yield self._tens_min
        yield Label(" ")
        yield self._ones_min
        yield Label(" ")
        yield self._sec_separator
        yield Label(" ")
        yield self._tens_sec
        yield Label(" ")
        yield self._ones_sec

    def update_time(self, minutes: str, seconds: str) -> None:
        if self._cm.get_clock_display_hours():
            self.update_hour_mode(minutes)
        else:
            self.update_minute_mode(minutes)

        self._update_seconds(seconds)

    def update_minute_mode(self, minutes: str):
        """Update clock number."""
        hundreds_length: int = 2
        tens_length: int = 1

        self._ones_hour.update("")
        self._hour_separator.update("")

        if len(minutes) > hundreds_length:
            self._hundreds_min.update(NUMBERS_DICT[minutes[-3]])
        else:
            self._hundreds_min.update("")

        if len(minutes) > tens_length:
            self._tens_min.update(NUMBERS_DICT[minutes[-2]])
        else:
            self._tens_min.update("")

        self._ones_min.update(NUMBERS_DICT[minutes[-1]])

    def update_hour_mode(self, minutes: str):
        hours, minutes = divmod(int(minutes), 60)
        minutes = str(minutes)
        tens_length: int = 1

        self._ones_hour.update(NUMBERS_DICT[str(hours)])
        self._hour_separator.update(NUMBERS_DICT[":"])
        self._hundreds_min.update("")

        if len(minutes) > tens_length:
            self._tens_min.update(NUMBERS_DICT[minutes[-2]])
        else:
            self._tens_min.update(NUMBERS_DICT["0"])

        self._ones_min.update(NUMBERS_DICT[minutes[-1]])

    def _update_seconds(self, seconds: str) -> None:
        if self._cm.get_clock_display_seconds():
            self._sec_separator.update(NUMBERS_DICT[":"])
            self._tens_sec.update(NUMBERS_DICT[seconds[0]])
            self._ones_sec.update(NUMBERS_DICT[seconds[1]])
        else:
            self._sec_separator.update("")
            self._tens_sec.update("")
            self._ones_sec.update("")
