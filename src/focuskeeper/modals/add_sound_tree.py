import shutil

from textual import on
from textual.app import ComposeResult
from textual.events import Click
from textual.screen import ModalScreen

from focuskeeper.config import AppPaths
from focuskeeper.widgets import MusicDirectoryTree
from focuskeeper.utils.sound import get_users_folder, soundify, is_imported_sound


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

    def __init__(self, sound_type, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sound_type = sound_type
        self.paths = AppPaths()

    def compose(self) -> ComposeResult:
        yield MusicDirectoryTree(get_users_folder())

    @on(MusicDirectoryTree.FileSelected)
    def file_selected(self, event: MusicDirectoryTree.FileSelected) -> None:
        """Add sounds to chosen folder type"""
        soundified_name = f'{soundify(event.path)}{event.path.suffix}'
        if is_imported_sound(soundified_name, self.sound_type):
            self.notify('Sound already imported', severity='warning')
            return None

        if self.sound_type == 'ambient':
            path = self.paths.user_ambiences
        else:
            path = self.paths.user_sounds

        shutil.copy(event.path, path / soundified_name)
        self.notify(f'Imported: {soundified_name}')
