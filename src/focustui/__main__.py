from pathlib import Path

import click
from click import Choice, echo, style

from focustui.app import FocusTUI
from focustui.config_manager import ConfigManager
from focustui.constants import (
    CONFIG_FILE_PATH,
    DB_FILE_PATH,
    LONGS_PATH,
    QUEUES_PATH,
    SHORTS_PATH,
    THEMES_PATH,
)
from focustui.db import DatabaseManager
from focustui.setup import setup_app
from focustui.sound_manager import SoundManager

_paths = {
    "db": DB_FILE_PATH,
    "config": CONFIG_FILE_PATH,
    "themes": THEMES_PATH,
    "queues": QUEUES_PATH,
    "shorts": SHORTS_PATH,
    "longs": LONGS_PATH,
}


@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx) -> None:
    """Start app."""
    if ctx.invoked_subcommand is None:
        # Prevent app start on command use
        setup_app()
        FocusTUI(
            db=DatabaseManager(),
            cm=ConfigManager(),
            sm=SoundManager(),
        ).run()


def echo_path(path: Path) -> None:
    """Print given resource path."""
    echo(style("Path: ", "green") + str(path))


@main.command()
@click.argument("what", type=Choice(list(_paths.keys())))
def locate(what: str) -> None:
    """Help you find location of a needed resource used by the app."""
    echo_path(_paths[what])
