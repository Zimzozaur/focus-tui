from textual.widgets import Input

from focustui.constants import MINUTE


def hour_min_session_len(value: str):
    """Convert a time string in the format 'H:MM' to total minutes."""
    length = value.split(":")
    if len(length) == 1:
        return 0
    return int(length[0]) * MINUTE + int(length[1])


class HourMinInput(Input):
    @property
    def formated_value(self) -> int:
        return hour_min_session_len(self.value)


class MinInput(Input):
    @property
    def formated_value(self) -> int:
        return int(self.value)

