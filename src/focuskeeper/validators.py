from textual.validation import ValidationResult, Validator

from focuskeeper.constants import MIN_SESSION_LEN


class ValueFrom5to300(Validator):
    def validate(self, value: str) -> ValidationResult:
        if not value or int(value) < MIN_SESSION_LEN or int(value) > 300:
            msg = f"Session has to be between {MIN_SESSION_LEN} and 300 minutes"
            return self.failure(msg)
        return self.success()
