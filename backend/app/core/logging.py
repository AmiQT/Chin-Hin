"""
Structured Logging Configuration.
JSON format untuk production, pretty format untuk development! 📝
"""

import logging
import sys
import json
from datetime import datetime
from typing import Any, Optional
from uuid import uuid4


class JSONFormatter(logging.Formatter):
    """JSON formatter untuk production logs."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add extra fields if present
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if hasattr(record, "path"):
            log_data["path"] = record.path
        if hasattr(record, "method"):
            log_data["method"] = record.method
        if hasattr(record, "status_code"):
            log_data["status_code"] = record.status_code
        if hasattr(record, "duration_ms"):
            log_data["duration_ms"] = record.duration_ms
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data, ensure_ascii=False)


class PrettyFormatter(logging.Formatter):
    """Pretty formatter untuk development (colorful)! 🌈"""
    
    COLORS = {
        "DEBUG": "\033[36m",     # Cyan
        "INFO": "\033[32m",      # Green
        "WARNING": "\033[33m",   # Yellow
        "ERROR": "\033[31m",     # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"
    
    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, "")
        reset = self.RESET
        
        # Format timestamp
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Build prefix
        prefix = f"{color}[{timestamp}] {record.levelname:8}{reset}"
        
        # Add request ID if present
        request_id = getattr(record, "request_id", None)
        if request_id:
            prefix += f" [{request_id[:8]}]"
        
        # Format message
        message = record.getMessage()
        
        return f"{prefix} {message}"


def setup_logging(environment: str = "development", log_level: str = "INFO"):
    """
    Setup logging configuration.
    
    Args:
        environment: 'development' or 'production'
        log_level: DEBUG, INFO, WARNING, ERROR, CRITICAL
    """
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    
    # Choose formatter based on environment
    if environment == "production":
        formatter = JSONFormatter()
    else:
        formatter = PrettyFormatter()
    
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Set log levels for noisy libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    
    return root_logger


class LogContext:
    """Context manager untuk add extra fields to logs."""
    
    def __init__(self, **kwargs):
        self.extra = kwargs
    
    def get_logger(self, name: str) -> logging.LoggerAdapter:
        """Get logger with extra context."""
        logger = logging.getLogger(name)
        return logging.LoggerAdapter(logger, self.extra)


def get_request_logger(
    request_id: str,
    user_id: Optional[str] = None,
    path: Optional[str] = None,
    method: Optional[str] = None
) -> logging.LoggerAdapter:
    """Get logger with request context."""
    extra = {
        "request_id": request_id,
    }
    if user_id:
        extra["user_id"] = user_id
    if path:
        extra["path"] = path
    if method:
        extra["method"] = method
    
    logger = logging.getLogger("app.request")
    return logging.LoggerAdapter(logger, extra)
