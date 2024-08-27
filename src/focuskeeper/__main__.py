from focuskeeper.setup import setup_app


def main() -> None:
    """Set up the application and starts the FocusKeeper instance."""
    setup_app()

    # Import here to avoid running Sound manager before
    # setting all folders and files if needed
    from focuskeeper.app import FocusKeeper
    FocusKeeper().run()


if __name__ == "__main__":
    main()
