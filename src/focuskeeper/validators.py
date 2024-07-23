from textual.validation import Validator, ValidationResult

from focuskeeper.settings import MIN_SESSION_LEN


class ValueFrom5to300(Validator):
    def validate(self, value: str) -> ValidationResult:
        if not value or int(value) < MIN_SESSION_LEN or int(value) > 300:
            return self.failure('Session has to be between 5 and 300 minutes')
        return self.success()
