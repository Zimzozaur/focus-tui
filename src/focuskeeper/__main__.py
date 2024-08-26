from focuskeeper.setup import setup_app
from focuskeeper.app import FocusKeeper


def main() -> None:
    """Set up the application and starts the FocusKeeper instance."""
    setup_app()
    FocusKeeper().run()


if __name__ == "__main__":
    main()
