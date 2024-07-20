from typing import Literal

import yaml

from focuskeeper.app_paths import AppPaths
from focuskeeper.setup import (
    DEFAULT_ALARM_NAME, DEFAULT_SIGNAL_NAME, DEFAULT_AMBIENT_NAME
)


class AppConfig(AppPaths):
    """Class used to manage config.yaml"""

    def forbiden_sound_names(self) -> set:
        """Return set of names that are used by app
        and user is not allowed to use
        """
        return {
            'Unfa_Woohoo', 'Unfa_Landing',
            'Unfa_Braam', 'Unfa_Acid_Bassline',
            'Woodpecker_Forest', 'Mexican_Forest',
        }

    def get_used_sound(
            self,
            sound_type: Literal['alarm', 'signal', 'ambient']
    ) -> str:
        """Get from config.yaml name of chosen sound_type"""
        with open(self.config_file_path, 'r') as file:
            return yaml.safe_load(file)['used_sounds'][sound_type]['name']

    def update_used_sound(
            self,
            sound_type: Literal['alarm', 'signal', 'ambient'],
            name: str,
    ) -> None:
        """Update config.yaml with sound name and path"""
        with open(self.config_file_path) as file:
            yaml_file = yaml.safe_load(file)

        yaml_file['used_sounds'][sound_type]['name'] = name

        with open(self.config_file_path, 'w') as file:
            yaml.dump(yaml_file, file, sort_keys=False)

    def is_sound_in_config(self, sound_name: str) -> bool:
        """Check is sound in config file if yes return True"""
        with open(self.config_file_path) as file:
            yaml_file = yaml.safe_load(file)
            alarm = yaml_file['used_sounds']['alarm']['name'] == sound_name
            signal = yaml_file['used_sounds']['signal']['name'] == sound_name
            ambient = yaml_file['used_sounds']['ambient']['name'] == sound_name
            return alarm or signal or ambient

    def update_sound_name(self, old_name: str, new_name: str | None = None) -> None:
        """Update name to new if old in config"""
        with open(self.config_file_path) as file:
            yaml_file = yaml.safe_load(file)

        if yaml_file['used_sounds']['alarm']['name'] == old_name:
            yaml_file['used_sounds']['alarm']['name'] = new_name or DEFAULT_ALARM_NAME

        if yaml_file['used_sounds']['signal']['name'] == old_name:
            yaml_file['used_sounds']['signal']['name'] = new_name or DEFAULT_SIGNAL_NAME

        if yaml_file['used_sounds']['ambient']['name'] == old_name:
            yaml_file['used_sounds']['ambient']['name'] = new_name or DEFAULT_AMBIENT_NAME

        with open(self.config_file_path, 'w') as file:
            yaml.dump(yaml_file, file, sort_keys=False)


