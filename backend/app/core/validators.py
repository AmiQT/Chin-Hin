"""
Input Validation Helpers for Chin Hin API.
Common validators for UUIDs, dates, and other inputs.
"""

import re
from uuid import UUID
from datetime import date, datetime
from typing import Optional
from fastapi import HTTPException


def validate_uuid(value: str, field_name: str = "ID") -> UUID:
    """
    Validate and parse UUID string.
    
    Args:
        value: String to validate as UUID
        field_name: Name of field for error message
    
    Returns:
        Parsed UUID object
    
    Raises:
        HTTPException: If invalid UUID format
    """
    try:
        return UUID(value)
    except (ValueError, AttributeError):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid {field_name} format. Expected UUID."
        )


def validate_date(value: str, field_name: str = "date") -> date:
    """
    Validate and parse date string (YYYY-MM-DD).
    
    Args:
        value: String to validate as date
        field_name: Name of field for error message
    
    Returns:
        Parsed date object
    
    Raises:
        HTTPException: If invalid date format
    """
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (ValueError, AttributeError):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid {field_name} format. Expected YYYY-MM-DD."
        )


def validate_datetime(value: str, field_name: str = "datetime") -> datetime:
    """
    Validate and parse datetime string (ISO format).
    
    Args:
        value: String to validate as datetime
        field_name: Name of field for error message
    
    Returns:
        Parsed datetime object
    
    Raises:
        HTTPException: If invalid datetime format
    """
    try:
        # Support both with and without timezone
        if value.endswith("Z"):
            value = value[:-1] + "+00:00"
        return datetime.fromisoformat(value)
    except (ValueError, AttributeError):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid {field_name} format. Expected ISO datetime."
        )


def validate_email(value: str) -> str:
    """
    Validate email format.
    
    Args:
        value: String to validate as email
    
    Returns:
        Lowercase email string
    
    Raises:
        HTTPException: If invalid email format
    """
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, value):
        raise HTTPException(
            status_code=400,
            detail="Invalid email format."
        )
    return value.lower()


def validate_amount(
    value: float, 
    min_amount: float = 0.01, 
    max_amount: Optional[float] = None,
    field_name: str = "amount"
) -> float:
    """
    Validate monetary amount.
    
    Args:
        value: Amount to validate
        min_amount: Minimum allowed amount
        max_amount: Maximum allowed amount (optional)
        field_name: Name of field for error message
    
    Returns:
        Validated amount
    
    Raises:
        HTTPException: If amount out of range
    """
    if value < min_amount:
        raise HTTPException(
            status_code=400,
            detail=f"{field_name} must be at least RM{min_amount:.2f}."
        )
    
    if max_amount and value > max_amount:
        raise HTTPException(
            status_code=400,
            detail=f"{field_name} cannot exceed RM{max_amount:.2f}."
        )
    
    return round(value, 2)


def validate_date_range(start_date: date, end_date: date) -> tuple[date, date]:
    """
    Validate that start_date <= end_date.
    
    Args:
        start_date: Start of date range
        end_date: End of date range
    
    Returns:
        Tuple of (start_date, end_date)
    
    Raises:
        HTTPException: If end_date before start_date
    """
    if end_date < start_date:
        raise HTTPException(
            status_code=400,
            detail="End date cannot be before start date."
        )
    return (start_date, end_date)


def validate_future_date(value: date, field_name: str = "date") -> date:
    """
    Validate that date is today or in the future.
    
    Args:
        value: Date to validate
        field_name: Name of field for error message
    
    Returns:
        Validated date
    
    Raises:
        HTTPException: If date is in the past
    """
    if value < date.today():
        raise HTTPException(
            status_code=400,
            detail=f"{field_name} cannot be in the past."
        )
    return value


def sanitize_string(value: str, max_length: int = 500) -> str:
    """
    Sanitize string input - trim whitespace and limit length.
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length
    
    Returns:
        Sanitized string
    """
    if not value:
        return ""
    
    # Trim whitespace
    sanitized = value.strip()
    
    # Limit length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized
