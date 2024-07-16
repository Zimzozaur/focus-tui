from pathlib import Path

import pygame


def play_sound(sound_path: Path, times: int):
    pygame.mixer.music.load(sound_path)
    pygame.mixer.music.play(loops=times)




