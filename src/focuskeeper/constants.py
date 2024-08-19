import os
from pathlib import Path

from dotenv import load_dotenv

from platformdirs import user_data_dir


load_dotenv(override=True)

DEBUG: bool = True if os.getenv('DEBUG') == 'True' else False

# Number of seconds in a minute
MINUTE: int = 60 if not DEBUG else 1
MIN_SESSION_LEN: int = 5 if not DEBUG else 1

# Root
MAIN_DIR_PATH: Path = Path(user_data_dir()) / 'focus-keeper'

# Sounds path
SOUNDS_PATH: Path = MAIN_DIR_PATH / 'sounds'
SHORT_PATH: Path = SOUNDS_PATH / 'shorts'
LONGS_PATH: Path = SOUNDS_PATH / 'longs'

# Others
THEMES_PATH: Path = MAIN_DIR_PATH / 'themes'
QUEUES_PATH: Path = MAIN_DIR_PATH / 'queues'

# Files
DB_FILE_PATH: Path = MAIN_DIR_PATH / 'focus_keeper.db'
CONFIG_FILE_PATH: Path = MAIN_DIR_PATH / 'config.yaml'

# Default sounds
DEFAULT_ALARM_NAME: str = 'Woohoo'
DEFAULT_SIGNAL_NAME: str = 'Landing'
DEFAULT_AMBIENT_NAME: str = 'Woodpecker_Forest'

# Reserved Sounds
RESERVED_SHORTS: set = {
    'Acid_bassline.flac',
    'Braam.flac',
    'Landing_forcefield.flac',
    'Woohoo.flac'
}

RESERVED_LONG: set = {
    'Mexican_Forest.wav',
    'Woodpecker_Forest.flac'
}

RESERVED_ALL_SOUNDS: set = RESERVED_SHORTS | RESERVED_LONG
