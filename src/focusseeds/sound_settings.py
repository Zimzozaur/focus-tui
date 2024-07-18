from pathlib import Path
from typing import cast, Literal, Callable
import platform
import os
import shutil

from textual import on
from textual.app import ComposeResult
from textual.containers import Grid, Horizontal, Center, VerticalScroll
from textual.events import Click
from textual.widgets import Button, Select, DirectoryTree, Collapsible, Input, Static, Footer
from textual.screen import ModalScreen

from focusseeds.sound_mixer import SoundMixer
from focusseeds.db import DatabaseManager
from focusseeds.config import AppConfig, AppPaths
from focusseeds.widgets.accordion import Accordion


def sounds_list(*paths: Path):
    """Return list of audio files supported by Pygame from paths"""
    return [sound.name for path in paths for sound in path.glob('*')
            if sound.suffix in {'.wav', '.mp3', '.ogg', '.flac', '.opus'}]


def remove_id_suffix(string: str) -> str:
    """Remove _something from the end of the string"""
    return string[:string.rindex('_')]


def rename_file(old_path: Path, old_name: str, new_name: str) -> None:
    """Rename a file located at `old_path` with the given `old_name` to `new_name`."""
    old_file_path = old_path / old_name
    new_file_path = old_path / new_name
    old_file_path.rename(new_file_path)


def get_users_folder() -> str:
    """Return name of users folder"""
    users_system = platform.system()

    if users_system == 'Linux':
        return '/home'
    elif users_system == 'Windows':
        return os.path.expandvars("%SystemDrive%\\Users")
    elif users_system == 'Darwin':
        return '/Users'
    else:
        raise NotImplementedError("Functionality not implemented for this operating system.")


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


