import pytest

from focustui.utils import session_len_parser


@pytest.mark.parametrize("zeros", ("0", "0:0", "0:00"))
def test_valid_0_format(zeros):
    assert session_len_parser(zeros) != -1


@pytest.mark.parametrize("zeros", ("0:", "0::", "0:::", "0::0"))
def test_invalid_0_format(zeros):
    assert session_len_parser(zeros) == -1


@pytest.mark.parametrize("minutes", range(5, 121))
def test_valid_min_format_from_5_to_120(minutes: int):
    assert session_len_parser(f"{minutes}") != -1


@pytest.mark.parametrize("time", ("3", "4"))
def test_invalid_min_format(time: str):
    assert session_len_parser(time) == -1


@pytest.mark.parametrize("time", ("1:00", "2:00"))
def test_valid_hour_min_format(time):
    assert session_len_parser(time) != -1


@pytest.mark.parametrize("hour", ("0:", "1:", "2:", "3:"))
def test_invalid_hour(hour):
    assert session_len_parser(hour) == -1


@pytest.mark.parametrize("i", range(5, 121))
def test_valid_hour_format_from_5_to_120(i: int):
    hour, min = divmod(i, 60)
    assert session_len_parser(f"{hour}:{min}") != -1


@pytest.mark.parametrize("i", range(5, 10))
def test_valid_hour_format_from_5_to_10_leading_0(i: int):
    """From 0:05 to 0:09"""
    hour, min = divmod(i, 60)
    assert session_len_parser(f"{hour}:{min:02}") != -1


@pytest.mark.parametrize("i", range(60, 70))
def test_valid_hour_format_from_60_to_70_leading_0(i: int):
    """From 1:01 to 1:09"""
    hour, min = divmod(i, 60)
    assert session_len_parser(f"{hour}:{min:02}") != -1


@pytest.mark.parametrize(
    "time",
    ("0:01", "0:02", "0:03", "0:04", "0:1", "0:2", "0:3", "0:4")
)
def test_invalid_hour_format_from_1_to_4(time):
    assert session_len_parser(time) == -1


@pytest.mark.parametrize(
    "time",
    ("1:61", "2:01", "2:59", "3:0", "3:01")
)
def test_invalid_hour_min_format(time: str):
    assert session_len_parser(time) == -1
