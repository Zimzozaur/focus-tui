import json
from pathlib import Path

from pydantic import BaseModel

from focustui.constants import (
    CONFIG_FILE_PATH,
    DEFAULT_ALARM_NAME,
    DEFAULT_AMBIENT_NAME,
    DEFAULT_SIGNAL_NAME,
    SoundType,
    VolumeType,
)

"""
I want on app init map config.json
Turn it into models and operate on models
"""


class SoundModel(BaseModel):
    # TODO: Add validation
    name: str


class ConfigModel(BaseModel):
    alarm: SoundModel
    signal: SoundModel
    ambient: SoundModel
    alarm_volume: int
    signal_volume: int
    ambient_volume: int
    test_volume: int
    session_length: int


class ConfigManager:
    _instance = None

    def __new__(cls) -> "ConfigManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        with Path(CONFIG_FILE_PATH).open() as file:
            self.config: ConfigModel = ConfigModel.model_validate(json.load(file))

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
        setattr(self.config, volume_type, value)
        self._save_config()

    def get_session_length(self) -> int:
        return self.config.session_length

    def update_session_length(self, new_length: int):
        self.config.session_length = new_length
        self._save_config()

    def _save_config(self) -> None:
        with Path(CONFIG_FILE_PATH).open("w") as file:
            json.dump(self.config.model_dump(), file, sort_keys=False)
