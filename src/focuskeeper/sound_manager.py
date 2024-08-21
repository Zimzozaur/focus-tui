import shutil
from collections import ChainMap
from pathlib import Path
from typing import Literal

import pygame

from focuskeeper.config import get_used_sound, is_sound_in_config, update_sound_name
from focuskeeper.constants import LONGS_PATH, RESERVED_ALL_SOUNDS, SHORT_PATH


class Sound:
    """Class that represent sound file."""

    def __init__(
        self,
        path: Path,
        sound_type: Literal["short", "long"],
    ) -> None:
        self.path: Path = path
        self.parent: Path = path.parent
        self.sound_type: Literal["short", "long"] = sound_type
        self.full_name = path.name
        self.name: str = path.name.split(".")[0]
        self.extension: str = path.suffix
        self.is_default: bool = self.full_name in RESERVED_ALL_SOUNDS

    def __repr__(self) -> str:
        return f"Sound({self.path}, '{self.sound_type}', {self.is_default})"

    def __gt__(self, other) -> bool:
        if not isinstance(other, Sound):
            raise NotImplementedError
        return self.name > other.name

    def __lt__(self, other) -> bool:
        if not isinstance(other, Sound):
            raise NotImplementedError
        return self.name < other.name


def create_sounds_dict(
    path: Path, sound_type: Literal["short", "long"],
) -> dict[str, Sound]:
    """Return dict of Sounds names and Sounds object mapped to them."""
    allowed_suffixes = {".wav", ".mp3", ".ogg", ".flac", ".opus"}

    return {
        sound.name.split(".")[0]: Sound(sound, sound_type)
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
        # Dicts containing all songs found at start up
        self._shorts_dict = create_sounds_dict(SHORT_PATH, "short")
        self._longs_dict = create_sounds_dict(LONGS_PATH, "long")

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

    @property
    def get_used_alarm(self) -> str:
        return get_used_sound("alarm")

    @property
    def get_used_signal(self) -> str:
        return get_used_sound("signal")

    @property
    def get_used_ambient(self) -> str:
        return get_used_sound("ambient")

    def get_any_sound(self, name: str) -> Sound:
        """Get Sound object by passing name of it."""
        return self._all_sounds_dict[name]

    def exists_in_all_dicts(self, name: str) -> bool:
        """Check if the key exists in _all_shorts_longs_dict."""
        return bool(self._all_sounds_dict.get(name, False))

    def rename_sound(self, old_name: str, new_name: str) -> None:
        """Rename sound on users drive and remove old sound from
        corresponding dict and create new instance of Sound class
        if sound was used in config rename it.
        """
        # Rename on drive
        sound: Sound = self.get_any_sound(old_name)
        old_file_path = sound.path
        new_file_path = sound.parent / (new_name + sound.extension)
        old_file_path.rename(new_file_path)

        # Update dict
        if sound.sound_type == "short":
            del self._shorts_dict[sound.name]
            self._shorts_dict[new_name] = Sound(new_file_path, "short")
        else:
            del self._longs_dict[sound.name]
            self._longs_dict[new_name] = Sound(new_file_path, "long")

        # Update config if needed
        update_sound_name(old_name, new_name)

    def add_sound(
        self,
        path: Path,
        name: str,
        extension: str,
        sound_type: Literal["short", "long"],
    ) -> None:
        """Add sound to right folder, create instance of Sound and to dict."""
        if sound_type == "short":
            new_path = SHORT_PATH
            dict_ = self._shorts_dict
        else:
            new_path = LONGS_PATH
            dict_ = self._longs_dict

        sound = Sound(new_path / (name + extension), sound_type)

        dict_[name] = sound
        shutil.copy(path, sound.path)

    def remove_sound(self, name: str, sound_type: Literal["short", "long"]) -> None:
        """Remove sound from users drive and update config if needed."""
        if is_sound_in_config(name):
            update_sound_name(name)
        # Remove from drive
        self._all_sounds_dict[name].path.unlink()
        # Remove form dict
        if sound_type == "short":
            del self._shorts_dict[name]
        else:
            del self._longs_dict[name]

    def sound_name_exist(self, name: str) -> bool:
        """Check if the sound is already imported."""
        return bool(self._all_sounds_dict.get(name, False))

    def play_sound(self, name: str) -> None:
        """Play chosen sound."""
        pygame.mixer.music.load(self.get_any_sound(name).path)
        pygame.mixer.music.play()

    def play_alarm(self) -> None:
        """Play alarm sounds."""
        self.play_sound(self.get_used_alarm)

    @staticmethod
    def stop_sound() -> None:
        """Stop all sounds."""
        pygame.mixer.music.stop()
