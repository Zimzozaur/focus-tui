import os
import platform
from typing import TYPE_CHECKING

from textual import on
from textual.app import ComposeResult
from textual.events import Click
from textual.screen import ModalScreen

from focustui.constants import LengthType
from focustui.widgets import MusicDirectoryTree

if TYPE_CHECKING:
    from focustui.sound_manager import SoundManager


def get_users_folder() -> str:
    """Return name of the user's folder."""
    users_system = platform.system()

    if users_system == "Linux":
        return "/home"
    if users_system == "Windows":
        return os.path.expandvars("%SystemDrive%\\Users")
    if users_system == "Darwin":
        return "/Users"
    msg = "App does not support this operating system."
    raise NotImplementedError(msg)


def soundify(sound: str):
    """Remove all characters that are not a letter, number, - or _."""
    return "".join(
        char if char.isalnum() or char in {"_", "-"} else "_" for char in sound
    )


class AddSoundTree(ModalScreen):
    BINDINGS = [
        ("ctrl+q", "quit_app", "Quit App"),
        ("escape", "close_popup", "Close Popup"),
    ]

    def action_quit_app(self) -> None:
        self.app.exit()

    def action_close_popup(self) -> None:
        self.dismiss(True)

    def on_click(self, event: Click) -> None:
        """Close popup when clicked on the background
        and user is not editing
        Return [self.edited] to give information to call back.
        """
        is_background = self.get_widget_at(event.screen_x, event.screen_y)[0] is self
        if is_background:
            self.dismiss(True)

    def __init__(
            self,
            sound_type: LengthType,
            sm: "SoundManager",
            *args: tuple,
            **kwargs: dict,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.sound_type = sound_type
        self._sm = sm

    def compose(self) -> ComposeResult:
        yield MusicDirectoryTree(get_users_folder())

    @on(MusicDirectoryTree.FileSelected)
    def file_selected(self, event: MusicDirectoryTree.FileSelected) -> None:
        """Add sounds to chosen folder type."""
        sound = soundify(event.path.name.split(".")[0])

        if self._sm.is_duplicate(sound):
            message = "The sound name is already in use."
            self.notify(message, severity="error")
            return

        extension = f".{event.path.name.split('.')[1]}"
        self._sm.add_sound(
            event.path,
            sound,
            extension,
            self.sound_type,
        )
        self.notify(f"Imported: {sound}")
