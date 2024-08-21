from collections.abc import Iterable
from pathlib import Path

from textual.widgets import DirectoryTree


class MusicDirectoryTree(DirectoryTree):
    show_root = False

    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        def not_hidden(path: Path) -> bool:
            return path.is_dir() and not path.name.startswith(".")

        suffixes = {".wav", ".mp3", ".ogg", ".flac", ".opus", "/"}
        return [path for path in paths if not_hidden(path) or path.suffix in suffixes]
