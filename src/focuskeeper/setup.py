import shutil
from pathlib import Path

import yaml

from focuskeeper.db import DatabaseManager
from focuskeeper.fake_api_client import FakeAPIClient
from focuskeeper.config import AppPaths
from focuskeeper.settings import (
    DEFAULT_ALARM_NAME,
    DEFAULT_SIGNAL_NAME,
    DEFAULT_AMBIENT_NAME
)


class AppSetup(AppPaths):
    def __init__(self):
        super().__init__()
        self.fake_api = FakeAPIClient()
        self.db = DatabaseManager()

    def setup_app(self):
        # Create app directory
        if not self.main_dir_path.exists():
            print('Creating .Focus-Keeper folder')
            self.main_dir_path.mkdir()

        # Create directory app usage
        if not self.app_data_path.exists():
            print('Creating .app_data folder')
            self.app_data_path.mkdir()

        # Create inner structure
        if not self.sounds_path.exists():
            self.sounds_path.mkdir()
            print('Creating sounds folder')
            for song in self.fake_api.get_songs():
                shutil.copy(song, self.sounds_path)
                print('Copying:', song)

        if not self.ambiences_path.exists():
            print('Creating ambiences folder')
            self.ambiences_path.mkdir()

        # Create SQLite database file (empty for now)
        if not self.db_file_path.exists():
            print('Creating focus_keeper.db file')
            Path(self.db_file_path).touch()
            with open(self.db_file_path, 'w'):
                # This is the only place where
                # this methods should be used
                self.db.db_setup()

        # Create config.yaml file
        if not self.config_file_path.exists():
            print('Creating config.yaml file')
            Path(self.config_file_path).touch()
            # This is the only place where
            # this methods should be used
            self.config_setup()

        # Create directory for app users
        if not self.user_data_path.exists():
            print('Creating user_data folder')
            self.user_data_path.mkdir()

        # Create directory for user sounds
        if not self.user_sounds_path.exists():
            print('Creating user_sounds folder')
            self.user_sounds_path.mkdir()

        # Create directory for user ambiences
        if not self.user_ambiences_path.exists():
            print('Creating user_ambiences folder')
            self.user_ambiences_path.mkdir()

        # TODO: download sounds

    def config_setup(self):
        """Method used only to set up CONFIG on app initialization"""
        default_config = {
            'used_sounds': {
                'alarm': {
                    'name': DEFAULT_ALARM_NAME,
                },
                'signal': {
                    'name': DEFAULT_SIGNAL_NAME,
                },
                'ambient': {
                    'name': DEFAULT_AMBIENT_NAME,
                }
            }
        }
        with open(self.config_file_path, 'w') as file:
            yaml.dump(default_config, file, sort_keys=False)

