import shutil
from collections import ChainMap
from pathlib import Path

import pygame

from focustui.constants import (
    LONGS_PATH,
    RESERVED_ALL_SOUNDS,
    SHORTS_PATH,
    LengthType,
)


class Sound:
    """Class that represent sound file."""

    def __init__(self, path: Path) -> None:
        self.path: Path = path
        self.parent: Path = path.parent
        self.sound_type: str = "short" if self.parent.name == "shorts" else "long"
        self.full_name: str = path.name
        self.name: str = path.name.split(".")[0]
        self.extension: str = path.suffix
        self.is_default: bool = self.full_name in RESERVED_ALL_SOUNDS

    def __repr__(self) -> str:
        return f"Sound({self.path})"

    def __gt__(self, other) -> bool:
        if not isinstance(other, Sound):
            raise NotImplementedError
        return self.name > other.name

    def __lt__(self, other) -> bool:
        if not isinstance(other, Sound):
            raise NotImplementedError
        return self.name < other.name


def create_sounds_dict(path: Path) -> dict[str, Sound]:
    """Return dict of Sounds names and Sounds object mapped to them."""
    allowed_suffixes = {".wav", ".mp3", ".ogg", ".flac", ".opus"}

    return {
        sound.name.split(".")[0]: Sound(sound)
        for sound in path.glob("*")
        if sound.suffix in allowed_suffixes
    }


class SoundManager:
    """Class used to work with sounds in app
    Allow to perform CRUD on Shorts, Longs and play them.

    This class is a singleton.
    """

    _instance = None

    def __new__(cls) -> "SoundManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        pygame.mixer.init(channels=2)
        self._ambient_channel = pygame.mixer.Channel(1)
        self._sound_channel = pygame.mixer.Channel(2)
        """Channel 1 is for alarm and signal, Channel 2 is for ambient"""
        # Dicts containing all songs found at start up
        self._shorts_dict = create_sounds_dict(SHORTS_PATH)
        self._longs_dict = create_sounds_dict(LONGS_PATH)

        # Never change them, those maps are used to check existence or list - GET ONLY
        self._all_sounds_dict = ChainMap(self._shorts_dict, self._longs_dict)

    @property
    def user_shorts_list(self) -> list[str]:
        return sorted(
            [key for key, value in self._shorts_dict.items() if not value.is_default],
        )

    @property
    def all_shorts_list(self) -> list[str]:
        return sorted(self._shorts_dict.keys())

    @property
    def user_longs_list(self) -> list[str]:
        return sorted(
            [key for key, value in self._longs_dict.items() if not value.is_default],
        )

    @property
    def all_longs_list(self) -> list[str]:
        return sorted(self._longs_dict.keys())

    @property
    def all_sounds_list(self) -> list[str]:
        return sorted(self._all_sounds_dict.keys())

    def get_any_sound(self, name: str) -> Sound:
        """Get Sound object by passing name of it."""
        return self._all_sounds_dict[name]

    def is_duplicate(self, name: str) -> bool:
        """Check if the key exists in _all_shorts_longs_dict."""
        return bool(self._all_sounds_dict.get(name, False))

    def rename_sound(self, old_name: str, new_name: str) -> None:
        """Rename sound on users drive and remove old sound from
        corresponding dict and create new instance of Sound class.
        """
        # Rename on drive
        sound: Sound = self.get_any_sound(old_name)
        old_file_path = sound.path
        new_file_path = sound.parent / (new_name + sound.extension)
        old_file_path.rename(new_file_path)

        # Update dict
        if sound.sound_type == "short":
            del self._shorts_dict[sound.name]
            self._shorts_dict[new_name] = Sound(new_file_path)
        else:
            del self._longs_dict[sound.name]
            self._longs_dict[new_name] = Sound(new_file_path)

    def add_sound(
        self,
        path: Path,
        name: str,
        extension: str,
        sound_type: LengthType,
    ) -> None:
        """Add sound to right folder, create instance of Sound and to dict."""
        if sound_type == "short":
            new_path = SHORTS_PATH
            dict_ = self._shorts_dict
        else:
            new_path = LONGS_PATH
            dict_ = self._longs_dict

        sound = Sound(new_path / (name + extension))

        dict_[name] = sound
        shutil.copy(path, sound.path)

    def remove_sound(self, name: str, sound_type: LengthType) -> None:
        """Remove sound from users drive and update config if needed."""
        self._all_sounds_dict[name].path.unlink()
        if sound_type == "short":
            del self._shorts_dict[name]
        else:
            del self._longs_dict[name]

    def play_sound(
        self,
        sound_name: str,
        sound_volume: int,
    ) -> None:
        """Play chosen sound."""
        self._sound_channel.set_volume(sound_volume / 100)
        sound = pygame.mixer.Sound(self.get_any_sound(sound_name).path)
        self._sound_channel.play(sound)

    def play_ambient_in_background(self, ambient_name: str) -> None:
        """Play ambient in background with set volume to 0."""
        self._ambient_channel.set_volume(0)
        sound_path = self.get_any_sound(ambient_name).path
        sound = pygame.mixer.Sound(sound_path)
        self._ambient_channel.play(sound, loops=-1)

    def stop_ambient(self) -> None:
        """Stop playing ambient in the background."""
        self._ambient_channel.stop()

    def toggle_ambient(self, quite: bool, ambient_volume: int) -> None:
        """Turn on and off ambient."""
        volume = 0 if quite else ambient_volume / 100
        self._ambient_channel.set_volume(volume)

    def stop_sound(self) -> None:
        """Stop playing sound."""
        self._sound_channel.stop()
