"""
Custom Exception Handlers dan Error Response Standardization.
Semua error akan return format yang konsisten! 🎯
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from typing import Any, Optional
import logging
import traceback

logger = logging.getLogger(__name__)


# ================================================
# STANDARD ERROR RESPONSE MODEL
# ================================================

class ErrorResponse:
    """Standard error response format."""
    
    def __init__(
        self,
        success: bool = False,
        error_code: str = "UNKNOWN_ERROR",
        message: str = "An error occurred",
        details: Optional[Any] = None,
        request_id: Optional[str] = None
    ):
        self.success = success
        self.error_code = error_code
        self.message = message
        self.details = details
        self.request_id = request_id
    
    def to_dict(self) -> dict:
        response = {
            "success": self.success,
            "error": {
                "code": self.error_code,
                "message": self.message
            }
        }
        if self.details:
            response["error"]["details"] = self.details
        if self.request_id:
            response["request_id"] = self.request_id
        return response


# ================================================
# ERROR CODE MAPPING
# ================================================

HTTP_ERROR_CODES = {
    400: "BAD_REQUEST",
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    405: "METHOD_NOT_ALLOWED",
    409: "CONFLICT",
    422: "VALIDATION_ERROR",
    429: "TOO_MANY_REQUESTS",
    500: "INTERNAL_SERVER_ERROR",
    502: "BAD_GATEWAY",
    503: "SERVICE_UNAVAILABLE",
}

ERROR_MESSAGES_BM = {
    400: "Request tak valid bro! 🚫",
    401: "Kau kena login dulu! 🔒",
    403: "Kau takde permission untuk buat ni! 🚫",
    404: "Tak jumpa la benda ni! 😅",
    405: "Method ni tak dibenarkan!",
    409: "Ada conflict dengan data sedia ada! ⚠️",
    422: "Data yang kau hantar tak valid!",
    429: "Slow down bro! Terlalu banyak request! 🐢",
    500: "Server error! Cuba lagi nanti 😅",
    502: "Gateway error!",
    503: "Service tak available sekarang!",
}


# ================================================
# EXCEPTION HANDLERS
# ================================================

async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTPException with standard format."""
    request_id = getattr(request.state, "request_id", None)
    
    error_code = HTTP_ERROR_CODES.get(exc.status_code, "HTTP_ERROR")
    
    # Use custom message if provided, otherwise use default BM message
    message = exc.detail if exc.detail else ERROR_MESSAGES_BM.get(
        exc.status_code, "Ada error berlaku!"
    )
    
    error_response = ErrorResponse(
        error_code=error_code,
        message=message,
        request_id=request_id
    )
    
    # Log error
    logger.warning(
        f"HTTP {exc.status_code} | {error_code} | {message} | "
        f"Path: {request.url.path} | Request ID: {request_id}"
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.to_dict()
    )


async def validation_exception_handler(
    request: Request, 
    exc: RequestValidationError
) -> JSONResponse:
    """Handle validation errors with details."""
    request_id = getattr(request.state, "request_id", None)
    
    # Format validation errors nicely
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"]
        })
    
    error_response = ErrorResponse(
        error_code="VALIDATION_ERROR",
        message="Data yang kau hantar tak valid! Check balik 👇",
        details=errors,
        request_id=request_id
    )
    
    logger.warning(
        f"Validation Error | Path: {request.url.path} | "
        f"Errors: {len(errors)} | Request ID: {request_id}"
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response.to_dict()
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    request_id = getattr(request.state, "request_id", None)
    
    # Log full traceback for debugging
    logger.error(
        f"Unhandled Exception | Path: {request.url.path} | "
        f"Request ID: {request_id} | Error: {str(exc)}\n"
        f"Traceback: {traceback.format_exc()}"
    )
    
    error_response = ErrorResponse(
        error_code="INTERNAL_SERVER_ERROR",
        message="Server error! Cuba lagi nanti 😅",
        request_id=request_id
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.to_dict()
    )


# ================================================
# CUSTOM EXCEPTIONS
# ================================================

class AppException(HTTPException):
    """Base application exception."""
    
    def __init__(
        self,
        status_code: int = 400,
        error_code: str = "APP_ERROR",
        message: str = "Application error",
        details: Optional[Any] = None
    ):
        self.error_code = error_code
        self.details = details
        super().__init__(status_code=status_code, detail=message)


class NotFoundError(AppException):
    """Resource not found."""
    
    def __init__(self, resource: str = "Resource"):
        super().__init__(
            status_code=404,
            error_code="NOT_FOUND",
            message=f"{resource} tak jumpa! 😅"
        )


class UnauthorizedError(AppException):
    """Not authenticated."""
    
    def __init__(self, message: str = "Kau kena login dulu! 🔒"):
        super().__init__(
            status_code=401,
            error_code="UNAUTHORIZED",
            message=message
        )


class ForbiddenError(AppException):
    """Not authorized."""
    
    def __init__(self, message: str = "Kau takde permission untuk buat ni! 🚫"):
        super().__init__(
            status_code=403,
            error_code="FORBIDDEN",
            message=message
        )


class ConflictError(AppException):
    """Resource conflict."""
    
    def __init__(self, message: str = "Ada conflict dengan data sedia ada! ⚠️"):
        super().__init__(
            status_code=409,
            error_code="CONFLICT",
            message=message
        )


class ValidationError(AppException):
    """Validation error."""
    
    def __init__(self, message: str = "Data tak valid!", details: Optional[Any] = None):
        super().__init__(
            status_code=422,
            error_code="VALIDATION_ERROR",
            message=message,
            details=details
        )
