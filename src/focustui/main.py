import json
import os
import re
import webbrowser

from collections import ChainMap
import shutil
from pathlib import Path
from re import Pattern
from sqlite3 import connect
from sys import platform
from typing import Iterable, Literal, cast

import click
import pygame
from click import Choice, echo, style
from dotenv import load_dotenv
from platformdirs import user_data_dir

from pydantic import BaseModel, ConfigDict, field_validator
from textual.events import Click
from textual.reactive import reactive
from textual.widget import Widget

from textual.widgets import *
from textual.validation import Validator, ValidationResult
from textual import on
from textual.screen import Screen, ModalScreen
from textual.app import App, ComposeResult
from textual.containers import Grid, Center, Horizontal, Vertical, VerticalScroll, Container


from focustui.assets import *



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
RESERVED_SHORTS: set[str] = {
    "Acid_Bassline.flac",
    "Braam.flac",
    "Landing_Forcefield.flac",
    "Woohoo.flac",
}
RESERVED_LONG: set[str] = {"Mexican_Forest.wav", "Woodpecker_Forest.flac"}
RESERVED_ALL_SOUNDS: set[str] = RESERVED_SHORTS | RESERVED_LONG

DEFAULT_SOUND_VOLUME: int = 50
MIN_VOLUME_LEVEL: int = 1
MAX_VOLUME_LEVEL: int = 100

DEFAULT_TIME_INPUT_TYPE: InputModeType = "minute"
DEFAULT_CLOCK_DISPLAY_HOURS: bool = False
DEFAULT_CLOCK_DISPLAY_SECONDS: bool = True

HOURS_MINUTES_TIMER_PATTERN: Pattern[str] = re.compile(r"^([0-5]|[0-4]:[0-5]?[0-9])$")

DISCORD_INVITATION = "https://discord.gg/new7rgTw"
PROJECT_GITHUB = "https://github.com/Zimzozaur/focus-tui"
SIMONS_X_ACCOUNT = "https://x.com/zimzozaur"


def session_len_parser(string: str) -> int:
    """If input string is correct return length
    if not return -1 as the indicator of invalid value.

    It accepts 0 or value in one of the 2 forms:
    1. Minutes form - value between MIN to MAX
    2. Hour form - H:M or H:MM between MIN and MAX
    """
    if not SESSION_SIGNATURE.match(string):
        return -1
    if ":" in string:
        hour, minute = string.split(":")
        time = int(hour) * MINUTE + int(minute)
        if time == 0 or MIN_SESSION_LEN <= time <= MAX_SESSION_LEN:
            return time
        return -1
    time = int(string)
    if time == 0 or MIN_SESSION_LEN <= time <= MAX_SESSION_LEN:
        return time
    return -1




tooltip = (
    "Type 0 to set stopwatch\n"
    "Or 5-120 for timer in minutes\n"
    "Examples: 5, 49, 120 (minutes)\n"
    "Or 0:5, 0:49, 2:0 (hours:minutes)"
)


class SessionInputValidator(Validator):
    def validate(self, value: str) -> ValidationResult:
        if session_len_parser(value) != -1:
            return self.success()
        return self.failure()


class ValueFrom1to100(Validator):
    def validate(self, value: str) -> ValidationResult:
        if not value or int(value) < MIN_VOLUME_LEVEL or int(value) > MAX_VOLUME_LEVEL:
            return self.failure()
        return self.success()



class SessionLenInput(Input):
    """Accept 0 or value in one of the 2 forms:
    1. Minutes form - value between MIN to MAX
    2. Hour form - H:M or H:MM between MIN and MAX.
    """

    def __init__(self, cm: "ConfigManager", *args, **kwargs) -> None:
        super().__init__(
            *args,
            value=cm.get_session_length(),
            id="session-duration",
            tooltip=tooltip,
            restrict="[0-9:]*$",
            validators=[SessionInputValidator()],
            **kwargs,
        )

    def to_int(self) -> int:
        return session_len_parser(self.value)


class SoundVolumeInput(Input):
    def __init__(
            self, **kwargs,
    ) -> None:
        super().__init__(
            placeholder=f"{MIN_VOLUME_LEVEL} - {MAX_VOLUME_LEVEL}",
            restrict=r"^(100|[1-9][0-9]?|0?[1-9])$",
            validators=[ValueFrom1to100()],
            type="integer",
            **kwargs,
        )



class Sound:
    """Class that represent sound file."""

    def __init__(self, path: Path) -> None:
        self.path: Path = path
        self.parent: Path = path.parent
        self.sound_type: str = "short" if self.parent.name == "shorts" else "long"
        self.full_name: str = path.name
        self.name: str = path.name.split(".")[0]
        self.extension: str = path.suffix
        self.is_default: bool = self.full_name in RESERVED_ALL_SOUNDS

    def __repr__(self) -> str:
        return f"Sound({self.path})"

    def __gt__(self, other) -> bool:
        if not isinstance(other, Sound):
            raise NotImplementedError
        return self.name > other.name

    def __lt__(self, other) -> bool:
        if not isinstance(other, Sound):
            raise NotImplementedError
        return self.name < other.name


