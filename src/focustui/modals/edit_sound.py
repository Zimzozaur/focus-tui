from typing import TYPE_CHECKING

from textual import on
from textual.app import ComposeResult
from textual.containers import Center, Horizontal
from textual.events import Click
from textual.screen import ModalScreen
from textual.widgets import Button, Collapsible, Input, Static

from focustui.constants import LengthType
from focustui.modals import AddSoundTree, ConfirmPopup
from focustui.widgets import Accordion

if TYPE_CHECKING:
    from focustui.config_manager import ConfigManager
    from focustui.sound_manager import SoundManager


def remove_id_suffix(string: str) -> str:
    """Remove _something from the end of the string."""
    return string[:string.rindex("_")]


class EditSound(ModalScreen):
    """EditSound allow user to perform CRUD operation on sounds."""

    BINDINGS = [
        ("ctrl+q", "quit_app", "Quit App"),
        ("escape", "close_popup", "Close Popup"),
    ]

    def action_quit_app(self) -> None:
        self.app.exit()

    def __init__(
        self,
        sound_type: LengthType,
        sm: "SoundManager",
        cm: "ConfigManager",
        *args: tuple,
        **kwargs: dict,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._cm = cm
        self._sm = sm
        self._sound_type = sound_type
        if self._sound_type == "short":
            self._sounds_names = self._sm.user_shorts_list
        else:
            self._sounds_names = self._sm.user_longs_list

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

    def compose(self) -> ComposeResult:
        restriction = r"^[a-zA-Z0-9_-]+$"
        with Accordion(id="sounds-accordion"):
            for name in self._sounds_names:
                with Collapsible(
                        title=name, classes="sound-collapsible", id=f"{name}_coll",
                ):
                    yield Input(
                        value=name, id=f"{name}_input", restrict=restriction,
                    )
                    with Horizontal(classes="sound-buttons-wrapper"):
                        yield Button(
                            "Rename",
                            variant="success",
                            disabled=True,
                            id=f"{name}_rename",
                            classes="sound-rename-bt",
                        )
                        yield Static(classes="sound-buttons-divider")
                        yield Button(
                            "Remove",
                            variant="error",
                            id=f"{name}_remove",
                            classes="sound-remove-bt",
                        )

            yield Static(id="add-sound-divider")
            with Center(id="add-sound-wrapper"):
                yield Button(
                    f"Add {'Sound' if self._sound_type != 'long' else 'Ambient'}",
                    variant="primary",
                    id="add-sound-bt",
                )

    @on(Input.Changed)
    def check_sound_name(self, event: Input.Changed) -> None:
        """Check is new sound name correct."""
        query = f"#{remove_id_suffix(event.input.id)}_rename"
        sound_name = event.input.value
        disable = not sound_name or self._sm.is_duplicate(sound_name)
        self.query_one(query).disabled = disable

    @on(Button.Pressed, ".sound-rename-bt")
    async def change_sound_name(self, event: Button.Pressed) -> None:
        """Change name of a sound and update DOM."""
        # Change name
        old_name = remove_id_suffix(event.button.id)
        new_name = self.query_one(f"#{old_name}_input", Input).value
        self._sm.rename_sound(old_name, new_name)
        # Update config if needed
        self._cm.update_sound_name(old_name, new_name)

        # Update DOM
        await self.recompose_(None)
        if self._sound_type == "long":
            self.notify("Renamed ambient")
        else:
            self.notify("Renamed sound")

        self.query_one(f"#{new_name}_coll", Collapsible).collapsed = False

    @on(Button.Pressed, ".sound-remove-bt")
    async def should_remove_sound(self, event: Button.Pressed) -> None:
        """Display confirmation screen if users accepts
        Sound is removed from drive.
        """

        async def remove_sound(boolean: bool) -> None:
            """Remove sound."""
            if not boolean:
                return
            # if removed sound that is already used
            if self._cm.is_sound_in_config(sound_name):
                self._cm.update_sound_name(sound_name)
            self._sm.remove_sound(sound_name, self._sound_type)
            self.notify("Removed sound")
            await self.recompose_(None)

        sound_name = remove_id_suffix(event.button.id)
        message = "Are you sure you want to remove the sound?"
        await self.app.push_screen(ConfirmPopup(message=message), remove_sound)

    @on(Button.Pressed, "#add-sound-bt")
    async def open_music_directory_tree(self) -> None:
        """Push AddSoundTree that allow user to add new songs."""
        await self.app.push_screen(
            AddSoundTree(
                self._sound_type, sm=self._sm),
            self.recompose_,
        )

    async def recompose_(self, arg_from_callback) -> None:
        """Update list before recompose."""
        if self._sound_type == "short":
            self._sounds_names = self._sm.user_shorts_list
        else:
            self._sounds_names = self._sm.user_longs_list
        await self.recompose()
