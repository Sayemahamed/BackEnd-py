from fastapi import status
from fastapi.exceptions import HTTPException


class AuthException(HTTPException):
    """Base exception for authentication errors"""
    
    def __init__(self, **kwargs):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            **kwargs
        )


class InvalidCredentials(AuthException):
    """Raised when invalid credentials are provided"""
    
    def __init__(self, detail: str = "Invalid email or password"):
        super().__init__(
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class TokenError(AuthException):
    """Base exception for token-related errors"""
    
    def __init__(self, detail: str = "Invalid token"):
        super().__init__(
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class TokenExpired(TokenError):
    """Raised when a token has expired"""
    
    def __init__(self, detail: str = "Token has expired"):
        super().__init__(detail=detail)


class TokenInvalid(TokenError):
    """Raised when a token is invalid"""
    
    def __init__(self, detail: str = "Could not validate credentials"):
        super().__init__(detail=detail)


class InactiveUser(AuthException):
    """Raised when a user account is inactive"""
    
    def __init__(self, detail: str = "Inactive user"):
        super().__init__(detail=detail)


class InsufficientPermissions(AuthException):
    """Raised when a user doesn't have required permissions"""
    
    def __init__(self, detail: str = "Insufficient permissions"):
        self.status_code = status.HTTP_403_FORBIDDEN
        self.detail = detail
