"""
Structured logging configuration for DesignMentor AI.
"""

import logging
import sys
from typing import Any


def configure_logging(level: str = "INFO", fmt: str = "text") -> None:
    """
    Configure application logging.

    Args:
        level: Log level string (DEBUG, INFO, WARNING, ERROR)
        fmt:   "text" for human-readable, "json" for structured JSON logs
    """
    log_level = getattr(logging, level.upper(), logging.INFO)

    if fmt == "json":
        try:
            import json

            class JsonFormatter(logging.Formatter):
                def format(self, record: logging.LogRecord) -> str:  # type: ignore[override]
                    log_record: dict[str, Any] = {
                        "timestamp": self.formatTime(record),
                        "level": record.levelname,
                        "logger": record.name,
                        "message": record.getMessage(),
                    }
                    if record.exc_info:
                        log_record["exception"] = self.formatException(record.exc_info)
                    return json.dumps(log_record)

            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(JsonFormatter())
        except Exception:
            handler = logging.StreamHandler(sys.stdout)
    else:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter(
                fmt="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )

    # Root logger
    root = logging.getLogger()
    root.setLevel(log_level)
    root.handlers.clear()
    root.addHandler(handler)

    # Silence noisy third-party loggers
    for noisy in ("httpx", "httpcore", "hpack", "watchfiles"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
