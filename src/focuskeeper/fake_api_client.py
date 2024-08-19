from pathlib import Path


class FakeAPIClient:
    """This class is made to be used while testing app."""

    current_dir: Path = Path(__file__)
    root: Path = current_dir.parent.parent.parent
    sounds: Path = root / "static" / "sounds"
    longs: Path = sounds / "longs"
    shorts: Path = sounds / "shorts"

    def get_shorts(self) -> list[Path]:
        """Return list of shorts paths."""
        return list(self.shorts.glob("*"))

    def get_longs(self) -> list[Path]:
        """Return list of longs paths."""
        return list(self.longs.glob("*"))
