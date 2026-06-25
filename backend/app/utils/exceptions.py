from fastapi import HTTPException, status, Request
from fastapi.responses import JSONResponse
from typing import Any, Dict


class AppException(Exception):
    """Base exception class for application-specific errors."""
    def __init__(self, code: str, message: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundException(AppException):
    """Exception raised when a resource is not found."""
    def __init__(self, message: str = "Resource not found"):
        super().__init__(code="NOT_FOUND", message=message, status_code=status.HTTP_404_NOT_FOUND)


class BadRequestException(AppException):
    """Exception raised for bad requests."""
    def __init__(self, message: str = "Bad request"):
        super().__init__(code="BAD_REQUEST", message=message, status_code=status.HTTP_400_BAD_REQUEST)


class UnauthorizedException(AppException):
    """Exception raised for unauthorized access."""
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(code="UNAUTHORIZED", message=message, status_code=status.HTTP_401_UNAUTHORIZED)


class ForbiddenException(AppException):
    """Exception raised for forbidden access."""
    def __init__(self, message: str = "Forbidden"):
        super().__init__(code="FORBIDDEN", message=message, status_code=status.HTTP_403_FORBIDDEN)


class ConflictException(AppException):
    """Exception raised for conflicts (e.g., duplicate resource)."""
    def __init__(self, message: str = "Conflict"):
        super().__init__(code="CONFLICT", message=message, status_code=status.HTTP_409_CONFLICT)


class RateLimitException(AppException):
    """Exception raised when rate limit is exceeded."""
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(code="RATE_LIMIT_EXCEEDED", message=message, status_code=status.HTTP_429_TOO_MANY_REQUESTS)


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle application exceptions and return consistent error response."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.code, "message": exc.message}}
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions and return consistent error response."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": "HTTP_ERROR", "message": str(exc.detail)}}
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle general exceptions and return consistent error response."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": {"code": "INTERNAL_ERROR", "message": "An unexpected error occurred"}}
    )
