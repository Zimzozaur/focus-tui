from typing import TYPE_CHECKING, Literal, cast

from textual import on
from textual.app import ComposeResult
from textual.containers import Grid
from textual.widgets import Button, Select

from focustui.constants import (
    MAX_VOLUME_LEVEL,
    MIN_VOLUME_LEVEL,
    LengthType,
    SoundType,
    VolumeType,
)
from focustui.modals import EditSound
from focustui.widgets import SoundVolumeInput

if TYPE_CHECKING:
    from focustui.config_manager import ConfigManager
    from focustui.sound_manager import SoundManager


def create_tooltip(volume_type: SoundType | Literal["test"]) -> str:
    """Return a tooltip string with volume_type interpolated."""
    return (
        f"Type value between {MIN_VOLUME_LEVEL} and {MAX_VOLUME_LEVEL}\nto "
        f"set {volume_type} volume."
    )


class SoundSettings(Grid):
    """SoundSettings allow user to change used sounds,
    test any sound and open EditSound modal.
    """

    def __init__(
        self,
        cm: "ConfigManager",
        sm: "SoundManager",
    ) -> None:
        super().__init__()
        self._cm = cm
        self._sm = sm

    def compose(self) -> ComposeResult:
        yield Select.from_values(
            self._sm.all_shorts_list,
            prompt=f"Alarm:{self._cm.get_sound_name("alarm")}",
            id="alarm",
        )
        yield SoundVolumeInput(
            value=str(self._cm.config.alarm.volume),
            tooltip=create_tooltip("alarm"),
            id="alarm_volume",
        )
        yield Button("Alarms\nSignals", id="short", classes="sound-edit-bt")
        yield Select.from_values(
            self._sm.all_shorts_list,
            prompt=f"Signal:{self._cm.get_sound_name("signal")}",
            id="signal",
        )
        yield SoundVolumeInput(
            value=str(self._cm.config.signal.volume),
            tooltip=create_tooltip("signal"),
            id="signal_volume",
        )
        yield Select.from_values(
            self._sm.all_longs_list,
            prompt=f"Ambient: {self._cm.get_sound_name("ambient")}",
            id="ambient",
        )
        yield SoundVolumeInput(
            value=str(self._cm.config.ambient.volume),
            tooltip=create_tooltip("ambient"),
            id="ambient_volume",
        )
        yield Button("Ambiences", id="long", classes="sound-edit-bt")
        yield Select.from_values(
            self._sm.all_sounds_list,
            prompt="Select to play sound",
            id="test-sound",
        )
        yield SoundVolumeInput(
            value=str(self._cm.config.test_volume),
            tooltip=create_tooltip("test"),
            id="test_volume",
        )
        yield Button(
            "Pause",
            variant="warning",
            id="test-sound-bt",
        )

    @on(Select.Changed)
    def select_changed(self, event: Select.Changed) -> None:
        """Change sound connected to type and update config."""
        # If button's id is 'test-sound' press blank or already chosen return
        if event.select.id == "test-sound" or event.value == Select.BLANK:
            return

        self._cm.update_used_sound(
            sound_type=cast(SoundType, event.select.id),
            name=event.value,
        )
        # Update song's name
        sound_type = event.control.id.capitalize()
        event.select.prompt = f"{sound_type}: {self._cm.config.alarm.name}"

    @on(Button.Pressed, ".sound-edit-bt")
    def open_edit_sound_popup(self, event: Button.Pressed) -> None:
        """Open Sounds Edit menu and refresh page if changes where applied."""
        async def recompose(arg) -> None:  # noqa: ARG001
            """Recompose."""
            await self.recompose()

        self.app.push_screen(
            EditSound(
                cast(LengthType, event.button.id),
                sm=self._sm,
                cm=self._cm,
            ),
            recompose,
        )

    @on(Select.Changed, "#test-sound")
    def test_sound(self, event: Select.Changed) -> None:
        """Play sound selected from list."""
        if event.value == Select.BLANK:
            return

        if event.value in self._sm.all_sounds_list:
            self._sm.play_sound(
                sound_name=event.value,
                sound_volume=self._cm.config.test_volume,
            )
            event.select.prompt = f"Last: {event.value}"
            event.select.clear()
        else:
            msg = "Sound is not in expected folder"
            raise FileNotFoundError(msg)

    @on(Button.Pressed, "#test-sound-bt")
    def stop_playing_sound(self) -> None:
        """Stop playing any sound."""
        self._sm.stop_sound()

    @on(SoundVolumeInput.Changed)
    def new_volume_submitted(self, event: SoundVolumeInput.Submitted) -> None:
        if event.value == "":
            return

        if not MIN_VOLUME_LEVEL <= int(event.value) <= MAX_VOLUME_LEVEL:
            return

        _type = cast(VolumeType, event.input.id)
        value = int(event.input.value)
        self._cm.change_volume_value(_type, value)