class EditSound(ModalScreen):
    DEFAULT_CSS = """
    EditSound {
        align: center middle;
        width: auto;
        height: auto;
    }

    #edit-sound-body {
        min-width: 50;
        max-width: 70;
        height: 30;
        padding: 1 2;
        background: $panel;
    }

    #sounds-accordion {
        min-width: 50;
        max-width: 70;
        height: auto;
    }

    .sound-buttons-wrapper {
        height: auto;
        padding: 1 1 0 1;
        width: 100%;
    }
    
    #add-sound-wrapper {
        height: auto;
    }

    .sound-buttons-divider {
        width: 1fr;
    }
    
    #add-sound-divider {
        height: 1fr
    }
    """
    BINDINGS = [
        ('ctrl+q', 'quit_app', 'Quit App'),
        ('escape', 'close_popup', 'Close Popup')
    ]

    def action_quit_app(self):
        self.app.exit()

    def __init__(
            self,
            sound_type: Literal['alarm', 'ambient'],
            path_to_sounds: Path,
            *args, **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self.config = AppConfig()
        self.sound_type = sound_type
        self.path_to_sounds = path_to_sounds
        self.sounds_names: dict[str, str] = {sound.split('.')[0]: f'.{sound.split('.')[1]}'
                                             for sound in sounds_list(path_to_sounds)}

    def action_close_popup(self):
        self.dismiss(True)

    def on_click(self, event: Click):
        """Close popup when clicked on the background
        and user is not editing
        Return [self.edited] to give information to call back
        """
        is_background = self.get_widget_at(event.screen_x, event.screen_y)[0] is self
        if is_background:
            self.dismiss(True)

    def compose(self) -> ComposeResult:
        with VerticalScroll(id='edit-sound-body'):
            with Accordion(id='sounds-accordion'):
                for name in self.sounds_names.keys():
                    with Collapsible(title=name, classes='sound-collapsible', id=f'{name}_coll'):
                        yield Input(value=name, id=f"{name}_input", restrict=r'^[a-zA-Z0-9_-]+$')
                        with Horizontal(classes='sound-buttons-wrapper'):
                            yield Button('Rename', variant='success',
                                         disabled=True, id=f"{name}_rename", classes='sound-rename-bt')
                            yield Static(classes='sound-buttons-divider')
                            yield Button('Remove', variant='error',
                                         id=f"{name}_remove", classes='sound-remove-bt')

            yield Static(id='add-sound-divider')
            with Center(id='add-sound-wrapper'):
                yield Button(
                    f"Add {'Sound' if self.sound_type != 'ambient' else 'Ambient'}",
                    variant='primary', id='add-sound-bt'
                )

    @on(Input.Changed)
    def check_sound_name(self, event: Input.Changed):
        """Check is new sound name correct"""
        query = f"#{remove_id_suffix(event.input.id)}_rename"
        self.query_one(query).disabled = event.input.value in self.sounds_names

    @on(Button.Pressed, '.sound-rename-bt')
    async def change_sound_name(self, event: Button.Pressed):
        """Change name of a sound and update DOM and dist"""
        # Change name
        sound_name = remove_id_suffix(event.button.id)
        extension = self.sounds_names[sound_name]
        old_name = sound_name + extension
        new_name = self.query_one(f'#{sound_name}_input', Input).value
        new_name_with_extension = new_name + extension
        rename_file(self.path_to_sounds, old_name, new_name_with_extension)
        # Update DOM and dict
        del self.sounds_names[sound_name]
        self.sounds_names[new_name] = extension
        self.config.change_sound_name_if_in_config(self.sound_type, old_name, new_name_with_extension)
        await self.recompose()
        if self.sound_type == 'ambient':
            self.notify('Changed name of an ambient')
        else:
            self.notify('Changed name of a sound')
        self.query_one(f'#{new_name}_coll', Collapsible).collapsed = False

    @on(Button.Pressed, '.sound-remove-bt')
    async def remove_sound(self, event: Button.Pressed):
        """Display confirmation screen
        if users accepts sound is removed from library
        """
        sound_name = remove_id_suffix(event.button.id)
        sound_to_remove = sound_name + self.sounds_names[sound_name]

        # if removed sound that is already used
        if self.config.is_sound_in_config(self.sound_type, sound_to_remove):
            if self.sound_type == 'ambient':
                self.config.change_sound_to_default(self.sound_type, sound_to_remove)
            else:
                self.config.change_sound_to_default(self.sound_type, sound_to_remove)

        # Remove sound
        (self.path_to_sounds / sound_to_remove).unlink()
        await self.recompose_(None)

    async def recompose_(self, arg):
        """Refresh and recompose screen"""
        self.sounds_names: dict[str, str] = {
            sound.split('.')[0]: f'.{sound.split('.')[1]}'
            for sound in sounds_list(self.path_to_sounds)
        }
        await self.recompose()

    @on(Button.Pressed, '#add-sound-bt')
    def open_music_directory_tree(self):
        self.app.push_screen(AddSoundTree(self.sound_type), self.recompose_)


class MusicDirectoryTree(DirectoryTree):
    show_root = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def filter_paths(self, paths):
        def not_hidden(path: Path) -> bool:
            return path.is_dir() and not path.name.startswith(".")
        suffixes = {".wav", ".mp3", ".ogg", ".flac", ".opus", '/'}
        return [path for path in paths if not_hidden(path) or path.suffix in suffixes]


class AddSoundTree(ModalScreen):
    DEFAULT_CSS = """
    AddSoundTree {
        align: center middle;
        width: auto;
        height: auto;
    }

    MusicDirectoryTree {
        width: 60%;
        height: 60%;
        padding: 1 2;
        background: $panel;
    }

    """
    BINDINGS = [
        ('ctrl+q', 'quit_app', 'Quit App'),
        ('escape', 'close_popup', 'Close Popup')
    ]

    def action_quit_app(self):
        self.app.exit()

    def action_close_popup(self):
        self.dismiss(True)

    def on_click(self, event: Click):
        """Close popup when clicked on the background
        and user is not editing
        Return [self.edited] to give information to call back
        """
        is_background = self.get_widget_at(event.screen_x, event.screen_y)[0] is self
        if is_background:
            self.dismiss(True)

    def __init__(self, sound_type, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sound_type = sound_type
        self.paths = AppPaths()

    def compose(self) -> ComposeResult:
        yield MusicDirectoryTree(get_users_folder())

    @on(MusicDirectoryTree.FileSelected)
    def file_selected(self, event: MusicDirectoryTree.FileSelected) -> None:
        """Add sounds to chosen folder type"""
        soundified_name = f'{soundify(event.path)}{event.path.suffix}'
        if is_imported_sound(soundified_name, self.sound_type):
            self.notify('Sound already imported', severity='warning')
            return None

        if self.sound_type == 'ambient':
            path = self.paths.user_ambiences
        else:
            path = self.paths.user_sounds

        shutil.copy(event.path, path / soundified_name)
        self.notify(f'Imported: {soundified_name}')


def is_imported_sound(sound: str, sound_type: Literal['alarm', 'ambient']) -> bool:
    """Rerun is file already in users absences or sounds folder"""
    paths = AppPaths()
    if sound_type == 'alarm':
        return sound in sounds_list(paths.user_sounds)
    else:
        return sound in sounds_list(paths.user_ambiences)


def soundify(sound: Path):
    """Remove all characters that are not a letter, number, - or _"""

    file_name = sound.name.rsplit('.')[0]
    return ''.join(map(lambda l: l if l.isalnum() or l in '_-' else '_', file_name))
