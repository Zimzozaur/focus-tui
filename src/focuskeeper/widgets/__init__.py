"""Collection of custom widget"""

# Local imports.
from .about_settings import AboutSettings
from .accordion import Accordion
from .app_header import AppHeader
from .clock_display import ClockDisplay
from .music_directory_tree import MusicDirectoryTree
from .sound_settings import SoundSettings

# Public symbols
__all__ = [
    "AppHeader",
    "AboutSettings",
    "Accordion",
    "MusicDirectoryTree",
    "SoundSettings",
    "ClockDisplay",
]
