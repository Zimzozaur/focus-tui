from focuskeeper.app import FocusKeeper
from focuskeeper.setup import setup_app


def main() -> None:
    setup_app()
    FocusKeeper().run()


if __name__ == "__main__":
    main()
