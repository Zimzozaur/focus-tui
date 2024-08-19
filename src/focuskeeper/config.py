from typing import Literal

import yaml

from focuskeeper.constants import (
    CONFIG_FILE_PATH,
    DEFAULT_ALARM_NAME,
    DEFAULT_AMBIENT_NAME,
    DEFAULT_SIGNAL_NAME,
)


def get_used_sound(sound_type: Literal["alarm", "signal", "ambient"]) -> str:
    """Get from config.yaml name of chosen sound_type"""
    with open(CONFIG_FILE_PATH) as file:
        return yaml.safe_load(file)["used_sounds"][sound_type]["name"]


def update_used_sound(
    sound_type: Literal["alarm", "signal", "ambient"],
    name: str,
) -> None:
    """Update config.yaml with sound name and path"""
    with open(CONFIG_FILE_PATH) as file:
        yaml_file = yaml.safe_load(file)

    yaml_file["used_sounds"][sound_type]["name"] = name

    with open(CONFIG_FILE_PATH, "w") as file:
        yaml.dump(yaml_file, file, sort_keys=False)


def is_sound_in_config(sound_name: str) -> bool:
    """Check is sound in config file if yes return True"""
    with open(CONFIG_FILE_PATH) as file:
        yaml_file = yaml.safe_load(file)
        alarm = yaml_file["used_sounds"]["alarm"]["name"] == sound_name
        signal = yaml_file["used_sounds"]["signal"]["name"] == sound_name
        ambient = yaml_file["used_sounds"]["ambient"]["name"] == sound_name
        return alarm or signal or ambient


def update_sound_name(old_name: str, new_name: str | None = None) -> None:
    """Update name to new if old in config"""
    with open(CONFIG_FILE_PATH) as file:
        yaml_file = yaml.safe_load(file)

    if yaml_file["used_sounds"]["alarm"]["name"] == old_name:
        yaml_file["used_sounds"]["alarm"]["name"] = new_name or DEFAULT_ALARM_NAME

    if yaml_file["used_sounds"]["signal"]["name"] == old_name:
        yaml_file["used_sounds"]["signal"]["name"] = new_name or DEFAULT_SIGNAL_NAME

    if yaml_file["used_sounds"]["ambient"]["name"] == old_name:
        yaml_file["used_sounds"]["ambient"]["name"] = new_name or DEFAULT_AMBIENT_NAME

    with open(CONFIG_FILE_PATH, "w") as file:
        yaml.dump(yaml_file, file, sort_keys=False)
