from typing import Literal

import pygame

from focusseeds.db import DatabaseManager
from focusseeds.setup import AppPaths


class SoundMixer:
    """Takes control of how music is play in app"""
    db = DatabaseManager()
    paths = AppPaths()

    def play_sound(self, sound_type: Literal['alarm', 'signal']) -> None:
        """Play chosen sound"""
        sound, is_default = self.db.get_sound_name(sound_type)
        sound_path = self.paths.sounds if is_default else self.paths.user_sounds
        pygame.mixer.music.load(sound_path / sound)
        pygame.mixer.music.play(loops=1)
