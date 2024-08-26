from textual.widgets import Input

from focuskeeper.constants import MAX_VOLUME_LEVEL, MIN_VOLUME_LEVEL
from focuskeeper.validators import ValueFrom1to100


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
