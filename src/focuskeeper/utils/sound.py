import os
import platform
from pathlib import Path
from typing import Literal

from focuskeeper.config import AppPaths

paths_obj = AppPaths()


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


def is_imported_sound(sound: str, sound_type: Literal['alarm', 'ambient']) -> bool:
    """Rerun is file already in users absences or sounds folder"""
    if sound_type == 'alarm':
        return sound in sounds_list(paths_obj.user_sounds)
    else:
        return sound in sounds_list(paths_obj.user_ambiences)


def soundify(sound: Path):
    """Remove all characters that are not a letter, number, - or _"""

    file_name = sound.name.rsplit('.')[0]
    return ''.join(map(lambda l: l if l.isalnum() or l in '_-' else '_', file_name))