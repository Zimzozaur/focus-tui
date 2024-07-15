from pathlib import Path


class FakeAPIClient:
    """This class is made to be used while testing app"""
    current_dir = Path(__file__)
    root = current_dir.parent.parent.parent
    mp3 = root / 'static' / 'mp3'

    def get_songs(self) -> list[Path]:
        """Return path to songs"""
        return list(self.mp3.glob('*.mp3'))

