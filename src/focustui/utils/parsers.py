from focustui.constants import MAX_SESSION_LEN as MAX_S
from focustui.constants import MIN_SESSION_LEN as MIN_S
from focustui.constants import MINUTE, SESSION_SIGNATURE


def session_len_parser(string: str) -> int:
    """If input string is correct return length
    if not return -1 as the indicator of invalid value.

    It accepts 0 or value in one of the 2 forms:
    1. Minutes form - value between MIN to MAX
    2. Hour form - H:M or H:MM between MIN and MAX
    """
    if not SESSION_SIGNATURE.match(string):
        return -1
    if ":" in string:
        hour, minute = string.split(":")
        time = int(hour) * MINUTE + int(minute)
        if time == 0 or MIN_S <= time <= MAX_S:
            return time
        return -1
    time = int(string)
    if time == 0 or MIN_S <= time <= MAX_S:
        return time
    return -1
