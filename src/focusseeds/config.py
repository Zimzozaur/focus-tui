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
        # DB
        self.db_file = self.app_data / "focus_seeds.db"

