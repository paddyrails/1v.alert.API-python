"""Structured logging configuration (JSON-ish, correlation ID via contextvars)."""

import logging
import sys
from contextvars import ContextVar
from typing import Any

correlation_id_ctx: ContextVar[str | None] = ContextVar("correlation_id", default=None)


def get_correlation_id() -> str | None:
    return correlation_id_ctx.get()


def set_correlation_id(value: str | None) -> None:
    correlation_id_ctx.set(value)


class StructuredFormatter(logging.Formatter):
    """Format log records with timestamp, level, message, correlationId, etc."""

    def format(self, record: logging.LogRecord) -> str:
        log_dict: dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
        }
        cid = get_correlation_id()
        if cid:
            log_dict["correlationId"] = cid
        if hasattr(record, "path"):
            log_dict["path"] = record.path
        if hasattr(record, "method"):
            log_dict["method"] = record.method
        if hasattr(record, "statusCode"):
            log_dict["statusCode"] = record.statusCode
        if hasattr(record, "durationMs"):
            log_dict["durationMs"] = record.durationMs
        if record.exc_info:
            log_dict["exception"] = self.formatException(record.exc_info)
        parts = [f"{k}={repr(v)}" for k, v in log_dict.items()]
        return " ".join(parts)


def configure_logging(log_level: str = "INFO") -> None:
    """Configure root logger once at startup."""
    level = getattr(logging, log_level.upper(), logging.INFO)
    root = logging.getLogger()
    root.setLevel(level)
    if not root.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        handler.setFormatter(StructuredFormatter())
        root.addHandler(handler)
