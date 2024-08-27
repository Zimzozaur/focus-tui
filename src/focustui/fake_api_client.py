from pathlib import Path


class FakeAPIClient:
    """Used while testing app."""

    current_dir: Path = Path(__file__).parent
    sounds: Path = current_dir / "static" / "sounds"
    longs: Path = sounds / "longs"
    shorts: Path = sounds / "shorts"

    def get_shorts(self) -> list[Path]:
        """Return list of shorts paths."""
        return list(self.shorts.glob("*"))

    def get_longs(self) -> list[Path]:
        """Return list of longs paths."""
        return list(self.longs.glob("*"))
