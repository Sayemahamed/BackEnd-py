from typing import Any, Dict, Optional

from fastapi import HTTPException, status


class BaseHTTPException(HTTPException):
    def __init__(
        self,
        status_code: int,
        detail: Any = None,
        headers: Optional[Dict[str, str]] = None,
        error_code: Optional[str] = None,
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code or str(status_code)


class NotFoundException(BaseHTTPException):
    def __init__(self, detail: str = "Resource not found", **kwargs):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_code="not_found",
            **kwargs,
        )


class UnauthorizedException(BaseHTTPException):
    def __init__(self, detail: str = "Not authenticated", **kwargs):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
            error_code="unauthorized",
            **kwargs,
        )


class ValidationException(BaseHTTPException):
    def __init__(self, errors: list, **kwargs):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"errors": errors},
            error_code="validation_error",
            **kwargs,
        )
