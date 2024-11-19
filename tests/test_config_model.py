from focustui.config_manager import ConfigModel, _SoundModel


def test_set_to_default_faulty_volume_to_small():
    faulty_values = {"name": "Lol", "volume": -1}
    res = _SoundModel.model_validate(faulty_values)
    assert res == _SoundModel.model_validate({"name": "Lol"})


def test_set_to_default_faulty_volume_to_big():
    faulty_values = {"name": "Lol", "volume": 10**9}
    res = _SoundModel.model_validate(faulty_values)
    assert res == _SoundModel.model_validate({"name": "Lol"})


def test_ignore_faulty_config_settings():
    faulty_values = {"RANDOM_VALUE": 123, "MARIO?": "Luigi"}
    assert ConfigModel.model_validate(faulty_values) == ConfigModel()


def test_set_to_default_session_length_to_big():
    faulty_values = {"session_length": "-1"}
    res = ConfigModel.model_validate(faulty_values)
    assert res == ConfigModel()


def test_set_to_default_faulty_session_length_to_big():
    faulty_values = {"session_length": "1000"}
    res = ConfigModel.model_validate(faulty_values)
    assert res == ConfigModel()
