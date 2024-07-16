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
