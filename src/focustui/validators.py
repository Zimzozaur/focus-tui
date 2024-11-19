from textual.validation import ValidationResult, Validator

from focustui.constants import MAX_VOLUME_LEVEL as MAX_V_LEV
from focustui.constants import MIN_VOLUME_LEVEL as MIN_V_LEV
from focustui.utils import session_len_parser


class SessionInputValidator(Validator):
    def validate(self, value: str) -> ValidationResult:
        if session_len_parser(value) != -1:
            return self.success()
        return self.failure()


class ValueFrom1to100(Validator):
    def validate(self, value: str) -> ValidationResult:
        if not value or int(value) < MIN_V_LEV or int(value) > MAX_V_LEV:
            return self.failure()
        return self.success()
