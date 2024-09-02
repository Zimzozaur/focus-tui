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
    return (f"Type value between {MIN_VOLUME_LEVEL} and {MAX_VOLUME_LEVEL}\nto "
            f"set {volume_type} volume.")


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
        # Those attributes are set to None and initialized
        # by function to updated them when users applies changes
        self.select_alarm: Select | None = None
        self.select_signal: Select | None = None
        self.select_ambient: Select | None = None
        self.test_sound: Select | None = None
        self.alarm_input: SoundVolumeInput | None = None
        self.signal_input: SoundVolumeInput | None = None
        self.ambient_input: SoundVolumeInput | None = None
        self.test_input: SoundVolumeInput | None = None
        self.initialize_sound_attributes()

    def compose(self) -> ComposeResult:
        yield self.select_alarm
        yield self.alarm_input
        yield Button("Alarms\nSignals", id="short", classes="sound-edit-bt")
        yield self.select_signal
        yield self.signal_input
        yield self.select_ambient
        yield self.ambient_input
        yield Button("Ambiences", id="long", classes="sound-edit-bt")
        yield self.test_sound
        yield self.test_input
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
        # Change prompt value in select menu
        if event.control.id == "alarm":
            self.select_alarm.prompt = f"Alarm: {self._sm.get_used_alarm}"
        elif event.control.id == "signal":
            self.select_alarm.prompt = f"Signal: {self._sm.get_used_signal}"
        else:
            self.select_alarm.prompt = f"Ambient: {self._sm.get_used_ambient}"

    @on(Button.Pressed, ".sound-edit-bt")
    def open_edit_sound_popup(self, event: Button.Pressed) -> None:
        """Open Sounds Edit menu and refresh page if changes where applied."""

        async def reinit_and_recompose_sound_settings(arg) -> None:
            """Restart initialization and recompose."""
            self.initialize_sound_attributes()
            await self.recompose()

        self.app.push_screen(
            EditSound(cast(LengthType, event.button.id), sm=self._sm),
            reinit_and_recompose_sound_settings,
        )

    @on(Select.Changed, "#test-sound")
    def test_sound(self, event: Select.Changed) -> None:
        """Play sound selected from list."""
        if event.value == Select.BLANK:
            return

        if event.value in self._sm.all_sounds_list:
            self._sm.play_sound(event.value, "test")
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

    def initialize_sound_attributes(self) -> None:
        # Set alarm Select
        self.select_alarm = Select.from_values(self._sm.all_shorts_list)
        self.select_alarm.prompt = f"Alarm: {self._sm.get_used_alarm}"
        self.select_alarm.id = "alarm"
        # Set signal Select
        self.select_signal = Select.from_values(self._sm.all_shorts_list)
        self.select_signal.prompt = f"Signal: {self._sm.get_used_signal}"
        self.select_signal.id = "signal"
        # Set ambient Select
        self.select_ambient = Select.from_values(self._sm.all_longs_list)
        self.select_ambient.prompt = f"Ambient: {self._sm.get_used_ambient}"
        self.select_ambient.id = "ambient"
        # Set test sound Select
        self.test_sound = Select.from_values(self._sm.all_sounds_list)
        self.test_sound.prompt = "Select to play sound"
        self.test_sound.id = "test-sound"
        # Set volume
        self.alarm_input = SoundVolumeInput(
            value=str(self._cm.config.alarm.volume),
            tooltip=create_tooltip("alarm"),
            id="alarm_volume",
        )
        self.signal_input = SoundVolumeInput(
            value=str(self._cm.config.signal.volume),
            tooltip=create_tooltip("signal"),
            id="signal_volume",
        )
        self.ambient_input = SoundVolumeInput(
            value=str(self._cm.config.ambient.volume),
            tooltip=create_tooltip("ambient"),
            id="ambient_volume",
        )
        self.test_input = SoundVolumeInput(
            value=str(self._cm.config.test_volume),
            tooltip=create_tooltip("test"),
            id="test_volume",
        )
