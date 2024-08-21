from textual.validation import ValidationResult, Validator

from focuskeeper.constants import MIN_SESSION_LEN as MIN_S_LEN
from focuskeeper.constants import MAX_SESSION_LEN as MAX_S_LEN


class ValueFrom5to300(Validator):
    def validate(self, value: str) -> ValidationResult:
        if not value or int(value) < MIN_S_LEN or int(value) > MAX_S_LEN:
            msg = f"Session has to be between {MIN_S_LEN} and {MAX_S_LEN} minutes"
            return self.failure(msg)
        return self.success()
