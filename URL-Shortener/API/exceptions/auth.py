from .base import AuthenticationError, BadRequest


class PasswordTooWeak(BadRequest):
    """Raised when a provided password fails strength requirements."""

    _detail = "The provided password does not meet complexity requirements."
    _default_error_code = "password_too_weak"


class TokenExpired(AuthenticationError):
    """Raised when an access token has expired."""

    _detail = "Authentication token has expired."
    _default_error_code = "token_expired"


class TokenInvalid(AuthenticationError):
    """Raised when a token is malformed or its signature is invalid."""

    _detail = "Provided token is invalid."
    _default_error_code = "token_invalid"


class PasswordOrEmailInvalid(AuthenticationError):
    """Raised when a token is malformed or its signature is invalid."""

    _detail = "Provided password or email is invalid."
    _default_error_code = "password_or_email_invalid"


class WrongPassword(AuthenticationError):
    """Raised when a token is malformed or its signature is invalid."""

    _detail = "Provided password is incorrect."
    _default_error_code = "wrong_password"
