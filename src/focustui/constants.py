import os
import re
from pathlib import Path
from re import Pattern
from typing import Literal

from dotenv import load_dotenv
from platformdirs import user_data_dir

#############################
#       Custom Types        #
#############################

VolumeType = Literal["alarm_volume", "signal_volume", "ambient_volume", "test_volume"]
SoundType = Literal["alarm", "signal", "ambient"]
LengthType = Literal["short", "long"]
InputModeType = Literal["minute", "hour_minute"]
ClockDisplayMode = Literal["hour", "minute"]


#############################
#      Custom Settings      #
#############################

load_dotenv()

# is Debug mode on
FOCUSTUI_DEBUG: bool = os.getenv("FOCUSTUI_DEBUG") == "True"

# Number of seconds in a minute
_minute = os.getenv("FOCUSTUI_DEBUG_MINUTE")
is_custom = FOCUSTUI_DEBUG and _minute is not None
MINUTE: int = int(_minute) if is_custom else 60

# Min number of minutes that session has to take at minimum
_min_sessions_len = os.getenv("FOCUSTUI_DEBUG_MIN_SESSION_LEN")
is_custom = FOCUSTUI_DEBUG and _min_sessions_len is not None
MIN_SESSION_LEN = int(_min_sessions_len) if is_custom else 5
MAX_SESSION_LEN: int = 120
MAX_SESSION_LEN_HOUR: int = 5
DEFAULT_SESSION_LEN: str = "45"
SESSION_SIGNATURE: Pattern[str] = re.compile("^([0-9]{1,3}|[0-3]:[0-9]{1,2})$")


#############################
#      Default Settings     #
#############################

# Root
MAIN_DIR_PATH: Path = Path(user_data_dir()) / "focus-tui"

# Sounds path
SOUNDS_PATH: Path = MAIN_DIR_PATH / "sounds"
SHORTS_PATH: Path = SOUNDS_PATH / "shorts"
LONGS_PATH: Path = SOUNDS_PATH / "longs"

# Others
THEMES_PATH: Path = MAIN_DIR_PATH / "themes"
QUEUES_PATH: Path = MAIN_DIR_PATH / "queues"

# Files
DB_FILE_PATH: Path = MAIN_DIR_PATH / "focus-tui.db"
CONFIG_FILE_PATH: Path = MAIN_DIR_PATH / "config.json"

# Default sounds
DEFAULT_ALARM_NAME: str = "Woohoo"
DEFAULT_SIGNAL_NAME: str = "Landing"
DEFAULT_AMBIENT_NAME: str = "Woodpecker_Forest"

# Reserved Sounds
RESERVED_SHORTS: set = {
    "Acid_Bassline.flac",
    "Braam.flac",
    "Landing_Forcefield.flac",
    "Woohoo.flac",
}
RESERVED_LONG: set = {"Mexican_Forest.wav", "Woodpecker_Forest.flac"}
RESERVED_ALL_SOUNDS: set = RESERVED_SHORTS | RESERVED_LONG

DEFAULT_SOUND_VOLUME: int = 50
MIN_VOLUME_LEVEL: int = 1
MAX_VOLUME_LEVEL: int = 100

DEFAULT_TIME_INPUT_TYPE: InputModeType = "minute"
DEFAULT_CLOCK_DISPLAY_HOURS: bool = False
DEFAULT_CLOCK_DISPLAY_SECONDS: bool = True

HOURS_MINUTES_TIMER_PATTERN: re.Pattern = re.compile(r"^([0-5]|[0-4]:[0-5]?[0-9])$")

DISCORD_INVITATION = "https://discord.gg/JF44rr67Ng"
PROJECT_GITHUB = "https://github.com/Zimzozaur/focus-tui"
SIMONS_X_ACCOUNT = "https://x.com/zimzozaur"
