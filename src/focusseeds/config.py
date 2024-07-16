from typing import Literal

import yaml
from pathlib import Path
from platformdirs import user_data_dir


class AppPaths:
    def __init__(self):
        # Root
        self.main_dir: Path = Path(user_data_dir()) / "Focus-Seeds"
        # App paths
        self.app_data = self.main_dir / "app_data"
        self.sounds = self.app_data / "sounds"
        self.ambiences = self.app_data / "ambiences"
        # User paths
        self.user_data = self.main_dir / "user_data"
        self.user_sounds = self.user_data / "user_sounds"
        self.user_ambiences = self.user_data / "user_ambiences"
        # Files
        self.db_file = self.app_data / "focus_seeds.db"
        self.config_file = self.app_data / "config.yaml"


class AppConfig(AppPaths):
    def get_used_sound(
            self,
            sound_type: Literal['alarm', 'signal', 'ambient']
    ) -> dict:
        """Get from config.yaml name and path of chosen sound_type"""
        with open(self.config_file, 'r') as file:
            return yaml.safe_load(file)['used_sounds'][sound_type]

    def update_used_sound(
            self,
            sound_type: Literal['alarm', 'signal', 'ambient'],
            name: str,
            path: str
    ) -> None:
        """Update config.yaml with sound name and path"""
        with open(self.config_file) as file:
            yaml_file = yaml.safe_load(file)

        yaml_file['used_sounds'][sound_type]['name'] = name
        yaml_file['used_sounds'][sound_type]['path'] = path

        with open(self.config_file, 'w') as file:
            yaml.dump(yaml_file, file, sort_keys=False)
