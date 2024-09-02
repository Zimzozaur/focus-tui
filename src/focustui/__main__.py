from focustui.app import FocusTUI
from focustui.config_manager import ConfigManager
from focustui.db import DatabaseManager
from focustui.setup import setup_app
from focustui.sound_manager import SoundManager


def main() -> None:
    setup_app()

    cm = ConfigManager()
    sm = SoundManager(cm)

    FocusTUI(
        db=DatabaseManager(),
        cm=cm,
        sm=sm,
    ).run()


if __name__ == "__main__":
    main()