def create_sounds_dict(path: Path) -> dict[str, Sound]:
    """Return dict of Sounds names and Sounds object mapped to them."""
    allowed_suffixes = {".wav", ".mp3", ".ogg", ".flac", ".opus"}

    return {
        sound.name.split(".")[0]: Sound(sound)
        for sound in path.glob("*")
        if sound.suffix in allowed_suffixes
    }


class SoundManager:
    """Class used to work with sounds in app
    Allow to perform CRUD on Shorts, Longs and play them.

    This class is a singleton.
    """

    _instance = None

    def __new__(cls) -> "SoundManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        pygame.mixer.init(channels=2)
        self._ambient_channel = pygame.mixer.Channel(1)
        self._sound_channel = pygame.mixer.Channel(2)
        """Channel 1 is for alarm and signal, Channel 2 is for ambient"""
        # Dicts containing all songs found at start up
        self._shorts_dict = create_sounds_dict(SHORTS_PATH)
        self._longs_dict = create_sounds_dict(LONGS_PATH)

        # Never change them, those maps are used to check existence or list - GET ONLY
        self._all_sounds_dict = ChainMap(self._shorts_dict, self._longs_dict)

    @property
    def user_shorts_list(self) -> list[str]:
        return sorted(
            [key for key, value in self._shorts_dict.items() if not value.is_default],
        )

    @property
    def all_shorts_list(self) -> list[str]:
        return sorted(self._shorts_dict.keys())

    @property
    def user_longs_list(self) -> list[str]:
        return sorted(
            [key for key, value in self._longs_dict.items() if not value.is_default],
        )

    @property
    def all_longs_list(self) -> list[str]:
        return sorted(self._longs_dict.keys())

    @property
    def all_sounds_list(self) -> list[str]:
        return sorted(self._all_sounds_dict.keys())

    def get_any_sound(self, name: str) -> Sound:
        """Get Sound object by passing name of it."""
        return self._all_sounds_dict[name]

    def is_duplicate(self, name: str) -> bool:
        """Check if the key exists in _all_shorts_longs_dict."""
        return bool(self._all_sounds_dict.get(name, False))

    def rename_sound(self, old_name: str, new_name: str) -> None:
        """Rename sound on users drive and remove old sound from
        corresponding dict and create new instance of Sound class.
        """
        # Rename on drive
        sound: Sound = self.get_any_sound(old_name)
        old_file_path = sound.path
        new_file_path = sound.parent / (new_name + sound.extension)
        old_file_path.rename(new_file_path)

        # Update dict
        if sound.sound_type == "short":
            del self._shorts_dict[sound.name]
            self._shorts_dict[new_name] = Sound(new_file_path)
        else:
            del self._longs_dict[sound.name]
            self._longs_dict[new_name] = Sound(new_file_path)

    def add_sound(
            self,
            path: Path,
            name: str,
            extension: str,
            sound_type: LengthType,
    ) -> None:
        """Add sound to right folder, create instance of Sound and to dict."""
        if sound_type == "short":
            new_path = SHORTS_PATH
            dict_ = self._shorts_dict
        else:
            new_path = LONGS_PATH
            dict_ = self._longs_dict

        sound = Sound(new_path / (name + extension))

        dict_[name] = sound
        shutil.copy(path, sound.path)

    def remove_sound(self, name: str, sound_type: LengthType) -> None:
        """Remove sound from users drive and update config if needed."""
        self._all_sounds_dict[name].path.unlink()
        if sound_type == "short":
            del self._shorts_dict[name]
        else:
            del self._longs_dict[name]

    def play_sound(
            self,
            sound_name: str,
            sound_volume: int,
    ) -> None:
        """Play chosen sound."""
        self._sound_channel.set_volume(sound_volume / 100)
        sound = pygame.mixer.Sound(self.get_any_sound(sound_name).path)
        self._sound_channel.play(sound)

    def play_ambient_in_background(self, ambient_name: str) -> None:
        """Play ambient in background with set volume to 0."""
        self._ambient_channel.set_volume(0)
        sound_path = self.get_any_sound(ambient_name).path
        sound = pygame.mixer.Sound(sound_path)
        self._ambient_channel.play(sound, loops=-1)

    def stop_ambient(self) -> None:
        """Stop playing ambient in the background."""
        self._ambient_channel.stop()

    def toggle_ambient(self, quite: bool, ambient_volume: int) -> None:
        """Turn on and off ambient."""
        volume = 0 if quite else ambient_volume / 100
        self._ambient_channel.set_volume(volume)

    def stop_sound(self) -> None:
        """Stop playing sound."""
        self._sound_channel.stop()

