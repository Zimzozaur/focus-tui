from focustui.constants import MINUTE


def hour_min_session_len(value: str):
    """Convert a time string in the format 'H:MM' to total minutes."""
    length = value.split(":")
    if len(length) == 1 and value == "0":
        return 0
    if len(length) == 1:
        return int(value) * MINUTE
    return int(length[0]) * MINUTE + int(length[1])


def int_to_hour_min(value: int) -> str:
    """Convert an int representing total minutes into a string formatted as 'H:MM'."""
    if value == 0:
        return "0"
    hour, minute = divmod(value, MINUTE)
    return f"{hour}:{minute:02d}"
