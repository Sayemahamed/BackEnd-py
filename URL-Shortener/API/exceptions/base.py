from http import HTTPStatus
from typing import Any, Dict, Optional

from fastapi import HTTPException


class APIException(Exception):
    """
    Base class for all service-layer exceptions.

    Attributes:
        detail: Human-readable error description.
        error_code: Machine-friendly error code.
        status: HTTPStatus to map to HTTP responses.
        extra: Arbitrary context for clients (e.g. field names).
    """

    status: HTTPStatus = HTTPStatus.INTERNAL_SERVER_ERROR
    _default_error_code: str = "api_error"

    __slots__ = ("_detail", "_error_code", "_status", "_extra")

    def __init__(
        self,
        detail: Optional[str] = None,
        *,
        error_code: Optional[str] = None,
        status: Optional[HTTPStatus] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        # Set detail, falling back to class‐level _detail or generic text
        self._detail = detail or getattr(self, "_detail", "An unexpected error occurred.")
        # Pull default from private class var, override if provided
        self._error_code = error_code or self._default_error_code
        # Pull default status, override if provided
        self._status = status or self.status
        # Store arbitrary extra context
        self._extra = extra or {}

    @property
    def detail(self) -> str:
        return self._detail

    @property
    def error_code(self) -> str:
        return self._error_code

    @property
    def status_code(self) -> int:
        return self._status.value

    @property
    def extra(self) -> Dict[str, Any]:
        return self._extra.copy()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize exception for JSON responses."""
        payload: Dict[str, Any] = {
            "error_code": self.error_code,
            "detail": self.detail,
        }
        if self._extra:
            payload["extra"] = self._extra
        return payload

    def to_http(self) -> HTTPException:
        """Convert this exception into FastAPI’s HTTPException."""
        return HTTPException(status_code=self.status_code, detail=self.to_dict())

    def __str__(self) -> str:
        return f"[{self.error_code}] {self.detail}"


class BadRequest(APIException):
    status = HTTPStatus.BAD_REQUEST
    _default_error_code = "bad_request"


class ValidationError(BadRequest):
    _default_error_code = "validation_error"


class AuthenticationError(APIException):
    status = HTTPStatus.UNAUTHORIZED
    _default_error_code = "authentication_failed"


class AuthorizationError(APIException):
    status = HTTPStatus.FORBIDDEN
    _default_error_code = "authorization_failed"


class NotFound(APIException):
    status = HTTPStatus.NOT_FOUND
    _default_error_code = "not_found"


class Conflict(APIException):
    status = HTTPStatus.CONFLICT
    _default_error_code = "conflict"


class ServiceUnavailable(APIException):
    status = HTTPStatus.SERVICE_UNAVAILABLE
    _default_error_code = "service_unavailable"




class IntegrityError(Conflict):
    _default_error_code = "integrity_error"
    _detail = "A database integrity constraint was violated."