class _SoundModel(BaseModel):
    model_config = ConfigDict(extra="ignore")

    # Fields
    name: str
    volume: int = DEFAULT_SOUND_VOLUME

    @field_validator("name")
    def validate_name(cls, string: str) -> str:
        for char in string:
            if not (char.isalpha() or char.isdigit() or char in {"_", "-", "'"}):
                msg = ("Only letters, numbers, underscore, "
                       "dash or apostrophe are allowed in sound name")
                raise ValueError(msg)
        return string

    @field_validator("volume")
    def validate_volume(cls, value: int) -> int:
        """Set to default when value is not correct."""
        if value < MIN_VOLUME_LEVEL or value > MAX_VOLUME_LEVEL:
            return DEFAULT_SOUND_VOLUME
        return value


class AlarmModel(_SoundModel):
    name: str = DEFAULT_ALARM_NAME


class SignalModel(_SoundModel):
    name: str = DEFAULT_SIGNAL_NAME


class AmbientModel(_SoundModel):
    name: str = DEFAULT_AMBIENT_NAME


class ConfigModel(BaseModel):
    model_config = ConfigDict(extra="ignore")

    # Fields
    alarm: AlarmModel = AlarmModel()
    signal: SignalModel = SignalModel()
    ambient: AmbientModel = AmbientModel()
    session_length: str = DEFAULT_SESSION_LEN
    test_volume: int = DEFAULT_SOUND_VOLUME
    input_mode_type: InputModeType = DEFAULT_TIME_INPUT_TYPE
    clock_display_hours: bool = DEFAULT_CLOCK_DISPLAY_HOURS
    clock_display_seconds: bool = DEFAULT_CLOCK_DISPLAY_SECONDS

    @field_validator("session_length")
    def session_length_validator(cls, value: str):
        if session_len_parser(value) == -1:
            return DEFAULT_SESSION_LEN
        return value

    @field_validator("test_volume")
    def validate_volume(cls, value: int) -> int:
        if value < MIN_VOLUME_LEVEL or value > MAX_VOLUME_LEVEL:
            return DEFAULT_SOUND_VOLUME
        return value


def _load_and_validate_model() -> ConfigModel:
    with Path(CONFIG_FILE_PATH).open() as file:
        data = json.load(file)
        return ConfigModel.model_validate(data)


class ConfigManager:
    _instance = None
    config = None

    def __new__(cls) -> "ConfigManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        self.config: ConfigModel = _load_and_validate_model()

    def get_sound_name(self, sound_type: SoundType) -> str:
        """Get from config.json name of chosen sound_type."""
        return getattr(self.config, sound_type).name

    def update_used_sound(
            self,
            sound_type: SoundType,
            name: str,
    ) -> None:
        """Update config.json with new name."""
        getattr(self.config, sound_type).name = name
        self._save_config()

    def is_sound_in_config(self, sound_name: str) -> bool:
        """Check is sound in config file if yes return True."""
        alarm = self.config.alarm.name == sound_name
        signal = self.config.signal.name == sound_name
        ambient = self.config.ambient.name == sound_name
        return alarm or signal or ambient

    def update_sound_name(self, old_name: str, new_name: str | None = None) -> None:
        """Update name to new if old in config."""
        if self.config.alarm.name == old_name:
            self.config.alarm.name = new_name or DEFAULT_ALARM_NAME

        if self.config.signal.name == old_name:
            self.config.signal.name = new_name or DEFAULT_SIGNAL_NAME

        if self.config.ambient.name == old_name:
            self.config.ambient.name = new_name or DEFAULT_AMBIENT_NAME

        self._save_config()

    def change_volume_value(
        self,
        volume_type: VolumeType,
        value: int,
    ) -> None:
        """Change volume value if type is not test it hast to get the attribute
        from the nested model.
        """
        if volume_type == "test_volume":
            if getattr(self.config, volume_type) == value:
                return
            self.config.test_volume = value
        else:
            sound_model = getattr(self.config, volume_type.split("_")[0])
            if sound_model.volume == value:
                return
            sound_model.volume = value

        self._save_config()

    def get_session_length(self) -> str:
        return self.config.session_length

    def update_session_length(self, new_length: str):
        self.config.session_length = new_length
        self._save_config()

    def _save_config(self) -> None:
        with Path(CONFIG_FILE_PATH).open("w") as file:
            json.dump(self.config.model_dump(), file, sort_keys=False)

    def get_time_input_mode(self) -> InputModeType:
        return self.config.input_mode_type

    def change_time_input_mode(self, new: InputModeType) -> None:
        self.config.input_mode_type = new
        self._save_config()

    def get_clock_display_hours(self) -> bool:
        return self.config.clock_display_hours

    def toggle_clock_display_hours(self) -> None:
        self.config.clock_display_hours = not self.config.clock_display_hours
        self._save_config()

    def get_clock_display_seconds(self) -> bool:
        return self.config.clock_display_seconds

    def toggle_clock_display_seconds(self) -> None:
        self.config.clock_display_seconds = not self.config.clock_display_seconds
        self._save_config()

