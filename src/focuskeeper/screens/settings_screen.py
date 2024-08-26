from typing import cast, Literal

from textual import on
from textual.app import ComposeResult
from textual.containers import Container, VerticalScroll, Grid
from textual.widgets import Button, Footer, Static, Select

from focuskeeper.constants import SoundType, LengthType, VolumeType, MIN_VOLUME_LEVEL, MAX_VOLUME_LEVEL
from focuskeeper.modals import EditSound
from focuskeeper.widgets import AboutSettings, AppHeader, SoundVolumeInput
from focuskeeper.screens import BaseScreen


def create_tooltip(volume_type: SoundType | Literal["test"]) -> str:
    """Return a tooltip string with volume_type interpolated."""
    return (f"Type value between {MIN_VOLUME_LEVEL} and {MAX_VOLUME_LEVEL}\nto "
            f"set {volume_type} volume.\nPress enter to save.")


class SettingsScreen(BaseScreen):
    TITLE = "Settings"
    BINDINGS = [
        ("ctrl+q", "quit_app", "Quit App"),
        ("escape", "close_settings", "Close Settings"),
    ]

    def action_quit_app(self) -> None:
        self.app.exit()

    def action_close_settings(self) -> None:
        """Return anything to run callback."""
        self.dismiss()

    def __init__(self) -> None:
        super().__init__()
        self.account_settings_border = Static(classes="settings-section")
        self.account_settings_border.border_title = "Account"

        self.social_settings_border = Static(classes="settings-section")
        self.social_settings_border.border_title = "Social"

        self.sound_settings_border = Static(classes="settings-section")
        self.sound_settings_border.border_title = "Sound"

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
        self.sound_grid = Grid(id="sound-settings-grid")

        self.theme_settings_border = Static(classes="settings-section")
        self.theme_settings_border.border_title = "Theme"

        self.theme_store_settings_border = Static(classes="settings-section")
        self.theme_store_settings_border.border_title = "Theme Store"

        self.about = Static(classes="settings-section")
        self.about.border_title = "About"

    def compose(self) -> ComposeResult:
        self.app.title = "Settings"
        yield AppHeader()
        with VerticalScroll(id="settings-wrapper"):
            with Container(id="settings-body"):
                with self.account_settings_border:
                    yield Button("PLACEHOLDER")
                with self.social_settings_border:
                    yield Button("PLACEHOLDER")
                with self.sound_settings_border:
                    with self.sound_grid:
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
                            id="test-sound-bt"
                        )
                with self.theme_settings_border:
                    yield Button("PLACEHOLDER")
                with self.theme_store_settings_border:
                    yield Button("PLACEHOLDER")
                with self.about:
                    yield AboutSettings()
        yield Footer()

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
            await self.screen.recompose()

        self.app.push_screen(
            EditSound(cast(LengthType, event.button.id)),
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

    @on(SoundVolumeInput.Submitted)
    def new_volume_submitted(self, event: SoundVolumeInput.Submitted) -> None:
        _type = cast(VolumeType, event.input.id)
        value = int(event.input.value)
        self._cm.change_volume_value(_type, value)
        msg = f"Value of {_type.replace('_', ' ')} was changed!"
        self.notify(msg)

    def initialize_sound_attributes(self) -> None:
        # Set alarm Select
        self.screen.select_alarm = Select.from_values(self._sm.all_shorts_list)
        self.screen.select_alarm.prompt = f"Alarm: {self._sm.get_used_alarm}"
        self.screen.select_alarm.id = "alarm"
        # Set signal Select
        self.screen.select_signal = Select.from_values(self._sm.all_shorts_list)
        self.screen.select_signal.prompt = f"Signal: {self._sm.get_used_signal}"
        self.screen.select_signal.id = "signal"
        # Set ambient Select
        self.screen.select_ambient = Select.from_values(self._sm.all_longs_list)
        self.screen.select_ambient.prompt = f"Ambient: {self._sm.get_used_ambient}"
        self.screen.select_ambient.id = "ambient"
        # Set test sound Select
        self.screen.test_sound = Select.from_values(self._sm.all_sounds_list)
        self.screen.test_sound.prompt = "Select to play sound"
        self.screen.test_sound.id = "test-sound"
        # Set volume
        self.screen.alarm_input = SoundVolumeInput(
            value=str(self._cm.config.alarm_volume),
            tooltip=create_tooltip("alarm"),
            id="alarm_volume",
        )
        self.screen.signal_input = SoundVolumeInput(
            value=str(self._cm.config.signal_volume),
            tooltip=create_tooltip("signal"),
            id="signal_volume",
        )
        self.screen.ambient_input = SoundVolumeInput(
            value=str(self._cm.config.ambient_volume),
            tooltip=create_tooltip("ambient"),
            id="ambient_volume",
        )
        self.screen.test_input = SoundVolumeInput(
            value=str(self._cm.config.test_volume),
            tooltip=create_tooltip("test"),
            id="test_volume",
        )
