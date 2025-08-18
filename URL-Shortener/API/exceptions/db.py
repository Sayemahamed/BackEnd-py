from .base import IntegrityError


class DuplicateEntry(IntegrityError):
    _default_error_code = "duplicate_entry"
    _detail = "The resource you’re trying to create already exists."


class ForeignKeyViolation(IntegrityError):
    _default_error_code = "foreign_key_violation"
    _detail = "Referenced resource does not exist."