class DatabaseManager:
    _instance = None

    def __new__(cls) -> "DatabaseManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        self.db_file = DB_FILE_PATH

    def db_setup(self) -> None:
        """Use only to set up DB on app initialization."""
        with connect(self.db_file) as con:
            # Setup Session table
            con.cursor().execute("""
                CREATE TABLE study_sessions(
                    id INTEGER PRIMARY KEY,
                    length INTEGER,
                    date DATE,
                    done BIT
                )
            """)
            con.commit()

    # def create_session_entry(self, length: int, is_successful: int) -> None:
    #     with connect(self.db_file) as con:
    #         con.cursor().execute("""
    #             INSERT INTO study_sessions(length, date, done)
    #             VALUES (?, ?, ?)
    #         """, (length, datetime.now(), is_successful),
    #                              )



class AboutSettings(Container):
    def compose(self) -> ComposeResult:
        yield Static("FocusTUI is your best buddy for working or studying.")
        yield Static("If you want to learn more, share your ideas, or report bugs...")
        yield Static("Check out our media!")
        with Grid(id="get-into-social"):
            yield Button("Discord", id="discord")
            yield Button("Github", id="github")
            yield Button("X", id="x")

    @on(Button.Pressed, "#discord")
    def discord_pressed(self) -> None:
        webbrowser.open(DISCORD_INVITATION)

    @on(Button.Pressed, "#github")
    def github_pressed(self) -> None:
        webbrowser.open(PROJECT_GITHUB)

    @on(Button.Pressed, "#x")
    def x_pressed(self) -> None:
        webbrowser.open(SIMONS_X_ACCOUNT)



def create_tooltip(volume_type: SoundType | Literal["test"]) -> str:
    """Return a tooltip string with volume_type interpolated."""
    return (
        f"Type value between {MIN_VOLUME_LEVEL} and {MAX_VOLUME_LEVEL}\nto "
        f"set {volume_type} volume."
    )


class SoundSettings(Grid):
    """SoundSettings allow user to change used sounds,
    test any sound and open EditSound modal.
    """

    def __init__(
        self,
        cm: "ConfigManager",
        sm: "SoundManager",
    ) -> None:
        super().__init__()
        self._cm = cm
        self._sm = sm

    def compose(self) -> ComposeResult:
        yield Select.from_values(
            self._sm.all_shorts_list,
            prompt=f"Alarm:{self._cm.get_sound_name("alarm")}",
            id="alarm",
        )
        yield SoundVolumeInput(
            value=str(self._cm.config.alarm.volume),
            tooltip=create_tooltip("alarm"),
            id="alarm_volume",
        )
        yield Button("Alarms\nSignals", id="short", classes="sound-edit-bt")
        yield Select.from_values(
            self._sm.all_shorts_list,
            prompt=f"Signal:{self._cm.get_sound_name("signal")}",
            id="signal",
        )
        yield SoundVolumeInput(
            value=str(self._cm.config.signal.volume),
            tooltip=create_tooltip("signal"),
            id="signal_volume",
        )
        yield Select.from_values(
            self._sm.all_longs_list,
            prompt=f"Ambient: {self._cm.get_sound_name("ambient")}",
            id="ambient",
        )
        yield SoundVolumeInput(
            value=str(self._cm.config.ambient.volume),
            tooltip=create_tooltip("ambient"),
            id="ambient_volume",
        )
        yield Button("Ambiences", id="long", classes="sound-edit-bt")
        yield Select.from_values(
            self._sm.all_sounds_list,
            prompt="Select to play sound",
            id="test-sound",
        )
        yield SoundVolumeInput(
            value=str(self._cm.config.test_volume),
            tooltip=create_tooltip("test"),
            id="test_volume",
        )
        yield Button(
            "Pause",
            variant="warning",
            id="test-sound-bt",
        )

    @on(Select.Changed)
    def select_changed(self, event: Select.Changed) -> None:
        """Change sound connected to type and update config."""
        # If button's id is 'test-sound' press blank or already chosen return
        if event.select.id == "test-sound" or event.value == Select.BLANK:
            return

        self._cm.update_used_sound(
            sound_type=cast(SoundType, event.select.id),
            name=event.value,
        )
        # Update song's name
        sound_type = event.control.id.capitalize()
        event.select.prompt = f"{sound_type}: {self._cm.config.alarm.name}"

    @on(Button.Pressed, ".sound-edit-bt")
    def open_edit_sound_popup(self, event: Button.Pressed) -> None:
        """Open Sounds Edit menu and refresh page if changes where applied."""
        async def recompose(arg) -> None:  # noqa: ARG001
            """Recompose."""
            await self.recompose()

        self.app.push_screen(
            EditSound(
                cast(LengthType, event.button.id),
                sm=self._sm,
                cm=self._cm,
            ),
            recompose,
        )

    @on(Select.Changed, "#test-sound")
    def test_sound(self, event: Select.Changed) -> None:
        """Play sound selected from list."""
        if event.value == Select.BLANK:
            return

        if event.value in self._sm.all_sounds_list:
            self._sm.play_sound(
                sound_name=event.value,
                sound_volume=self._cm.config.test_volume,
            )
            event.select.prompt = f"Last: {event.value}"
            event.select.clear()
        else:
            msg = "Sound is not in expected folder"
            raise FileNotFoundError(msg)

    @on(Button.Pressed, "#test-sound-bt")
    def stop_playing_sound(self) -> None:
        """Stop playing any sound."""
        self._sm.stop_sound()

    @on(SoundVolumeInput.Changed)
    def new_volume_submitted(self, event: SoundVolumeInput.Submitted) -> None:
        if event.value == "":
            return

        if not MIN_VOLUME_LEVEL <= int(event.value) <= MAX_VOLUME_LEVEL:
            return

        _type = cast(VolumeType, event.input.id)
        value = int(event.input.value)
        self._cm.change_volume_value(_type, value)



