from typing import cast

from textual import on
from textual.app import ComposeResult
from textual.containers import Grid
from textual.widgets import Button, Input, Select

from focuskeeper.config import ConfigManager
from focuskeeper.constants import (
    MAX_VOLUME_LEVEL,
    MIN_VOLUME_LEVEL,
    LengthType,
    SoundType,
    VolumeType,
)
from focuskeeper.modals import EditSound
from focuskeeper.sound_manager import SoundManager
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


class SoundSettings(Grid):
    """SoundSettings allow user to change used sounds,
    test any sound and open EditSound modal.
    """

    def __init__(self) -> None:
        super().__init__()
        # External classes
        self._cm = ConfigManager()
        self._sm = SoundManager()

        self._select_alarm = None
        self._select_signal = None
        self._select_ambient = None
        self._test_sound = None
        self._alarm_input = None
        self._signal_input = None
        self._ambient_input = None
        self._test_sound_input = None
        self.initialize_attributes()

    def initialize_attributes(self) -> None:
        # Set alarm Select
        self._select_alarm = Select.from_values(self._sm.all_shorts_list)
        self._select_alarm.prompt = f"Alarm: {self._sm.get_used_alarm}"
        self._select_alarm.id = "alarm"
        # Set signal Select
        self._select_signal = Select.from_values(self._sm.all_shorts_list)
        self._select_signal.prompt = f"Signal: {self._sm.get_used_signal}"
        self._select_signal.id = "signal"
        # Set ambient Select
        self._select_ambient = Select.from_values(self._sm.all_longs_list)
        self._select_ambient.prompt = f"Ambient: {self._sm.get_used_ambient}"
        self._select_ambient.id = "ambient"
        # Set test sound Select
        self._test_sound = Select.from_values(self._sm.all_sounds_list)
        self._test_sound.prompt = "Select to play sound"
        self._test_sound.id = "test-sound"
        # Set volume
        self._alarm_input = SoundVolumeInput(
            value=str(self._cm.config.alarm_volume),
            tooltip="Set alarm volume",
            id="alarm_volume",
        )
        self._signal_input = SoundVolumeInput(
            value=str(self._cm.config.signal_volume),
            tooltip="Set signal volume",
            id="signal_volume",
        )
        self._ambient_input = SoundVolumeInput(
            value=str(self._cm.config.ambient_volume),
            tooltip="Set ambient volume",
            id="ambient_volume",
        )
        self._test_sound_input = SoundVolumeInput(
            value=str(self._cm.config.test_volume),
            tooltip="Set test volume",
            id="test_volume",
        )

    def compose(self) -> ComposeResult:
        yield self._select_alarm
        yield self._alarm_input
        yield Button("Alarms\nSignals", id="short", classes="sound-edit-bt")
        yield self._select_signal
        yield self._signal_input
        yield self._select_ambient
        yield self._ambient_input
        yield Button("Ambiences", id="long", classes="sound-edit-bt")
        yield self._test_sound
        yield self._test_sound_input
        yield Button("Pause", variant="warning", id="test-sound-bt")

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
            self._select_alarm.prompt = f"Alarm: {self._sm.get_used_alarm}"
        elif event.control.id == "signal":
            self._select_signal.prompt = f"Signal: {self._sm.get_used_signal}"
        else:
            self._select_ambient.prompt = f"Ambient: {self._sm.get_used_ambient}"

    @on(Button.Pressed, ".sound-edit-bt")
    def open_edit_sound_popup(self, event: Button.Pressed) -> None:
        """Open Sounds Edit menu and refresh page if changes where applied."""
        self.app.push_screen(
            EditSound(cast(LengthType, event.button.id)),
            self.reinit_and_recompose_self,
        )

    @on(Select.Changed, "#test-sound")
    def listen_to_sound(self, event: Select.Changed) -> None:
        """Play sound selected from list."""
        if event.value == Select.BLANK:
            return

        if event.value in self._sm.all_sounds_list:
            self._sm.play_sound(event.value, "test")
        else:
            msg = "Sound is not in expected folder"
            raise FileNotFoundError(msg)

    @on(Button.Pressed, "#test-sound-bt")
    def stop_playing_sound(self) -> None:
        """Stop playing any sound."""
        self._sm.stop_sound()

    async def reinit_and_recompose_self(self, arg) -> None:
        """Restart initialization and recompose."""
        self.initialize_attributes()
        await self.recompose()

    @on(SoundVolumeInput.Submitted)
    def change_volume_config(self, event: SoundVolumeInput.Submitted) -> None:
        _type = cast(VolumeType, event.input.id)
        value = int(event.input.value)
        self._cm.change_volume_value(_type, value)
        msg = f"Value of {_type.replace('_', ' ')} was changed!"
        self.notify(msg)
