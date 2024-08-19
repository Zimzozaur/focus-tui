from pathlib import Path

from platformdirs import user_data_dir


class AppPaths:
    """Class that provides all paths"""

    # Root
    main_dir_path: Path = Path(user_data_dir()) / "focus-keeper"

    # Sounds path
    sounds_path = main_dir_path / "sounds"
    short_path = sounds_path / "shorts"
    longs_path = sounds_path / "longs"

    # Others
    themes_path = main_dir_path / "themes"
    queues_path = main_dir_path / "queues"

    # Files
    db_file_path = main_dir_path / "focus_keeper.db"
    config_file_path = main_dir_path / "config.yaml"
