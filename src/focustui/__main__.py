from focustui.setup import setup_app


def main() -> None:
    setup_app()

    # Import here to avoid running Sound manager before
    # setting all folders and files if needed
    from focustui.app import FocusTUI
    FocusTUI().run()


if __name__ == "__main__":
    main()
