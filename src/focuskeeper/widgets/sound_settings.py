from typing import Literal, cast

from textual import on
from textual.app import ComposeResult
from textual.containers import Grid
from textual.widgets import Button, Select

from focuskeeper.config import update_used_sound
from focuskeeper.db import DatabaseManager
from focuskeeper.modals import EditSound
from focuskeeper.sound_manager import SoundManager


class SoundSettings(Grid):
    """SoundSettings allow user to change used sounds,
    test any sound and open EditSound modal.
    """

    def __init__(self) -> None:
        super().__init__()
        # External classes
        self.db = DatabaseManager()
        self.sm = SoundManager()

        self.select_alarm = None
        self.select_signal = None
        self.select_ambient = None
        self.test_sound = None
        self.initialize_attributes()

    def initialize_attributes(self) -> None:
        # Set alarm Select
        self.select_alarm = Select.from_values(self.sm.all_shorts_list)
        self.select_alarm.prompt = f"Alarm: {self.sm.get_used_alarm}"
        self.select_alarm.id = "alarm"
        # Set signal Select
        self.select_signal = Select.from_values(self.sm.all_shorts_list)
        self.select_signal.prompt = f"Signal: {self.sm.get_used_signal}"
        self.select_signal.id = "signal"
        # Set ambient Select
        self.select_ambient = Select.from_values(self.sm.all_longs_list)
        self.select_ambient.prompt = f"Ambient: {self.sm.get_used_ambient}"
        self.select_ambient.id = "ambient"
        # Set test sound Select
        self.test_sound = Select.from_values(self.sm.all_sounds_list)
        self.test_sound.prompt = "Select to play sound"
        self.test_sound.id = "test-sound"

    def compose(self) -> ComposeResult:
        yield self.select_alarm
        yield Button("Edit Alarms/Signals", id="short", classes="sound-edit-bt")
        yield self.select_signal
        yield self.select_ambient
        yield Button("Edit Ambiences", id="long", classes="sound-edit-bt")
        yield self.test_sound
        yield Button("Pause", variant="warning", id="test-sound-bt")

    @on(Select.Changed)
    def select_changed(self, event: Select.Changed) -> None:
        """Change sound connected to type and update config."""
        # If #test-sound, press blank or already chosen return
        if event.select.id == "test-sound" or event.value == Select.BLANK:
            return

        update_used_sound(
            sound_type=cast(Literal["alarm", "signal", "ambient"], event.select.id),
            name=event.value,
        )
        # Change prompt value in select menu
        if event.control.id == "alarm":
            self.select_alarm.prompt = f"Alarm: {self.sm.get_used_alarm}"
        elif event.control.id == "signal":
            self.select_signal.prompt = f"Signal: {self.sm.get_used_signal}"
        else:
            self.select_ambient.prompt = f"Ambient: {self.sm.get_used_ambient}"

    @on(Button.Pressed, ".sound-edit-bt")
    def open_edit_sound_popup(self, event: Button.Pressed) -> None:
        """Open Sounds Edit menu and refresh page if changes
        where applied.
        """
        self.app.push_screen(
            EditSound(cast(Literal["short", "long"], event.button.id)),
            self.reinit_and_recompose_self,
        )

    @on(Select.Changed, "#test-sound")
    def listen_to_sound(self, event: Select.Changed) -> None:
        """Play sound selected from list."""
        if event.value == Select.BLANK:
            return

        if event.value in self.sm.all_sounds_list:
            self.sm.play_sound(event.value)
        else:
            msg = "Sound is not in expected folder"
            raise FileNotFoundError(msg)

    @on(Button.Pressed, "#test-sound-bt")
    def stop_playing_sound(self) -> None:
        """Stop playing any sound."""
        self.sm.stop_sound()

    async def reinit_and_recompose_self(self, arg) -> None:
        """Restart initialization and recompose."""
        self.initialize_attributes()
        await self.recompose()
