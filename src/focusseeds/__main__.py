from focusseeds.app import FocusSeeds
from focusseeds.setup import AppSetup


def main():
    AppSetup().setup_app()
    FocusSeeds().run()


if __name__ == "__main__":
    main()
