from focuskeeper.app import FocusKeeper
from focuskeeper.setup import AppSetup


def main():
    AppSetup().setup_app()
    FocusKeeper().run()


if __name__ == "__main__":
    main()
