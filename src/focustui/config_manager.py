import json
from pathlib import Path

from pydantic import BaseModel, ConfigDict, field_validator

from focustui.constants import (
    CONFIG_FILE_PATH,
    DEFAULT_ALARM_NAME,
    DEFAULT_AMBIENT_NAME,
    DEFAULT_CLOCK_DISPLAY_HOURS,
    DEFAULT_CLOCK_DISPLAY_SECONDS,
    DEFAULT_SESSION_LEN,
    DEFAULT_SIGNAL_NAME,
    DEFAULT_SOUND_VOLUME,
    DEFAULT_TIME_INPUT_TYPE,
    MAX_VOLUME_LEVEL,
    MIN_VOLUME_LEVEL,
    InputModeType,
    SoundType,
    VolumeType,
)
from focustui.utils import session_len_parser


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
