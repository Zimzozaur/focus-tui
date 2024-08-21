from textual.validation import ValidationResult, Validator

from focuskeeper.constants import MAX_SESSION_LEN as MAX_S_LEN
from focuskeeper.constants import MIN_SESSION_LEN as MIN_S_LEN
from focuskeeper.constants import MAX_VOLUME_LEVEL as MAX_V_LEV
from focuskeeper.constants import MIN_VOLUME_LEVEL as MIN_V_LEV


class ValueFrom5to300(Validator):
    def validate(self, value: str) -> ValidationResult:
        if not value or int(value) < MIN_S_LEN or int(value) > MAX_S_LEN:
            return self.failure()
        return self.success()


class ValueFrom1to100(Validator):
    def validate(self, value: str) -> ValidationResult:
        if not value or int(value) < MIN_V_LEV or int(value) > MAX_V_LEV:
            return self.failure()
        return self.success()