class ClockDisplay(Horizontal):
    """Display time."""

    def __init__(self, cm: "ConfigManager", *args: tuple, **kwargs: dict) -> None:
        super().__init__(*args, **kwargs)
        self._cm = cm

        if self._cm.get_clock_display_hours():
            self._ones_hour = Static(NUMBERS_DICT["0"], classes="clock-digit")
            self._hour_separator = Static(
                NUMBERS_DICT[":"],
                classes="clock-digit",
            )
        else:
            self._ones_hour = Static("", classes="clock-digit")
            self._hour_separator = Static("", classes="clock-digit")

        self._hundreds_min = Static("", classes="clock-digit")
        self._tens_min = Static(NUMBERS_DICT["0"], classes="clock-digit")
        self._ones_min = Static(NUMBERS_DICT["0"], classes="clock-digit")

        if self._cm.get_clock_display_seconds():
            self._sec_separator = Static(NUMBERS_DICT[":"], classes="clock-digit")
            self._tens_sec = Static(NUMBERS_DICT["0"], classes="clock-digit")
            self._ones_sec = Static(NUMBERS_DICT["0"], classes="clock-digit")
        else:
            self._sec_separator = Static("", classes="clock-digit")
            self._tens_sec = Static("", classes="clock-digit")
            self._ones_sec = Static("", classes="clock-digit")

    def compose(self) -> ComposeResult:
        yield self._ones_hour
        yield Label(" ")
        yield self._hour_separator
        yield self._hundreds_min
        yield Label(" ")
        yield self._tens_min
        yield Label(" ")
        yield self._ones_min
        yield Label(" ")
        yield self._sec_separator
        yield Label(" ")
        yield self._tens_sec
        yield Label(" ")
        yield self._ones_sec

    def update_time(self, minutes: str, seconds: str) -> None:
        if self._cm.get_clock_display_hours():
            self.update_hour_mode(minutes)
        else:
            self.update_minute_mode(minutes)

        self._update_seconds(seconds)

    def update_minute_mode(self, minutes: str):
        """Update clock number."""
        hundreds_length: int = 2
        tens_length: int = 1

        self._ones_hour.update("")
        self._hour_separator.update("")

        if len(minutes) > hundreds_length:
            self._hundreds_min.update(NUMBERS_DICT[minutes[-3]])
        else:
            self._hundreds_min.update("")

        if len(minutes) > tens_length:
            self._tens_min.update(NUMBERS_DICT[minutes[-2]])
        else:
            self._tens_min.update("")

        self._ones_min.update(NUMBERS_DICT[minutes[-1]])

    def update_hour_mode(self, minutes: str):
        hours, minutes = divmod(int(minutes), 60)
        minutes = str(minutes)
        tens_length: int = 1

        self._ones_hour.update(NUMBERS_DICT[str(hours)])
        self._hour_separator.update(NUMBERS_DICT[":"])
        self._hundreds_min.update("")

        if len(minutes) > tens_length:
            self._tens_min.update(NUMBERS_DICT[minutes[-2]])
        else:
            self._tens_min.update(NUMBERS_DICT["0"])

        self._ones_min.update(NUMBERS_DICT[minutes[-1]])

    def _update_seconds(self, seconds: str) -> None:
        if self._cm.get_clock_display_seconds():
            self._sec_separator.update(NUMBERS_DICT[":"])
            self._tens_sec.update(NUMBERS_DICT[seconds[0]])
            self._ones_sec.update(NUMBERS_DICT[seconds[1]])
        else:
            self._sec_separator.update("")
            self._tens_sec.update("")
            self._ones_sec.update("")


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

