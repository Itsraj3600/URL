"""
Centralized logging configuration for CINE3600.

Provides structured JSON logging with better formatting, error handling, and performance tracking.
Features:
- Colored console output for development
- JSON file logging for structured analysis
- Rotating file handlers with automatic cleanup
- Performance context tracking
- Worker/module identification in logs
"""

import logging
import logging.handlers
import sys
import json
import os
from datetime import datetime
from os import environ
from typing import Optional, Dict, Any

# Logging configuration
LOG_LEVEL = environ.get("LOG_LEVEL", "INFO").upper()
LOG_FILE = environ.get("LOG_FILE", "cine3600.log")
LOG_MAX_BYTES = int(environ.get("LOG_MAX_BYTES", 10485760))  # 10MB
LOG_BACKUP_COUNT = int(environ.get("LOG_BACKUP_COUNT", 5))


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colored output for console logs."""
    
    COLORS = {
        "DEBUG": "\033[36m",      # Cyan
        "INFO": "\033[32m",       # Green
        "WARNING": "\033[33m",    # Yellow
        "ERROR": "\033[31m",      # Red
        "CRITICAL": "\033[35m",   # Magenta
    }
    RESET = "\033[0m"
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with color."""
        level_color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{level_color}{record.levelname}{self.RESET}"
        return super().format(record)


class StructuredJSONFormatter(logging.Formatter):
    """Formatter that outputs structured JSON logs."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON for structured logging."""
        log_data = {
            "timestamp": datetime.utcfromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "message": record.getMessage(),
        }
        
        # Add worker info if available
        if hasattr(record, "worker"):
            log_data["worker"] = record.worker
        
        # Add custom context data
        if hasattr(record, "context"):
            log_data["context"] = record.context
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)


def setup_logging() -> None:
    """
    Configure application-wide logging with console and file handlers.
    
    Sets up:
    - Console handler with colored output
    - Text file handler with rotation
    - JSON file handler for structured analysis
    - Timestamp and worker identification
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, LOG_LEVEL))
    
    # Remove existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Log format
    log_format = "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Console handler with colored output
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, LOG_LEVEL))
    console_formatter = ColoredFormatter(log_format, datefmt=date_format)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # Text file handler with rotation
    try:
        file_handler = logging.handlers.RotatingFileHandler(
            LOG_FILE,
            maxBytes=LOG_MAX_BYTES,
            backupCount=LOG_BACKUP_COUNT
        )
        file_handler.setLevel(logging.DEBUG)  # Always log DEBUG to file
        file_formatter = logging.Formatter(log_format, datefmt=date_format)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
    except Exception as e:
        print(f"Failed to setup text file logging: {e}", file=sys.stderr)
    
    # JSON structured log file handler for analytics
    try:
        json_log_file = environ.get("JSON_LOG_FILE", "cine3600_structured.jsonl")
        json_handler = logging.handlers.RotatingFileHandler(
            json_log_file,
            maxBytes=LOG_MAX_BYTES,
            backupCount=LOG_BACKUP_COUNT
        )
        json_handler.setLevel(logging.DEBUG)
        json_formatter = StructuredJSONFormatter()
        json_handler.setFormatter(json_formatter)
        root_logger.addHandler(json_handler)
    except Exception as e:
        print(f"Failed to setup JSON logging: {e}", file=sys.stderr)


def get_logger(name: str) -> logging.Logger:
    """
    Get a configured logger instance.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


class StructuredLogger:
    """Wrapper for structured logging with context."""
    
    def __init__(self, name: str, worker_id: Optional[str] = None):
        """Initialize structured logger."""
        self.logger = logging.getLogger(name)
        self.worker_id = worker_id
    
    def info(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Log info with optional context."""
        record = self.logger.makeRecord(
            self.logger.name, logging.INFO, "", 0, message, (), None
        )
        if self.worker_id:
            record.worker = self.worker_id
        if context:
            record.context = context
        self.logger.handle(record)
    
    def error(self, message: str, context: Optional[Dict[str, Any]] = None, exc_info: bool = False) -> None:
        """Log error with optional context."""
        record = self.logger.makeRecord(
            self.logger.name, logging.ERROR, "", 0, message, (), None, exc_info=exc_info
        )
        if self.worker_id:
            record.worker = self.worker_id
        if context:
            record.context = context
        self.logger.handle(record)
    
    def warning(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Log warning with optional context."""
        record = self.logger.makeRecord(
            self.logger.name, logging.WARNING, "", 0, message, (), None
        )
        if self.worker_id:
            record.worker = self.worker_id
        if context:
            record.context = context
        self.logger.handle(record)
    
    def debug(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Log debug with optional context."""
        record = self.logger.makeRecord(
            self.logger.name, logging.DEBUG, "", 0, message, (), None
        )
        if self.worker_id:
            record.worker = self.worker_id
        if context:
            record.context = context
        self.logger.handle(record)


# Initialize logging when module is imported
setup_logging()
