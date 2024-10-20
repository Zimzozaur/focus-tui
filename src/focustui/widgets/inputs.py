from typing import TYPE_CHECKING

from textual.widgets import Input

from focustui.constants import (
    MAX_SESSION_LEN,
    MAX_VOLUME_LEVEL,
    MIN_SESSION_LEN,
    MIN_VOLUME_LEVEL,
)
from focustui.utils import hour_min_session_len, int_to_hour_min
from focustui.validators import StopwatchOrTimer, StopwatchOrTimerHour, ValueFrom1to100

if TYPE_CHECKING:
    from focustui.config_manager import ConfigManager


tooltip = (f"Type 0 to set stopwatch or\nbetween {MIN_SESSION_LEN} and "
           f"{MAX_SESSION_LEN} to set timer.")


class HourMinInput(Input):
    def __init__(self, cm: "ConfigManager", *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.value = int_to_hour_min(cm.get_session_length())
        self.placeholder = "0 or 0:00-3:59"
        self.validators = [StopwatchOrTimerHour()]
        self.id = "session-duration"
        self.tooltip = "Type 0 or 0:00-3:59 (e.g., 1:30)"

    @property
    def formated_value(self) -> int:
        return hour_min_session_len(self.value)


class MinInput(Input):
    def __init__(self, cm: "ConfigManager", *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.value = str(cm.get_session_length())
        self.placeholder = f"0 or {MIN_SESSION_LEN}-{MAX_SESSION_LEN}"
        self.restrict = r"^(?:[0-9]|[1-9][0-9]{1,2})$"
        self.validators = [StopwatchOrTimer()]
        self.id = "session-duration"
        self.tooltip = tooltip

    @property
    def formated_value(self) -> int:
        return int(self.value)


class SoundVolumeInput(Input):
    def __init__(
            self, **kwargs,
    ) -> None:
        super().__init__(
            placeholder=f"{MIN_VOLUME_LEVEL} - {MAX_VOLUME_LEVEL}",
            restrict=r"^(100|[1-9][0-9]?|0?[1-9])$",
            validators=[ValueFrom1to100()],
            type="integer",
            **kwargs,
        )
