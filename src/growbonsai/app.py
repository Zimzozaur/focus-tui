import pygame
from textual.app import App
from textual.widgets import Button

from config import UNFA_LANDING, UNFA_ACID_BASSLINE, UNFS_BRAAM, UNFS_WOOHOO

pygame.init()


class MyApp(App):
    def compose(self):
        yield Button(label="Braam", id='braam')
        yield Button(label="Acid Bassline", id='acid')
        yield Button(label="Woohoo", id='woohoo')
        yield Button(label="Landing", id='landing')

    def on_button_pressed(self, even: Button.Pressed):
        # Play sound when the button is pressed
        button_id = even.button.id
        if button_id == 'braam':
            play_sound(UNFS_BRAAM)
        elif button_id == 'woohoo':
            play_sound(UNFS_WOOHOO)
        elif button_id == 'landing':
            play_sound(UNFA_LANDING)
        else:
            play_sound(UNFA_ACID_BASSLINE)

def play_sound(song_name):
    # Define the path to the sound file
    pygame.mixer.music.load(song_name)
    pygame.mixer.music.play()


if __name__ == "__main__":
    MyApp().run()


