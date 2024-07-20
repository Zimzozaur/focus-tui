from pathlib import Path
from platformdirs import user_data_dir


class AppPaths:
    """Class that provides all paths"""
    # Root
    main_dir_path: Path = Path(user_data_dir()) / ".Focus-Keeper"

    # App paths
    app_data_path = main_dir_path / ".app_data"
    sounds_path = app_data_path / "sounds"
    ambiences_path = app_data_path / "ambiences"

    # User paths
    user_data_path = main_dir_path / "user_data"
    user_sounds_path = user_data_path / "user_sounds"
    user_ambiences_path = user_data_path / "user_ambiences"

    # Files
    db_file_path = app_data_path / "focus_keeper.db"
    config_file_path = app_data_path / "config.yaml"

    # Default Sounds
    default_alarm_name = 'Unfa_Woohoo.mp3'
    default_signal_name = 'Unfa_Landing.mp3'
    default_ambient_name = 'Woodpecker_Forest.flac'
