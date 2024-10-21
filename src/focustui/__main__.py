from focustui.app import FocusTUI
from focustui.config_manager import ConfigManager
from focustui.db import DatabaseManager
from focustui.setup import setup_app
from focustui.sound_manager import SoundManager


def main() -> None:
    """Start app."""
    setup_app()
    FocusTUI(
        db=DatabaseManager(),
        cm=ConfigManager(),
        sm=SoundManager(),
    ).run()


if __name__ == "__main__":
    main()
