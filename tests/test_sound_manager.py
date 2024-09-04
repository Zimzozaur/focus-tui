from pathlib import Path
from unittest.mock import Mock

import pytest

from focustui.sound_manager import Sound, create_sounds_dict

ROOT = Path(__file__).parent.parent
SOUND_PATH = "src/focustui/static/sounds/shorts/Braam.flac"


@pytest.fixture
def sound_obj() -> Sound:
    path = ROOT / SOUND_PATH
    return Sound(path)


def test_sound_path(sound_obj):
    path = ROOT / SOUND_PATH
    assert sound_obj.path == path


def test_sound_sound_type(sound_obj):
    assert sound_obj.sound_type == "short"


def test_sound_full_name(sound_obj):
    assert sound_obj.full_name == "Braam.flac"


def test_sound_name(sound_obj):
    assert sound_obj.name == "Braam"


def test_sound_extension(sound_obj):
    assert sound_obj.extension == ".flac"


def test_sound_is_default(sound_obj):
    assert sound_obj.is_default is True


def test_sound_repr(sound_obj):
    repr = f"Sound({ROOT / SOUND_PATH})"
    assert sound_obj.__repr__() == repr


def test_sound_gt(sound_obj):
    other = Sound(ROOT / "src/focustui/static/sounds/shorts/Woohoo.flac")
    assert sound_obj < other


def test_sound_lt(sound_obj):
    other = Sound(ROOT / "src/focustui/static/sounds/shorts/Woohoo.flac")
    assert other > sound_obj


@pytest.mark.parametrize(
    "extension",
    (".wav", ".mp3", ".ogg", ".flac", ".opus")
)
def test_create_sounds_dict_correct_extensions(extension):
    mock_file = Mock(spec=Path)
    mock_file.name = f"sound1{extension}"
    mock_file.suffix = extension
    mock_path = Mock(spec=Path)
    mock_path.glob.return_value = [mock_file]
    assert len(create_sounds_dict(mock_path)) == 1


def test_create_sounds_dict_wrong_extension():
    mock_file = Mock(spec=Path)
    mock_file.name = f"sound1.jpg"
    mock_file.suffix = ".jpg"
    mock_path = Mock(spec=Path)
    mock_path.glob.return_value = [mock_file]
    assert len(create_sounds_dict(mock_path)) == 0



