from .base import Conflict, NotFound

class UserAlreadyExists(Conflict):
    """Raised when creating a user with an email that already exists."""
    _detail = "A user with this email already exists."
    _default_error_code = "user_already_exists"

class UserNotFound(NotFound):
    """Raised when a user cannot be found by ID or email."""
    _detail = "User not found."
    _default_error_code = "user_not_found"