class MusicDirectoryTree(DirectoryTree):
    show_root = False

    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        def not_hidden(path: Path) -> bool:
            return path.is_dir() and not path.name.startswith(".")

        suffixes = {".wav", ".mp3", ".ogg", ".flac", ".opus", "/"}
        return [path for path in paths if not_hidden(path) or path.suffix in suffixes]

class Accordion(Container):
    """Accordion class is a container for Collapsibles
    that turns them into Accordion.
    """

    def __init__(
        self,
        *children: Widget,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(
            *children, name=name, id=id, classes=classes, disabled=disabled,
        )
        self._currently_expanded: Collapsible | None = None

    @on(Collapsible.Expanded)
    def collapse_other_expanded(self, event: Collapsible.Expanded) -> None:
        """Close last when new clicked."""
        if self._currently_expanded is event.collapsible:
            self._currently_expanded.collapsed = False
        elif self._currently_expanded is not None:
            self._currently_expanded.collapsed = True
        self._currently_expanded = event.collapsible


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





class ConfirmPopup(ModalScreen[bool]):
    """ModalScreen to ask user for confirmation of certain action."""

    def __init__(self, *args: tuple, message: str, **kwargs: dict) -> None:
        super().__init__(*args, **kwargs)
        self.message = message

    def compose(self) -> ComposeResult:
        with Container(id="confirm-popup-body"):
            yield Static(self.message, id="confirm-popup-message")
            with Horizontal(id="confirm-popup-buttons"):
                yield Button("No", variant="error", id="no-button")
                yield Button("Yes", variant="success", id="yes-button")

    @on(Button.Pressed, "#no-button")
    def reject(self) -> None:
        """Return False to callback."""
        self.dismiss(False)

    @on(Button.Pressed, "#yes-button")
    def confirm(self) -> None:
        """Return True to callback."""
        self.dismiss(True)




ACTIONS_NOT_ALLOWED_ON_IDLE = (
    "play_ambient",
    "stop_ambient",
    "toggle_hours",
    "toggle_seconds",
)


class FocusScreen(Screen):
    _ambient_silent = reactive(True, bindings=True)
    _input_mode = reactive("PLACEHOLDER", bindings=True)

    BINDINGS = [
        ("ctrl+q", "quit_app", "Quit App"),
        ("ctrl+s", "open_settings", "Settings"),
        ("ctrl+a", "play_ambient", "Play Ambient"),
        ("ctrl+a", "stop_ambient", "Stop Ambient"),
        ("ctrl+e", "toggle_hours", "Toggle Hours"),
        ("ctrl+r", "toggle_seconds", "Toggle Seconds"),
    ]

    def action_quit_app(self) -> None:
        self.app.exit()

    def action_open_settings(self) -> None:
        """Open settings screen."""
        self.app.open_settings()

    def action_play_ambient(self):
        self._ambient_silent = False
        self._sm.toggle_ambient(
            self._ambient_silent,
            self._cm.config.ambient.volume,
        )

    def action_stop_ambient(self):
        self._ambient_silent = True
        self._sm.toggle_ambient(
            self._ambient_silent,
            self._cm.config.ambient.volume,
        )

    def action_toggle_hours(self):
        self._cm.toggle_clock_display_hours()

    def action_toggle_seconds(self):
        self._cm.toggle_clock_display_seconds()

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:  # noqa: PLR0911
        """If clock is active allow to toggle ambient and hide rest."""
        if self._active_session and action not in ACTIONS_NOT_ALLOWED_ON_IDLE:
            return False

        if action in ("play_ambient", "stop_ambient") and not self._active_session:
            return False
        if action == "play_ambient" and self._ambient_silent:
            return True
        if action == "stop_ambient" and not self._ambient_silent:
            return True

        if action in ("toggle_hours", "toggle_seconds") and not self._active_session:
            return False
        if action in ("toggle_hours", "toggle_seconds"):
            return True

        return not self._active_session

    def __init__(
        self,
        cm: "ConfigManager",
        db: "DatabaseManager",
        sm: "SoundManager",
    ) -> None:
        super().__init__()
        self._cm = cm
        self._db = db
        self._sm = sm
        self._session_len_input = SessionLenInput(cm=self._cm)
        self._clock_display = ClockDisplay(cm=self._cm)
        self._focus_button = Button("Focus", variant="success", id="focus-bt")
        self._active_session = False
        self._session_len: int = session_len_parser(self._cm.get_session_length())
        self._remaining_session: int = 0
        self._cancel_session_remaining: int = MINUTE
        self._intervals = []
        self._mode: Literal["stopwatch", "timer"] | None = None
        self._min_length: int = MIN_SESSION_LEN * MINUTE
        self._input_mode = self._cm.get_time_input_mode()

    def compose(self):
        with Horizontal(id="clock-wrapper"):
            yield self._clock_display
        with Vertical(id="focus-wrapper"):
            yield self._session_len_input
            yield self._focus_button
        yield Footer()

    @on(Button.Pressed, "#focus-bt")
    def _focus_button_clicked(self) -> None:
        """Start, Cancel, Kill session."""
        if self._focus_button.variant == "success":
            self._start_session()
        elif self._focus_button.variant == "warning":
            self._reset_timer()
        elif self._mode == "timer" or self._session_len < self._min_length:
            popup = ConfirmPopup(message="Do you want to kill the session?")
            self.app.push_screen(popup, self._not_successful_session)
        else:
            self._successful_session()

    @on(Input.Changed, "#session-duration")
    def _is_valid_session_length(self, event: Input.Changed) -> None:
        """If the session duration is not correct block start button."""
        is_valid: bool = event.input.is_valid
        self._focus_button.disabled = not is_valid
        if is_valid:
            self._cm.update_session_length(
                self._session_len_input.value,
            )

    def _start_session(self) -> None:
        """Start a Timer session."""
        self._active_session = True
        self._session_len_input.visible = False
        self._session_len = self._session_len_input.to_int() * MINUTE
        self._mode = "stopwatch" if self._session_len == 0 else "timer"
        if self._mode == "timer":
            self._remaining_session = self._session_len
            update_clock = self.set_interval(1, self._timer_display_update)
        else:
            update_clock = self.set_interval(1, self._stopwatch_display_update)

        cancel_session = self.set_interval(1, self._cancel_session)
        self._intervals.extend([update_clock, cancel_session])
        self._focus_button.variant = "warning"
        self._sm.play_ambient_in_background(
            ambient_name=self._cm.config.ambient.name,
        )
        self.app.refresh_bindings()  # Deactivates Bindings

    def _timer_display_update(self) -> None:
        """Update variable used by timer, update displayed time and
        call `TimerScreen._successful_session()` when self._remaining_session == 0.
        """
        self._remaining_session -= 1
        if self._remaining_session == 0:
            self._successful_session()
        else:
            minutes, seconds = divmod(self._remaining_session, 60)
            minutes_str = str(minutes).zfill(1)
            seconds_str = str(seconds).zfill(2)
            self._clock_display.update_time(minutes_str, seconds_str)

    def _stopwatch_display_update(self) -> None:
        """Update variable used by timer and update displayed time."""
        self._session_len += 1
        minutes, seconds = divmod(self._session_len, 60)
        minutes_str = str(minutes).zfill(1)
        seconds_str = str(seconds).zfill(2)
        self._clock_display.update_time(minutes_str, seconds_str)

    def _successful_session(self) -> None:
        """Play song, add successful session to DB and reset clock."""
        # self._db.create_session_entry(self._session_len // 60, 1)  # noqa: ERA001
        self._reset_timer()
        alarm = self._cm.config.alarm
        self._sm.play_sound(
            sound_name=alarm.name,
            sound_volume=alarm.volume,
        )

    def _not_successful_session(self, should_kill: bool) -> None:
        """Add killed session to DB and reset clock."""
        if not should_kill:
            return

        focused_for = (self._session_len - self._remaining_session) // MINUTE  # noqa: F841
        # self._db.create_session_entry(focused_for, 0)  # noqa: ERA001
        self._reset_timer()

    def _reset_timer(self) -> None:
        """Set all clock properties to default."""
        self._active_session = False
        self._session_len_input.visible = True
        self._session_len = self._cm.get_session_length()
        self._cancel_session_remaining = MINUTE
        for interval in self._intervals:
            interval.stop()
        self._intervals.clear()
        self._clock_display.update_time("0", "00")
        self._focus_button.variant = "success"
        self._focus_button.label = "Focus"
        self._ambient_silent = True
        self._sm.stop_ambient()
        self.app.refresh_bindings()

    def _cancel_session(self) -> None:
        """Allow user to cancel timer in first
        `self._cancel_timer_counter_default` seconds.
        """
        self._cancel_session_remaining -= 1
        if self._cancel_session_remaining > 0:
            self._focus_button.label = f"Cancel ({self._cancel_session_remaining})"
        elif self._mode == "timer" or (
                self._mode == "stopwatch" and self._session_len < self._min_length
        ):
            self._focus_button.label = "Kill"
            self._focus_button.variant = "error"
        else:
            self._focus_button.label = "End"
            self._focus_button.variant = "error"


class SettingsScreen(Screen):
    TITLE = "Settings"
    BINDINGS = [
        ("ctrl+q", "quit_app", "Quit App"),
        ("escape", "close_settings", "Close Settings"),
    ]

    def action_quit_app(self) -> None:
        self.app.exit()

    def action_close_settings(self) -> None:
        """Return anything to run callback."""
        self._sm.stop_sound()
        self.app.open_focus()

    def __init__(
            self,
            cm: "ConfigManager",
            sm: "SoundManager",
    ) -> None:
        super().__init__()
        self._cm = cm
        self._sm = sm

        self.account_settings_border = Static(classes="settings-section")
        self.account_settings_border.border_title = "Account"

        self.social_settings_border = Static(classes="settings-section")
        self.social_settings_border.border_title = "Social"

        self.sound_settings_border = Static(classes="settings-section")
        self.sound_settings_border.border_title = "Sound"

        self.theme_settings_border = Static(classes="settings-section")
        self.theme_settings_border.border_title = "Theme"

        self.theme_store_settings_border = Static(classes="settings-section")
        self.theme_store_settings_border.border_title = "Theme Store"

        self.about = Static(classes="settings-section")
        self.about.border_title = "About"

    def compose(self) -> ComposeResult:
        with VerticalScroll(id="settings-wrapper"):
            with Container(id="settings-body"):
                with self.account_settings_border:
                    yield Button("PLACEHOLDER")
                with self.social_settings_border:
                    yield Button("PLACEHOLDER")
                with self.sound_settings_border:
                    yield SoundSettings(cm=self._cm, sm=self._sm)
                with self.theme_settings_border:
                    yield Button("PLACEHOLDER")
                with self.theme_store_settings_border:
                    yield Button("PLACEHOLDER")
                with self.about:
                    yield AboutSettings()
        yield Footer()


class FocusTUI(App, inherit_bindings=False):
    ENABLE_COMMAND_PALETTE = False
    CSS_PATH = "style.tcss"

    def __init__(
            self,
            db: "DatabaseManager",
            cm: "ConfigManager",
            sm: "SoundManager",
    ) -> None:
        super().__init__()
        self._db = db
        self._cm = cm
        self._sm = sm

        pygame.init()

    def on_mount(self):
        self.push_screen(FocusScreen(cm=self._cm, db=self._db, sm=self._sm))

    def open_settings(self):
        """Switch to settings screen."""
        self.switch_screen(SettingsScreen(cm=self._cm, sm=self._sm))

    def open_focus(self):
        """Switch to focus screen."""
        self.switch_screen(FocusScreen(cm=self._cm, db=self._db, sm=self._sm))


class SoundFileManager:
    """Manages sound files bundled with the application.

    This class provides methods to access the paths of short and long sound files
    stored within the package. It is primarily used to copy these sound files
    to the appropriate directories on the user's PC.
    """

    current_dir: Path = Path(__file__).parent
    sounds: Path = current_dir / "static" / "sounds"
    longs: Path = sounds / "longs"
    shorts: Path = sounds / "shorts"

    def get_shorts(self) -> list[Path]:
        """Return list of shorts paths."""
        return list(self.shorts.glob("*"))

    def get_longs(self) -> list[Path]:
        """Return list of longs paths."""
        return list(self.longs.glob("*"))



def _create_dir_if_not_exist(path: Path) -> None:
    if not path.exists():
        # Create app directory
        path.mkdir()


def setup_app() -> None:
    """Create app folder with all subfolder and files."""
    sfm = SoundFileManager()
    db = DatabaseManager()

    _create_dir_if_not_exist(MAIN_DIR_PATH)
    _create_dir_if_not_exist(THEMES_PATH)
    _create_dir_if_not_exist(QUEUES_PATH)
    _create_dir_if_not_exist(SOUNDS_PATH)
    if not SHORTS_PATH.exists():
        # Create shorts folder
        SHORTS_PATH.mkdir()
        for sound in sfm.get_shorts():
            shutil.copy(sound, SHORTS_PATH)

    if not LONGS_PATH.exists():
        # Create longs folder
        LONGS_PATH.mkdir()
        for sound in sfm.get_longs():
            shutil.copy(sound, LONGS_PATH)

    # if not DB_FILE_PATH.exists():
    # Create SQLite database file
    # Path(DB_FILE_PATH).touch()  # noqa: ERA001
    # This is the only place where
    # this methods should be used
    # db.db_setup()  # noqa: ERA001

    if not CONFIG_FILE_PATH.exists():
        # Create config.json file
        Path(CONFIG_FILE_PATH).touch()
        with Path(CONFIG_FILE_PATH).open("w") as file:
            json_config = json.loads(ConfigModel().model_dump_json())
            json.dump(json_config, file, sort_keys=False, indent=4)


_paths = {
    "db": DB_FILE_PATH,
    "config": CONFIG_FILE_PATH,
    "themes": THEMES_PATH,
    "queues": QUEUES_PATH,
    "shorts": SHORTS_PATH,
    "longs": LONGS_PATH,
}


@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx) -> None:
    """Start app."""
    if ctx.invoked_subcommand is None:
        # Prevent app start on command use
        setup_app()
        FocusTUI(
            db=DatabaseManager(),
            cm=ConfigManager(),
            sm=SoundManager(),
        ).run()


def echo_path(path: Path) -> None:
    """Print given resource path."""
    echo(style("Path: ", "green") + str(path))


@main.command()
@click.argument("what", type=Choice(list(_paths.keys())))
def locate(what: str) -> None:
    """Help you find location of a needed resource used by the app."""
    echo_path(_paths[what])


