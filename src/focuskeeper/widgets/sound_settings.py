from typing import Literal, cast

from textual import on
from textual.app import ComposeResult
from textual.containers import Grid
from textual.widgets import Button, Select

from focuskeeper.config import ConfigManager
from focuskeeper.modals import EditSound
from focuskeeper.sound_manager import SoundManager


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

    def compose(self) -> ComposeResult:
        yield self._select_alarm
        yield Button("Edit Alarms/Signals", id="short", classes="sound-edit-bt")
        yield self._select_signal
        yield self._select_ambient
        yield Button("Edit Ambiences", id="long", classes="sound-edit-bt")
        yield self._test_sound
        yield Button("Pause", variant="warning", id="test-sound-bt")

    @on(Select.Changed)
    def select_changed(self, event: Select.Changed) -> None:
        """Change sound connected to type and update config."""
        # If button's id is 'test-sound' press blank or already chosen return
        if event.select.id == "test-sound" or event.value == Select.BLANK:
            return

        self._cm.update_used_sound(
            sound_type=cast(Literal["alarm", "signal", "ambient"], event.select.id),
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
            EditSound(cast(Literal["short", "long"], event.button.id)),
            self.reinit_and_recompose_self,
        )

    @on(Select.Changed, "#test-sound")
    def listen_to_sound(self, event: Select.Changed) -> None:
        """Play sound selected from list."""
        if event.value == Select.BLANK:
            return

        if event.value in self._sm.all_sounds_list:
            self._sm.play_sound(event.value)
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
