# backend/app/core/logging.py
import logging
import sys
from logging.config import dictConfig
from ..core.config import settings

def setup_logging():
    """Configure logging with JSON format if not in debug mode."""
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
            "json": {
                "format": '{"time": "%(asctime)s", "name": "%(name)s", "level": "%(levelname)s", "message": "%(message)s"}',
                "datefmt": "%Y-%m-%dT%H:%M:%S%z",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "stream": sys.stdout,
                "formatter": "json" if not settings.DEBUG else "default",
            },
        },
        "root": {
            "level": log_level,
            "handlers": ["console"],
        },
    }

    dictConfig(config)