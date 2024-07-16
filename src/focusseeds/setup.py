import shutil
from pathlib import Path

from platformdirs import user_data_dir

from focusseeds.db import DatabaseManager
from fake_api_client import FakeAPIClient


class AppSetup:
    def __init__(self):
        # Paths
        self.main_dir: Path = Path(user_data_dir()) / "Focus-Seeds"
        self.app_data = self.main_dir / "app_data"
        self.user_data = self.main_dir / "user_data"
        self.sounds = self.app_data / "sounds"
        self.ambiences = self.app_data / "ambiences"
        self.db_file = self.app_data / "focus_seeds.db"

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

        # Create directory for app users
        if not self.user_data.exists():
            print('Creating user_data folder')
            self.user_data.mkdir()

        # TODO: download sounds


