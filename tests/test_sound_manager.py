from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from pytest_mock.plugin import MockerFixture

from focustui.constants import LONGS_PATH, SHORTS_PATH
from focustui.sound_manager import Sound, create_sounds_dict, SoundManager

ROOT = Path(__file__).parent.parent
SOUND_PATH = "src/focustui/static/sounds/shorts/Braam.flac"
SHORT_PATH = "src/focustui/static/sounds/shorts/"
LONG_PATH = "src/focustui/static/sounds/longs/"


@pytest.fixture
def sound_obj() -> Sound:
    path = ROOT / SOUND_PATH
    return Sound(path)


@pytest.fixture
def mock_get_any_sound(mocker: MockerFixture):
    mock_function = mocker.patch(
        "focustui.sound_manager.SoundManager.get_any_sound"
    )
    mock_function.return_value.path = (
        Path(__file__).parent.parent
        / "src/focustui/static/sounds/shorts" / "Acid_Bassline.flac"
    )
    return mock_function


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


def create_shorts_dict():
    paths: list[Path] = [Path(SHORT_PATH + f"sound_{i}.mp3")
                         for i in [3, 1, 9, 7]]

    mock_path = Mock(spec=Path)
    mock_path.glob.return_value = paths

    sound_dict: dict[str, Sound] = create_sounds_dict(mock_path)
    sound_dict["sound_7"].is_default = True
    sound_dict["sound_9"].is_default = True
    return sound_dict


def create_longs_dict():
    paths: list[Path] = [Path(LONG_PATH + f"sound_{i}.mp3")
                         for i in [2, 0, 10, 6]]

    mock_path = Mock(spec=Path)
    mock_path.glob.return_value = paths

    sound_dict: dict[str, Sound] = create_sounds_dict(mock_path)
    sound_dict["sound_6"].is_default = True
    sound_dict["sound_10"].is_default = True
    return sound_dict


def custom_create_sounds_dict(path):
    if path == SHORTS_PATH:
        return create_shorts_dict()
    elif path == LONGS_PATH:
        return create_longs_dict()
    raise ValueError


@pytest.fixture
def sound_manager():
    with patch(
        'focustui.sound_manager.create_sounds_dict',
        side_effect=custom_create_sounds_dict
    ):
        manager = SoundManager()
        yield manager


def test_user_shorts_list(sound_manager):
    result = sound_manager.user_shorts_list
    assert result == ["sound_1", "sound_3"]


def test_all_shorts_list(sound_manager):
    result = sound_manager.all_shorts_list
    assert result == ["sound_1", "sound_3", "sound_7", "sound_9"]


def test_user_longs_list(sound_manager):
    result = sound_manager.user_longs_list
    assert result == ["sound_0", "sound_2"]


def test_all_longs_list(sound_manager):
    result = sound_manager.all_longs_list
    assert result == ["sound_0", "sound_10", "sound_2", "sound_6"]


def test_all_sounds_list(sound_manager):
    print(sound_manager.all_sounds_list)
    result = sound_manager.all_sounds_list
    assert result == [
        "sound_0", "sound_1", "sound_10", "sound_2",
        "sound_3", "sound_6", "sound_7", "sound_9"
    ]


def test_get_user_short(sound_manager):
    user_short = "sound_3"
    result = sound_manager.get_any_sound(user_short)
    assert result.name == user_short


def test_get_short(sound_manager):
    short = "sound_7"
    result = sound_manager.get_any_sound(short)
    assert result.name == short


def test_get_user_long(sound_manager):
    user_long = "sound_2"
    result = sound_manager.get_any_sound(user_long)
    assert result.name == user_long


def test_get_long(sound_manager):
    long = "sound_6"
    result = sound_manager.get_any_sound(long)
    assert result.name == long


def test_is_duplicate_short_dup(sound_manager):
    assert sound_manager.is_duplicate("sound_1")


def test_is_duplicate_short_no_dup(sound_manager):
    assert not sound_manager.is_duplicate("sound_30")


def test_is_duplicate_long_dup(sound_manager):
    assert sound_manager.is_duplicate("sound_0")


def test_is_duplicate_long_no_dup(sound_manager):
    assert not sound_manager.is_duplicate("sound_30")


@pytest.mark.parametrize(
    ("old_name", "new_name"),
    (("sound_1", "short"), ("sound_2", "long"))
)
def test_rename_sound_short(sound_manager, old_name, new_name):
    with patch.object(Path, 'rename'):
        sound_manager.rename_sound(old_name, new_name)
    assert sound_manager.is_duplicate(new_name)
    assert not sound_manager.is_duplicate(old_name)


def test_add_sound_short(sound_manager):
    with patch("shutil.copy"):
        sound_manager.add_sound(Mock(spec=Path), "Mario", ".flac", "short")
    assert len(sound_manager._shorts_dict) == 5


def test_add_sound_long(sound_manager):
    with patch("shutil.copy"):
        sound_manager.add_sound(Mock(spec=Path), "Mario", ".flac", "long")
    assert len(sound_manager._longs_dict) == 5


def test_remove_sound_short(sound_manager):
    with patch.object(Path, "unlink"):
        sound_manager.remove_sound("sound_3", "short")
    assert len(sound_manager._shorts_dict) == 3


def test_remove_sound_long(sound_manager):
    with patch.object(Path, "unlink"):
        sound_manager.remove_sound("sound_2", "long")
    assert len(sound_manager._longs_dict) == 3


def test_play_sound(sound_manager, mock_get_any_sound):
    sound_manager.play_sound("what_ever", 1)
    assert sound_manager._sound_channel.get_sound() is not None


def test_play_ambient_in_background(sound_manager, mock_get_any_sound):
    sound_manager.play_ambient_in_background("what_ever")
    assert sound_manager._ambient_channel.get_volume() == 0
    assert sound_manager._ambient_channel.get_sound() is not None


def test_stop_ambient(sound_manager, mock_get_any_sound):
    sound_manager.play_ambient_in_background("what_ever")
    sound_manager.stop_ambient()
    assert sound_manager._ambient_channel.get_sound() is None


def test_stop_sound(sound_manager, mock_get_any_sound):
    sound_manager.play_sound("what_ever", 1)
    sound_manager.stop_sound()
    assert sound_manager._sound_channel.get_sound() is None
