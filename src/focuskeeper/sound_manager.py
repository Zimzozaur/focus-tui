import shutil
from pathlib import Path
from typing import Literal
from collections import ChainMap

import pygame

from focuskeeper.app_paths import AppPaths
from focuskeeper.config import AppConfig


class Sound:
    """Class that represent sound file"""

    def __init__(
            self,
            path: Path,
            sound_type: Literal['short', 'long'],
            is_default: bool
    ) -> None:
        self.path: Path = path
        self.parent: Path = path.parent
        self.sound_type: Literal['short', 'long'] = sound_type
        self.full_name = path.name
        self.name: str = path.name.split('.')[0]
        self.extension: str = path.suffix
        self.is_default: bool = is_default

    def __repr__(self) -> str:
        return f"Sound({self.path}, '{self.sound_type}', {self.is_default})"

    def __gt__(self, other):
        if not isinstance(other, Sound):
            raise NotImplemented
        return self.name > other.name

    def __lt__(self, other):
        if not isinstance(other, Sound):
            raise NotImplemented
        return self.name < other.name


def create_sounds_dict(path: Path, sound_type: Literal['short', 'long'], is_default: bool) -> dict[str, Sound]:
    """Return dict of Sounds names and Sounds object mapped to them"""

    allowed_suffixes = {'.wav', '.mp3', '.ogg', '.flac', '.opus'}

    return {
        sound.name.split('.')[0]: Sound(sound, sound_type, is_default)
        for sound in path.glob('*')
        if sound.suffix in allowed_suffixes
    }


class SoundManager:
    """Class used to work with sounds in app
    Allow to perform CRUD on Shorts, Longs and play them

    """
    # Imported classes
    config = AppConfig()

    # Dicts containing all songs found at start up
    _shorts_dict = create_sounds_dict(AppPaths.sounds_path, 'short', True)
    _user_shorts_dict = create_sounds_dict(AppPaths.user_sounds_path, 'short', False)
    _longs_dict = create_sounds_dict(AppPaths.ambiences_path, 'long', True)
    _user_longs_dict = create_sounds_dict(AppPaths.user_ambiences_path, 'long', False)

    # Never change them, those maps are used to check existence or list - GET ONLY
    _all_shorts_dict = ChainMap(_shorts_dict, _user_shorts_dict)
    _all_longs_dict = ChainMap(_longs_dict, _user_longs_dict)
    _all_shorts_longs_dict = ChainMap(_all_shorts_dict, _all_longs_dict)

    @property
    def shorts_list(self) -> list[str]:
        return sorted(self._shorts_dict.keys())

    @property
    def user_shorts_list(self) -> list[str]:
        return sorted(self._user_shorts_dict.keys())

    @property
    def longs_list(self) -> list[str]:
        return sorted(self._longs_dict.keys())

    @property
    def user_longs_list(self) -> list[str]:
        return sorted(self._user_longs_dict.keys())

    @property
    def all_shorts_list(self) -> list[str]:
        return sorted(self._all_shorts_dict.keys())

    @property
    def all_longs_list(self) -> list[str]:
        return sorted(self._all_longs_dict.keys())

    @property
    def all_shorts_longs_list(self) -> list[str]:
        return sorted(self._all_shorts_longs_dict)

    # TODO: it has to be cached

    @property
    def get_used_alarm(self) -> str:
        return self.config.get_used_sound('alarm')

    @property
    def get_used_signal(self) -> str:
        return self.config.get_used_sound('signal')

    @property
    def get_used_ambient(self) -> str:
        return self.config.get_used_sound('ambient')

    def get_any_sound(self, name: str) -> Sound:
        """Get Sound object by passing name of it"""
        return self._all_shorts_longs_dict[name]

    def exists_in_all_dicts(self, name: str) -> bool:
        """Check if the key exists in _all_shorts_longs_dict."""
        return bool(self._all_shorts_longs_dict.get(name, False))

    def rename_sound(self, old_name: str, new_name: str) -> None:
        """Rename sound on users drive and remove old sound from
        corresponding dict and create new instance of Sound class
        if sound was used in config rename it
        """
        # Rename on drive
        sound: Sound = self.get_any_sound(old_name)
        old_file_path = sound.path
        new_file_path = sound.parent / (new_name + sound.extension)
        old_file_path.rename(new_file_path)

        # Update dict
        if sound.sound_type == 'short':
            del self._user_shorts_dict[sound.name]
            self._user_shorts_dict[new_name] = Sound(new_file_path, 'short', False)
        else:
            del self._user_longs_dict[sound.name]
            self._user_longs_dict[new_name] = Sound(new_file_path, 'long', False)

        # Update config if needed
        self.config.update_sound_name(old_name, new_name)

    def add_sound(self, path: Path, name: str, extension: str, sound_type: Literal['short', 'long']) -> None:
        """Add sound to right folder, create instance of Sound and to dict"""
        if sound_type == 'short':
            new_path = self.config.user_sounds_path
            dict_ = self._user_shorts_dict
        else:
            new_path = self.config.user_ambiences_path
            dict_ = self._user_longs_dict

        sound = Sound(
            new_path / (name + extension), sound_type, False
        )

        dict_[name] = sound
        shutil.copy(path, sound.path)

    def remove_sound(self, name: str, sound_type: Literal['short', 'long']) -> None:
        """Remove sound from users drive and update config if needed."""
        if self.config.is_sound_in_config(name):
            self.config.update_sound_name(name)
        # Remove from drive
        self._all_shorts_longs_dict[name].path.unlink()
        # Remove form dict
        if sound_type == 'short':
            del self._user_shorts_dict[name]
        else:
            del self._user_longs_dict[name]

    def sound_name_exist(self, name: str) -> bool:
        """Check if the sound is already imported."""
        return bool(self._all_shorts_longs_dict.get(name, False))

    def play_sound(self, name: str) -> None:
        """Play chosen sound"""
        pygame.mixer.music.load(self.get_any_sound(name).path)
        pygame.mixer.music.play()

    def play_alarm(self):
        """Play alarm sounds"""
        self.play_sound(self.get_used_alarm)

    @staticmethod
    def stop_sound() -> None:
        """Stop all sounds"""
        pygame.mixer.music.stop()



