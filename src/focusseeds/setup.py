import shutil
from pathlib import Path

import yaml

from focusseeds.db import DatabaseManager
from focusseeds.fake_api_client import FakeAPIClient
from focusseeds.config import AppPaths


class AppSetup(AppPaths):
    def __init__(self):
        super().__init__()
        self.fake_api = FakeAPIClient()
        self.db = DatabaseManager()

    def setup_app(self):
        # Create app directory
        if not self.main_dir.exists():
            print('Creating Focus-Seeds folder')
            self.main_dir.mkdir()

        # Create directory app usage
        if not self.app_data.exists():
            print('Creating app_data folder')
            self.app_data.mkdir()

        # Create inner structure
        if not self.sounds.exists():
            self.sounds.mkdir()
            print('Creating sounds folder')
            for song in self.fake_api.get_songs():
                shutil.copy(song, self.sounds)
                print('Copying:', song)

        if not self.ambiences.exists():
            print('Creating ambiences folder')
            self.ambiences.mkdir()

        # Create SQLite database file (empty for now)
        if not self.db_file.exists():
            print('Creating focus_seeds.db file')
            Path(self.db_file).touch()
            with open(self.db_file, 'w'):
                # This is the only place where
                # this methods should be used
                self.db.db_setup()

        # Create config.yaml file
        if not self.config_file.exists():
            print('Creating config.yaml file')
            Path(self.config_file).touch()
            # This is the only place where
            # this methods should be used
            self.config_setup()

        # Create directory for app users
        if not self.user_data.exists():
            print('Creating user_data folder')
            self.user_data.mkdir()

        # Create directory for user sounds
        if not self.user_sounds.exists():
            print('Creating user_sounds folder')
            self.user_sounds.mkdir()

        # Create directory for user ambiences
        if not self.user_ambiences.exists():
            print('Creating user_ambiences folder')
            self.user_ambiences.mkdir()

        # TODO: download sounds

    def config_setup(self):
        """Method used only to set up CONFIG on app initialization"""
        default_config = {
            'used_sounds': {
                'alarm': {
                    'name': 'Unfa_Woohoo.mp3',
                    'path': f'{self.sounds}'
                },
                'signal': {
                    'name': 'Unfa_Braam.mp3',
                    'path': f'{self.sounds}'
                },
                'ambient': {
                    'name': 'Auntie_Cleo_s.mp3',
                    'path': f'{self.ambiences}'
                }
            }
        }
        with open(self.config_file, 'w') as file:
            yaml.dump(default_config, file, sort_keys=False)

