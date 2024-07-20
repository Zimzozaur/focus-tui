from typing import Literal

from textual import on
from textual.app import ComposeResult
from textual.containers import VerticalScroll, Horizontal, Center
from textual.events import Click
from textual.screen import ModalScreen
from textual.widgets import Button, Collapsible, Input, Static

from focuskeeper.config import AppConfig
from focuskeeper.modals import AddSoundTree, ConfirmPopup
from focuskeeper.widgets import Accordion
from focuskeeper.sound_manager import SoundManager


def remove_id_suffix(string: str) -> str:
    """Remove _something from the end of the string"""
    return string[:string.rindex('_')]


class EditSound(ModalScreen):
    """EditSound allow user to perform CUD operation on sounds"""

    DEFAULT_CSS = """
    EditSound {
        align: center middle;
        width: auto;
        height: auto;
    }

    #edit-sound-body {
        min-width: 50;
        max-width: 70;
        height: 30;
        padding: 1 2;
        background: $surface;
    }

    #sounds-accordion {
        min-width: 50;
        max-width: 70;
        height: auto;
    }

    .sound-buttons-wrapper {
        height: auto;
        padding: 1 1 0 1;
        width: 100%;
    }

    #add-sound-wrapper {
        height: auto;
    }

    .sound-buttons-divider {
        width: 1fr;
    }

    #add-sound-divider {
        height: 1fr
    }
    """
    BINDINGS = [
        ('ctrl+q', 'quit_app', 'Quit App'),
        ('escape', 'close_popup', 'Close Popup')
    ]

    def action_quit_app(self):
        self.app.exit()

    def __init__(
            self,
            sound_type: Literal['short', 'long'],
            *args, **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        # Imported classes
        self.config = AppConfig()
        self.sm = SoundManager()
        # Type of sound, either 'alarm' or 'ambient'
        self.sound_type = sound_type
        if self.sound_type == 'short':
            self.sounds_names = self.sm.user_shorts_list
        else:
            self.sounds_names = self.sm.user_longs_list

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

    def compose(self) -> ComposeResult:
        with VerticalScroll(id='edit-sound-body'):
            with Accordion(id='sounds-accordion'):
                for name in self.sounds_names:
                    with Collapsible(title=name, classes='sound-collapsible', id=f'{name}_coll'):
                        yield Input(value=name, id=f"{name}_input", restrict=r'^[a-zA-Z0-9_-]+$')
                        with Horizontal(classes='sound-buttons-wrapper'):
                            yield Button('Rename', variant='success',
                                         disabled=True, id=f"{name}_rename", classes='sound-rename-bt')
                            yield Static(classes='sound-buttons-divider')
                            yield Button('Remove', variant='error',
                                         id=f"{name}_remove", classes='sound-remove-bt')

            yield Static(id='add-sound-divider')
            with Center(id='add-sound-wrapper'):
                yield Button(
                    f"Add {'Sound' if self.sound_type != 'long' else 'Ambient'}",
                    variant='primary', id='add-sound-bt'
                )

    @on(Input.Changed)
    def check_sound_name(self, event: Input.Changed):
        """Check is new sound name correct"""
        query = f"#{remove_id_suffix(event.input.id)}_rename"
        sound_name = event.input.value
        self.query_one(query).disabled = sound_name in self.sm.all_shorts_longs_dict

    @on(Button.Pressed, '.sound-rename-bt')
    async def change_sound_name(self, event: Button.Pressed):
        """Change name of a sound and update DOM"""
        # Change name
        old_name = remove_id_suffix(event.button.id)
        new_name = self.query_one(f'#{old_name}_input', Input).value
        self.sm.rename_sound(old_name, new_name)
        # Update DOM
        await self.recompose_(None)
        if self.sound_type == 'long':
            self.notify('Changed name of an ambient')
        else:
            self.notify('Changed name of a sound')

        self.query_one(f'#{new_name}_coll', Collapsible).collapsed = False

    @on(Button.Pressed, '.sound-remove-bt')
    async def should_remove_sound(self, event: Button.Pressed):
        """Display confirmation screen if users accepts
        Sound is removed from drive
        """
        async def remove_sound(boolean: bool) -> None:
            """Remove sound"""
            if not boolean:
                return None
            # if removed sound that is already used
            self.sm.remove_sound(sound_name, self.sound_type)
            self.notify('Sound has been remove')
            await self.recompose_(None)

        sound_name = remove_id_suffix(event.button.id)
        message = 'Are you sure you want to remove sound?'
        await self.app.push_screen(ConfirmPopup(message=message), remove_sound)

    @on(Button.Pressed, '#add-sound-bt')
    async def open_music_directory_tree(self):
        """Push AddSoundTree that allow user to add new songs"""
        await self.app.push_screen(AddSoundTree(self.sound_type), self.recompose_)

    async def recompose_(self, arg_from_callback) -> None:
        """Update list before recompose"""
        if self.sound_type == 'short':
            self.sounds_names = self.sm.user_shorts_list
        else:
            self.sounds_names = self.sm.user_longs_list
        await self.recompose()