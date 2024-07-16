from pathlib import Path
from typing import cast, Literal

from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Button, Select

from focusseeds.sound_mixer import SoundMixer
from focusseeds.db import DatabaseManager
from focusseeds.config import AppConfig


def load_music_list(*paths: Path):
    """Return list of mp3 files from paths"""
    return [sound.name for path in paths for sound in path.glob('*mp3')]


class SoundSettings(Container):
    DEFAULT_CSS = """
    SoundSettings {
        height: auto;
        & > * {
            height: auto;
        }
    }
    .sound-settings-horizontal-padding {
        padding-bottom: 1;
    }
    """

    # External classes
    db = DatabaseManager()
    mixer = SoundMixer()
    app_config = AppConfig()
    # App paths
    sounds: Path = app_config.sounds
    ambiences: Path = app_config.ambiences
    # User paths
    user_sounds: Path = app_config.user_sounds
    user_ambiences: Path = app_config.user_ambiences

    def __init__(self):
        super().__init__()
        self.set_alarm = self.app_config.get_used_sound('alarm')['name']
        self.set_signal = self.app_config.get_used_sound('signal')['name']
        self.set_ambient = self.app_config.get_used_sound('ambient')['name']

        sound_list = load_music_list(self.sounds, self.user_sounds)
        # Set alarm Select
        self.select_alarm = Select.from_values(sound_list)
        self.select_alarm.prompt = f'Alarm: {self.set_alarm}'
        self.select_alarm.id = 'alarm'
        # Set signal Select
        self.select_signal = Select.from_values(sound_list)
        self.select_signal.prompt = f'Signal: {self.set_signal}'
        self.select_signal.id = 'signal'
        # Set ambient Select
        ambiences_list = load_music_list(self.ambiences, self.user_ambiences)
        self.select_ambient = Select.from_values(ambiences_list)
        self.select_ambient.prompt = f'Ambient: {self.set_ambient}'
        self.select_ambient.id = 'ambient'

    @on(Select.Changed)
    def select_changed(self, event: Select.Changed) -> None:
        """
        Change assigned sound to sound type when other than saved in db
        """
        if (event.value == Select.BLANK or
                event.control.id in [self.set_alarm, self.set_signal, self.set_ambient]):
            return None

        if event.control.id == 'ambient':
            songs_list = [path.name for path in self.ambiences.glob('*')]
            file_path = self.ambiences if event.value in songs_list else self.user_sounds
        else:
            songs_list = [path.name for path in self.sounds.glob('*')]
            file_path = self.sounds if event.value in songs_list else self.user_sounds

        self.app_config.update_used_sound(
            sound_type=cast(Literal['alarm', 'signal', 'ambient'], event.control.id),
            name=event.value,
            path=str(file_path)
        )

        if event.control.id == 'alarm':
            self.set_alarm = event.value
            self.select_alarm.prompt = f'Alarm: {self.set_alarm}'
        elif event.control.id == 'signal':
            self.set_signal = event.value
            self.select_signal.prompt = f'Signal: {self.set_signal}'
        else:
            self.set_ambient = event.value
            self.select_ambient.prompt = f'Ambient: {self.set_ambient}'

    def compose(self) -> ComposeResult:
        with Horizontal(classes='sound-settings-horizontal-padding'):
            yield self.select_alarm
            yield Button('Edit Alarms')
        with Horizontal(classes='sound-settings-horizontal-padding'):
            yield self.select_signal
            yield Button('Edit Signals')
        with Horizontal():
            yield self.select_ambient
            yield Button('Edit Ambiences')

