from textual.validation import ValidationResult, Validator

from focustui.constants import HOURS_MINUTES_TIMER_PATTERN
from focustui.constants import MAX_SESSION_LEN as MAX_S_LEN
from focustui.constants import MAX_VOLUME_LEVEL as MAX_V_LEV
from focustui.constants import MIN_SESSION_LEN as MIN_S_LEN
from focustui.constants import MIN_VOLUME_LEVEL as MIN_V_LEV


class StopwatchOrTimer(Validator):
    def validate(self, value: str) -> ValidationResult:
        if (
            value.isdigit() and
            (int(value) == 0 or MIN_S_LEN <= int(value) <= MAX_S_LEN)
        ):
            return self.success()
        return self.failure()


class StopwatchOrTimerHour(Validator):
    def validate(self, value: str) -> ValidationResult:
        pattern_bool = bool(HOURS_MINUTES_TIMER_PATTERN.match(value))
        forbidden_patter = ["0:00", "0:0"]
        if pattern_bool and value not in forbidden_patter:
            return self.success()
        return self.failure()


class ValueFrom1to100(Validator):
    def validate(self, value: str) -> ValidationResult:
        if not value or int(value) < MIN_V_LEV or int(value) > MAX_V_LEV:
            return self.failure()
        return self.success()
