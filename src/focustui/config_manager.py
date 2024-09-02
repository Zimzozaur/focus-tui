import json
from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, Field, field_validator

from focustui.constants import (
    CONFIG_FILE_PATH,
    DEFAULT_ALARM_NAME,
    DEFAULT_AMBIENT_NAME,
    DEFAULT_SESSION_LEN,
    DEFAULT_SIGNAL_NAME,
    DEFAULT_SOUND_VOLUME,
    MAX_SESSION_LEN,
    MAX_VOLUME_LEVEL,
    MIN_SESSION_LEN,
    MIN_VOLUME_LEVEL,
    SoundType,
    VolumeType,
)

SoundVolume = Annotated[
    int, Field(
        ge=MIN_VOLUME_LEVEL,
        le=MAX_VOLUME_LEVEL,
        default=DEFAULT_SOUND_VOLUME),
]
SessionLength = Annotated[
    int, Field(ge=MIN_SESSION_LEN, le=MAX_SESSION_LEN, default=DEFAULT_SESSION_LEN),
]


class _SoundModel(BaseModel):
    name: str
    volume: SoundVolume

    @field_validator("name")
    def validate_name(cls, string: str) -> str:
        for char in string:
            if not (char.isalpha() or char.isdigit() or char in {"_", "-", "'"}):
                msg = ("Only letters, numbers, underscore, "
                       "dash or apostrophe are allowed in sound name")
                raise ValueError(msg)
        return string


class AlarmModel(_SoundModel):
    name: str = DEFAULT_ALARM_NAME


class SignalModel(_SoundModel):
    name: str = DEFAULT_SIGNAL_NAME


class AmbientModel(_SoundModel):
    name: str = DEFAULT_AMBIENT_NAME


class ConfigModel(BaseModel):
    alarm: AlarmModel = AlarmModel()
    signal: SignalModel = SignalModel()
    ambient: AmbientModel = AmbientModel()
    session_length: int = Field(
        ge=MIN_SESSION_LEN, le=MAX_SESSION_LEN, default=DEFAULT_SESSION_LEN,
    )
    test_volume: SoundVolume = DEFAULT_SOUND_VOLUME


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

    def get_used_sound(self, sound_type: SoundType) -> str:
        """Get from config.json name of chosen sound_type."""
        return getattr(self.config, sound_type).name

    def update_used_sound(
        self,
        sound_type: SoundType,
        name: str,
    ) -> None:
        """Update config.yaml with sound name and path."""
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

    def get_session_length(self) -> int:
        return self.config.session_length

    def update_session_length(self, new_length: int):
        self.config.session_length = new_length
        self._save_config()

    def _save_config(self) -> None:
        with Path(CONFIG_FILE_PATH).open("w") as file:
            json.dump(self.config.model_dump(), file, sort_keys=False)
