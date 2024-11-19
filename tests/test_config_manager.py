import pytest
from pytest_mock.plugin import MockerFixture

from focustui.config_manager import ConfigManager, ConfigModel
from focustui.constants import SoundType, VolumeType

from focustui.constants import DEFAULT_ALARM_NAME as DEF_AL
from focustui.constants import DEFAULT_SIGNAL_NAME as DEF_SIG
from focustui.constants import DEFAULT_AMBIENT_NAME as DEF_AMB


@pytest.fixture
def mock_cm_init(mocker: MockerFixture):
    mock_function = mocker.patch(
        "focustui.config_manager._load_and_validate_model"
    )
    mock_function.return_value = ConfigModel()
    return mock_function


@pytest.fixture
def mock_save_config(mocker: MockerFixture):
    mocker.patch(
        "focustui.config_manager.ConfigManager._save_config"
    )


def test_session_length_positive():
    key = "session_length"
    test_dict = {key: "45"}
    model = ConfigModel.model_validate(test_dict)
    assert test_dict[key] == model.model_dump()[key]


def test_session_length_zero():
    key = "session_length"
    test_dict = {key: "0"}
    model = ConfigModel.model_validate(test_dict)
    assert test_dict[key] == model.model_dump()[key]


def test_test_sound_volume():
    key = "test_volume"
    test_dict = {key: 57}
    model = ConfigModel.model_validate(test_dict)
    assert test_dict[key] == model.model_dump()[key]


def test_is_singleton(mock_cm_init):
    inst1 = ConfigManager()
    inst2 = ConfigManager()
    assert inst1 is inst2


def test_default_alarm(mock_cm_init):
    inst = ConfigManager()
    sound_name = inst.config.alarm.name
    assert sound_name == inst.get_sound_name("alarm")


def test_default_signal(mock_cm_init):
    inst = ConfigManager()
    sound_name = inst.config.signal.name
    assert sound_name == inst.get_sound_name("signal")


def test_default_ambient(mock_cm_init):
    inst = ConfigManager()
    sound_name = inst.config.ambient.name
    assert sound_name == inst.get_sound_name("ambient")


@pytest.mark.parametrize(
    ("sound_type", "new_name"),
    (
            ("alarm", "Mario"),
            ("signal", "Mario"),
            ("ambient", "Mario"),
    )
)
def test_update_sound_name(mock_cm_init, mock_save_config, sound_type: SoundType, new_name):
    inst = ConfigManager()
    inst.update_used_sound(sound_type, new_name)
    sound_name = inst.get_sound_name(sound_type)
    assert sound_name == new_name


@pytest.mark.parametrize(
    "sound_name", (DEF_AL, DEF_SIG, DEF_AMB)
)
def test_is_in_config(mock_cm_init, sound_name: str):
    inst = ConfigManager()
    assert inst.is_sound_in_config(sound_name)


@pytest.mark.parametrize(
    (
        "old_name",
        "new_name",
        "new_alarm",
        "alarm",
        "new_signal",
        "signal",
        "new_ambient",
        "ambient"
    ),
    (
        ("A", None, DEF_AL, DEF_AL, DEF_SIG, DEF_SIG, DEF_AMB, DEF_AMB),
        ("A", None, "A", DEF_AL, DEF_SIG, DEF_SIG, DEF_AMB, DEF_AMB),
        ("A", None, DEF_AL, DEF_AL, "A", DEF_SIG, DEF_AMB, DEF_AMB),
        ("A", None, DEF_AL, DEF_AL, DEF_SIG, DEF_SIG, "A", DEF_AMB),
        ("A", None, "A", DEF_AL, "A", DEF_SIG, DEF_AMB, DEF_AMB),
        ("A", None, "A", DEF_AL, DEF_SIG, DEF_SIG, "A", DEF_AMB),
        ("A", None, DEF_AL, DEF_AL, "A", DEF_SIG, "A", DEF_AMB),
        ("A", None, "A", DEF_AL, "A", DEF_SIG, "A", DEF_AMB),
        ("A", "A", "A", "A", DEF_SIG, DEF_SIG, DEF_AMB, DEF_AMB),
        ("A", "A", DEF_AL, DEF_AL, "A", "A", DEF_AMB, DEF_AMB),
        ("A", "A", DEF_AL, DEF_AL, DEF_SIG, DEF_SIG, "A", "A"),
        ("A", "A", "A", "A", "A", "A", DEF_AMB, DEF_AMB),
        ("A", "A", "A", "A", DEF_SIG, DEF_SIG, "A", "A"),
        ("A", "A", DEF_AL, DEF_AL, "A", "A", "A", "A"),
        ("A", "A", "A", "A", "A", "A", "A", "A"),
    )
)
def test_update_sound_name_if_in_config(
        mock_cm_init,
        mock_save_config,
        old_name,
        new_name,
        new_alarm,
        alarm,
        new_signal,
        signal,
        new_ambient,
        ambient,
):
    """
    Params:
        old_name - Name that will be check is in config
        new_name - New name for attribute that old name matches
                    if None names will be set to deflate
        new_alarm - Name to which alarm will be changed
        alarm - Alarm name after change
        new_signal - Name to which signal will be changed
        signal - Signal name after change
        new_ambient -Name to which signal will be changed
        ambient - Ambient name after change

    All cases.
    1. Keep everything to default and old_name does not match
    2 - 8. Set new name and change back to default
    9 - 15. Set new name and change to new name
    """
    inst = ConfigManager()
    inst.update_used_sound("alarm", new_alarm)
    inst.update_used_sound("signal", new_signal)
    inst.update_used_sound("ambient", new_ambient)

    inst.update_sound_name(old_name, new_name)

    assert inst.config.alarm.name == alarm
    assert inst.config.signal.name == signal
    assert inst.config.ambient.name == ambient


@pytest.mark.parametrize(
    ("sound_type", "new_name"),
    (
            ("alarm", "Mario"),
            ("signal", "Luigi"),
            ("ambient", "Toad"),
    )
)
def test_is_in_config_after_change(mock_cm_init, mock_save_config, sound_type: SoundType, new_name):
    inst = ConfigManager()
    inst.update_used_sound(sound_type, new_name)
    assert inst.is_sound_in_config(new_name)


@pytest.mark.parametrize(
    ("volume_name", "volume_type"),
    (
        ("alarm_volume", "alarm"),
        ("signal_volume", "signal"),
        ("ambient_volume", "ambient"),
    )
)
def test_change_volume_value(mock_cm_init, mock_save_config, volume_name: VolumeType, volume_type: SoundType):
    inst = ConfigManager()
    new_volume_value = 1
    inst.change_volume_value(volume_name, new_volume_value)
    assert getattr(inst.config, volume_type).volume == new_volume_value


def test_change_volume_value_for_test(mock_cm_init, mock_save_config):
    inst = ConfigManager()
    new_volume_value = 1
    inst.change_volume_value("test_volume", new_volume_value)
    assert inst.config.test_volume == new_volume_value


def test_get_session_length(mock_cm_init):
    inst = ConfigManager()
    assert inst.config.session_length == inst.get_session_length()


def test_update_session_length(mock_cm_init, mock_save_config):
    inst = ConfigManager()
    new_length = 1
    inst.update_session_length(new_length)
    assert inst.get_session_length() == new_length
