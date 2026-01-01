import logging
import json
import sys
from datetime import datetime
from typing import Any, Dict, Optional


class StructuredLogger:
    """Structured JSON logger"""
    
    def __init__(self, name: str, level: str = "INFO"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # Remove existing handlers
        self.logger.handlers = []
        
        # Create console handler with JSON formatter
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        self.logger.addHandler(handler)
    
    def _log(self, level: str, message: str, **kwargs):
        """Log with structured data"""
        extra = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "message": message,
            **kwargs
        }
        getattr(self.logger, level.lower())(json.dumps(extra))
    
    def info(self, message: str, **kwargs):
        self._log("INFO", message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        self._log("WARNING", message, **kwargs)
    
    def error(self, message: str, **kwargs):
        self._log("ERROR", message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        self._log("DEBUG", message, **kwargs)


class JSONFormatter(logging.Formatter):
    """JSON formatter for logs"""
    
    def format(self, record: logging.LogRecord) -> str:
        # If already a JSON string, return as-is
        if isinstance(record.msg, str) and record.msg.startswith('{'):
            return record.msg
        return super().format(record)


def get_logger(name: str) -> StructuredLogger:
    """Get structured logger instance"""
    import os
    log_level = os.getenv("LOG_LEVEL", "INFO")
    return StructuredLogger(name, log_level)

