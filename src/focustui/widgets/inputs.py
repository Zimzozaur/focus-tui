from typing import TYPE_CHECKING

from textual.widgets import Input

from focustui.constants import (
    MAX_VOLUME_LEVEL,
    MIN_VOLUME_LEVEL,
)
from focustui.utils import session_len_parser
from focustui.validators import SessionInputValidator, ValueFrom1to100

if TYPE_CHECKING:
    from focustui.config_manager import ConfigManager


tooltip = (
    "Type 0 to set stopwatch\n"
    "Or 5-120 for timer in minutes\n"
    "Examples: 5, 49, 120 (minutes)\n"
    "Or 0:5, 0:49, 2:0 (hours:minutes)"
)


class SessionLenInput(Input):
    """Accept 0 or value in one of the 2 forms:
    1. Minutes form - value between MIN to MAX
    2. Hour form - H:M or H:MM between MIN and MAX.
    """

    def __init__(self, cm: "ConfigManager", *args, **kwargs) -> None:
        super().__init__(
            *args,
            value=cm.get_session_length(),
            id="session-duration",
            tooltip=tooltip,
            restrict="^[0-9:]{1,4}$",
            validators=[SessionInputValidator()],
            **kwargs,
        )

    def to_int(self) -> int:
        return session_len_parser(self.value)


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
