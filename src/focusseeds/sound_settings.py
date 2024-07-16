from pathlib import Path

from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Middle
from textual.widgets import Label, Button, Input, Select

from focusseeds.setup import AppSetup


def load_music_list(*paths: Path):
    """Return list of mp3 files from paths"""
    return [sound.name for path in paths for sound in path.glob('*mp3')]


class SoundSettings(Container):
    DEFAULT_CSS = """
    SoundSettings {
        height: auto;
        & > * {
            border: round green;
            height: auto;
            & > Middle {
                height: 3;
            }
        }
    }
    .sound-settings-button {
        
    }
    """
    """
    Sound settings should:
        - list all effect from app_data and users_data
        - update records when user add new, remove or rename
        - add, remove, rename song
        - change songs
    """
    app_setup = AppSetup()
    # App paths
    sounds: Path = app_setup.sounds
    ambiences: Path = app_setup.ambiences
    # User paths
    user_sounds: Path = app_setup.user_sounds
    user_ambiences: Path = app_setup.user_ambiences

    def __init__(self):
        super().__init__()
        sound_list = load_music_list(self.sounds, self.user_sounds)
        self.select_alarm = Select.from_values(sound_list)
        self.select_signal = Select.from_values(sound_list)
        ambiences_list = load_music_list(self.ambiences, self.user_ambiences)
        self.select_ambient = Select.from_values(ambiences_list)

    @on(Select.Changed)
    def select_changed(self, event: Select.Changed) -> None:
        self.app.title = str(event.value)

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Label('Alarm')
            yield self.select_alarm
            yield Button('Edit')
        with Horizontal():
            yield Label('Signal')
            yield self.select_signal
            yield Button('Edit')
        with Horizontal():
            yield Label('Ambient')
            yield self.select_ambient
            yield Button('Edit')


