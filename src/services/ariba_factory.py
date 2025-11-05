"""Factory for Ariba service - returns mock or real service based on configuration."""

from src.config.settings import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


def get_ariba_service():
    """
    Get the appropriate Ariba service based on configuration.

    Returns:
        AribaService or AribaMockService instance
    """
    if settings.ariba_use_mock:
        logger.info("🎭 Initializing MOCK Ariba service (no real API calls)")
        from src.services.ariba_mock_service import ariba_mock_service
        return ariba_mock_service
    else:
        logger.info("🌐 Initializing REAL Ariba service (live API)")
        from src.services.ariba_service import ariba_service
        return ariba_service


# Global Ariba service instance (mock or real based on config)
ariba = get_ariba_service()
