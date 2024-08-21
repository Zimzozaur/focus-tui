from focuskeeper.app import FOCUS_KEEPER
from focuskeeper.setup import setup_app


def main() -> None:
    """Set up the application and starts the FocusKeeper instance."""
    setup_app()
    FOCUS_KEEPER.run()


if __name__ == "__main__":
    main()
