import os
import platform
from typing import Literal

from textual import on
from textual.app import ComposeResult
from textual.events import Click
from textual.screen import ModalScreen

from focuskeeper.sound_manager import SoundManager
from focuskeeper.widgets import MusicDirectoryTree


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


def soundify(sound: str):
    """Remove all characters that are not a letter, number, - or _"""
    return ''.join(map(lambda l: l if l.isalnum() or l in '_-' else '_', sound))


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

    def __init__(self, sound_type: Literal['short', 'long'], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sound_type = sound_type
        self.sm = SoundManager()

    def compose(self) -> ComposeResult:
        yield MusicDirectoryTree(get_users_folder())

    @on(MusicDirectoryTree.FileSelected)
    def file_selected(self, event: MusicDirectoryTree.FileSelected) -> None:
        """Add sounds to chosen folder type"""
        sound = soundify(event.path.name.split('.')[0])

        if self.sm.sound_name_exist(sound):
            message = ("Sound name already in use.\n"
                       "Please change it before importing.")
            self.notify(message, severity='error')
            return None

        extension = f'.{event.path.name.split('.')[1]}'
        self.sm.add_sound(event.path, sound, extension, self.sound_type)
        self.notify(f'Imported: {sound}')
