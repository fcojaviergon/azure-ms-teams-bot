"""Logging configuration with Application Insights integration."""

import logging
import sys
from typing import Optional
from pythonjsonlogger import jsonlogger

from src.config.settings import settings


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter for structured logging."""

    def add_fields(self, log_record, record, message_dict):
        """Add custom fields to log records."""
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        log_record["environment"] = settings.environment
        log_record["service"] = "teams-bot"


def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    Get a configured logger instance.

    Args:
        name: Logger name (typically __name__)
        level: Optional log level override

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Set log level
    log_level = level or settings.log_level
    logger.setLevel(getattr(logging, log_level.upper()))

    # Remove existing handlers
    logger.handlers = []

    # Console handler with JSON formatting
    console_handler = logging.StreamHandler(sys.stdout)

    if settings.environment == "production":
        formatter = CustomJsonFormatter(
            "%(timestamp)s %(level)s %(name)s %(message)s",
            rename_fields={"levelname": "level", "asctime": "timestamp"},
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Application Insights handler
    if settings.appinsights_connection_string:
        try:
            from opencensus.ext.azure.log_exporter import AzureLogHandler

            ai_handler = AzureLogHandler(
                connection_string=settings.appinsights_connection_string
            )
            logger.addHandler(ai_handler)
        except ImportError:
            logger.warning(
                "Application Insights SDK not available. Install opencensus-ext-azure."
            )

    return logger
