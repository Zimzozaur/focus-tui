from pathlib import Path
from typing import cast, Literal

from textual import on
from textual.app import ComposeResult
from textual.containers import Grid
from textual.widgets import Button, Select

from focuskeeper.db import DatabaseManager
from focuskeeper.config import AppConfig
from focuskeeper.modals import EditSound
from focuskeeper.utils.sound import sounds_list


class SoundSettings(Grid):
    DEFAULT_CSS = """
    SoundSettings {
        grid-size: 2 3;
        grid-columns: 3fr 1fr;
        
    
        height: auto;
        & > * {
            height: auto;
        }
    }
    
    #edit-alarm {
        row-span: 2;
        height: 8;
    }
    
    .sound-edit-bt {
        width: 8;
    }
    
    .sound-settings-horizontal-padding {
        padding-bottom: 1;
    }
    """

    # External classes
    db = DatabaseManager()
    app_config = AppConfig()
    # App paths
    sounds: Path = app_config.sounds
    ambiences: Path = app_config.ambiences
    # User paths
    user_sounds: Path = app_config.user_sounds
    user_ambiences: Path = app_config.user_ambiences

    def __init__(self):
        super().__init__()
        self.set_alarm = None
        self.set_signal = None
        self.set_ambient = None
        self.select_alarm = None
        self.select_signal = None
        self.select_ambient = None
        self.initialize_attributes()

    def initialize_attributes(self):
        self.set_alarm = self.app_config.get_used_sound('alarm')['name']
        self.set_signal = self.app_config.get_used_sound('signal')['name']
        self.set_ambient = self.app_config.get_used_sound('ambient')['name']

        sound_list = sounds_list(self.sounds, self.user_sounds)
        # Set alarm Select
        self.select_alarm = Select.from_values(sound_list)
        self.select_alarm.prompt = f'Alarm: {self.set_alarm}'
        self.select_alarm.id = 'alarm'
        # Set signal Select
        self.select_signal = Select.from_values(sound_list)
        self.select_signal.prompt = f'Signal: {self.set_signal}'
        self.select_signal.id = 'signal'
        # Set ambient Select
        ambiences_list = sounds_list(self.ambiences, self.user_ambiences)
        self.select_ambient = Select.from_values(ambiences_list)
        self.select_ambient.prompt = f'Ambient: {self.set_ambient}'
        self.select_ambient.id = 'ambient'

    def compose(self) -> ComposeResult:
        yield self.select_alarm
        yield Button('Edit Alarms/Signal', id='edit-alarm', classes='sound-edit-bt')
        yield self.select_signal
        yield self.select_ambient
        yield Button('Edit Ambiences', id='edit-ambient', classes='sound-edit-bt')

    @on(Select.Changed)
    def select_changed(self, event: Select.Changed) -> None:
        """Change sound connected to type and update config"""
        # If press blank or already chosen return
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

    @on(Button.Pressed)
    def on_button_pressed(self, event: Button.Pressed):
        """Open Sounds Edit menu and refresh page if changes
        where applied"""

        if event.button.id == 'edit-ambient':
            sound_type: Literal['ambient'] = 'ambient'
            path_to_sounds: Path = self.user_ambiences
        else:
            sound_type: Literal['alarm'] = 'alarm'
            path_to_sounds: Path = self.user_sounds

        self.app.push_screen(
            EditSound(sound_type, path_to_sounds),
            self.reinit_and_recompose_self
        )

    async def reinit_and_recompose_self(self, arg):
        """Restart initialization and recompose"""
        self.initialize_attributes()
        await self.recompose()
