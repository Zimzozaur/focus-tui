"""Collection of custom widget."""

# Local imports.
from .about_settings import AboutSettings
from .accordion import Accordion
from .app_header import AppHeader
from .clock_display import ClockDisplay
from .music_directory_tree import MusicDirectoryTree
from .sound_settings import SoundSettings
from .sound_volume_input import SoundVolumeInput

# Public symbols
__all__ = [
    "SoundSettings",
    "AppHeader",
    "AboutSettings",
    "Accordion",
    "MusicDirectoryTree",
    "ClockDisplay",
    "SoundVolumeInput",
]
