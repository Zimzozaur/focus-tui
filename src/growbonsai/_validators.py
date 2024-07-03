from textual.validation import Validator, ValidationResult


class ValueFrom5to300(Validator):
    def validate(self, value: str) -> ValidationResult:
        if not value or int(value) < 5 or int(value) > 300:
            return self.failure('Title cannot be longer than 50 chars')
        return self.success()
