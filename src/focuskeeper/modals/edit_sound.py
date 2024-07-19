from pathlib import Path
from typing import Literal

from textual import on
from textual.app import ComposeResult
from textual.containers import VerticalScroll, Horizontal, Center
from textual.events import Click
from textual.screen import ModalScreen
from textual.widgets import Button, Collapsible, Input, Static

from focuskeeper.config import AppConfig
from focuskeeper.modals import AddSoundTree
from focuskeeper.widgets import Accordion
from focuskeeper.utils.sound import sounds_list, remove_id_suffix, rename_file


class EditSound(ModalScreen):
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
            sound_type: Literal['alarm', 'ambient'],
            path_to_sounds: Path,
            *args, **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self.config = AppConfig()
        self.sound_type = sound_type
        self.path_to_sounds = path_to_sounds
        self.sounds_names: dict[str, str] = {
            sound.split('.')[0]: f'.{sound.split('.')[1]}'
            for sound in sounds_list(path_to_sounds)
        }


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
                for name in self.sounds_names.keys():
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
                    f"Add {'Sound' if self.sound_type != 'ambient' else 'Ambient'}",
                    variant='primary', id='add-sound-bt'
                )

    @on(Input.Changed)
    def check_sound_name(self, event: Input.Changed):
        """Check is new sound name correct"""
        query = f"#{remove_id_suffix(event.input.id)}_rename"
        sound_name = event.input.value
        self.query_one(query).disabled = (sound_name in self.sounds_names or
                                          sound_name in self.config.forbiden_sound_names())

    @on(Button.Pressed, '.sound-rename-bt')
    async def change_sound_name(self, event: Button.Pressed):
        """Change name of a sound and update DOM and dist"""
        # Change name
        sound_name = remove_id_suffix(event.button.id)
        extension = self.sounds_names[sound_name]
        old_name = sound_name + extension
        new_name = self.query_one(f'#{sound_name}_input', Input).value
        new_name_with_extension = new_name + extension
        rename_file(self.path_to_sounds, old_name, new_name_with_extension)
        # Update DOM and dict
        del self.sounds_names[sound_name]
        self.sounds_names[new_name] = extension
        self.config.change_sound_name_if_in_config(self.sound_type, old_name, new_name_with_extension)
        await self.recompose()
        if self.sound_type == 'ambient':
            self.notify('Changed name of an ambient')
        else:
            self.notify('Changed name of a sound')
        self.query_one(f'#{new_name}_coll', Collapsible).collapsed = False

    @on(Button.Pressed, '.sound-remove-bt')
    async def remove_sound(self, event: Button.Pressed):
        """Display confirmation screen
        if users accepts sound is removed from library
        """
        sound_name = remove_id_suffix(event.button.id)
        sound_to_remove = sound_name + self.sounds_names[sound_name]

        # if removed sound that is already used
        if self.config.is_sound_in_config(self.sound_type, sound_to_remove):
            if self.sound_type == 'ambient':
                self.config.change_sound_to_default(self.sound_type, sound_to_remove)
            else:
                self.config.change_sound_to_default(self.sound_type, sound_to_remove)

        # Remove sound
        (self.path_to_sounds / sound_to_remove).unlink()
        await self.recompose_(None)

    async def recompose_(self, arg):
        """Refresh and recompose screen"""
        self.sounds_names: dict[str, str] = {
            sound.split('.')[0]: f'.{sound.split('.')[1]}'
            for sound in sounds_list(self.path_to_sounds)
        }
        await self.recompose()

    @on(Button.Pressed, '#add-sound-bt')
    def open_music_directory_tree(self):
        self.app.push_screen(AddSoundTree(self.sound_type), self.recompose_)

