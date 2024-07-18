from focuskeeper.app import FocusSeeds
from focuskeeper.setup import AppSetup


def main():
    AppSetup().setup_app()
    FocusSeeds().run()


if __name__ == "__main__":
    main()
