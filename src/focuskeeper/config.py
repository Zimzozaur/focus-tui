import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from focuskeeper.constants import (
    CONFIG_FILE_PATH,
    DEFAULT_ALARM_NAME,
    DEFAULT_AMBIENT_NAME,
    DEFAULT_SIGNAL_NAME,
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


class ConfigManager:
    _instance = None

    def __new__(cls) -> "ConfigManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        with open(CONFIG_FILE_PATH) as file:
            self.config: ConfigModel = ConfigModel.model_validate(json.load(file))

    def get_used_sound(self, sound_type: Literal["alarm", "signal", "ambient"]) -> str:
        """Get from config.json name of chosen sound_type."""
        return getattr(self.config, sound_type).name

    def update_used_sound(
        self,
        sound_type: Literal["alarm", "signal", "ambient"],
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

    def _save_config(self):
        with Path(CONFIG_FILE_PATH).open("w") as file:
            json.dump(self.config.model_dump(), file, sort_keys=False)


