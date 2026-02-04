"""
Core module - exceptions, logging, middleware, validators.
"""

from app.core.exceptions import (
    AppException,
    NotFoundError,
    UnauthorizedError,
    ForbiddenError,
    ConflictError,
    ValidationError,
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler,
)
from app.core.logging import setup_logging, get_request_logger
from app.core.middleware import RequestMiddleware, RateLimitMiddleware, SecurityHeadersMiddleware
from app.core.validators import (
    validate_uuid,
    validate_date,
    validate_datetime,
    validate_email,
    validate_amount,
    validate_date_range,
    validate_future_date,
    sanitize_string,
)

__all__ = [
    # Exceptions
    "AppException",
    "NotFoundError",
    "UnauthorizedError",
    "ForbiddenError",
    "ConflictError",
    "ValidationError",
    # Handlers
    "http_exception_handler",
    "validation_exception_handler",
    "general_exception_handler",
    # Logging
    "setup_logging",
    "get_request_logger",
    # Middleware
    "RequestMiddleware",
    "RateLimitMiddleware",
    "SecurityHeadersMiddleware",
    # Validators
    "validate_uuid",
    "validate_date",
    "validate_datetime",
    "validate_email",
    "validate_amount",
    "validate_date_range",
    "validate_future_date",
    "sanitize_string",
]
