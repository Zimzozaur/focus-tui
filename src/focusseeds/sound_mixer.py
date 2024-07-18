from pathlib import Path
from typing import Literal

import pygame

from focusseeds.config import AppConfig


class SoundMixer:
    """Takes control of how music is play in app"""
    config = AppConfig()

    def play_sound(self, sound_type: Literal['alarm', 'signal']) -> None:
        """Play chosen sound"""
        sound_dict = self.config.get_used_sound(sound_type)
        sound, sound_path = sound_dict['name'], sound_dict['path']
        pygame.mixer.music.load(sound_path + '/' + sound)
        pygame.mixer.music.play(loops=1)

    def play_any_sound(self, path: Path, sound: str):
        """Play any sound that is passed by path and sound name with extension"""
        pygame.mixer.music.load(path / sound)
        pygame.mixer.music.play(loops=1)

    def stop_all_sounds(self):
        """Stop playing everything"""
        pygame.mixer.music.stop()
