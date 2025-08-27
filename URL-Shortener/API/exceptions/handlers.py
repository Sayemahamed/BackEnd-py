from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .http import (
    BaseHTTPException,
    NotFoundException,
    UnauthorizedException,
    ValidationException,
)


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    error_code: str
    details: Optional[Dict[str, Any]] = None


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(BaseHTTPException)
    async def http_exception_handler(request: Request, exc: BaseHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error=str(exc.detail),
                error_code=exc.error_code,
                details=exc.detail if isinstance(exc.detail, dict) else None,
            ).dict(),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        errors = []
        for error in exc.errors():
            field = ".".join(str(loc) for loc in error["loc"][1:] if loc != "body")
            errors.append(
                {
                    "field": field or "body",
                    "message": error["msg"],
                    "type": error["type"],
                }
            )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=ErrorResponse(
                error="Validation error",
                error_code="validation_error",
                details={"errors": errors},
            ).dict(),
        )

    @app.exception_handler(HTTPException)
    async def generic_http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error=str(exc.detail),
                error_code=str(exc.status_code),
                details=exc.detail if isinstance(exc.detail, dict) else None,
            ).dict(),
        )

    @app.exception_handler(500)
    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        # In production, log this error
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                error="Internal server error", error_code="internal_server_error"
            ).dict(),
        )
