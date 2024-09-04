from pathlib import Path


class SoundFileManager:
    """Manages sound files bundled with the application.

    This class provides methods to access the paths of short and long sound files
    stored within the package. It is primarily used to copy these sound files
    to the appropriate directories on the user's PC.
    """

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
