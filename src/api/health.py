"""Health check endpoints."""

from typing import Dict, Any
from datetime import datetime
import sys

from src.config.settings import settings
from src.services.cache_service import cache_service
from src.utils.logger import get_logger

logger = get_logger(__name__)


class HealthChecker:
    """Health check service."""

    @staticmethod
    async def check_health() -> Dict[str, Any]:
        """
        Perform basic health check.

        Returns:
            Health status
        """
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "environment": settings.environment,
        }

    @staticmethod
    async def check_readiness() -> Dict[str, Any]:
        """
        Perform readiness check (dependencies).

        Returns:
            Readiness status
        """
        checks = {}
        all_healthy = True

        # Check Redis
        try:
            if cache_service.client:
                await cache_service.client.ping()
                checks["redis"] = {"status": "healthy"}
            else:
                checks["redis"] = {"status": "not_connected"}
                all_healthy = False
        except Exception as e:
            checks["redis"] = {"status": "unhealthy", "error": str(e)}
            all_healthy = False

        # Check Azure OpenAI (basic connectivity)
        try:
            # Just check if settings are configured
            if settings.azure_openai_endpoint and settings.azure_openai_api_key:
                checks["openai"] = {"status": "configured"}
            else:
                checks["openai"] = {"status": "not_configured"}
                all_healthy = False
        except Exception as e:
            checks["openai"] = {"status": "unhealthy", "error": str(e)}
            all_healthy = False

        # Check Cognitive Search
        try:
            if settings.azure_search_endpoint and settings.azure_search_api_key:
                checks["cognitive_search"] = {"status": "configured"}
            else:
                checks["cognitive_search"] = {"status": "not_configured"}
                all_healthy = False
        except Exception as e:
            checks["cognitive_search"] = {"status": "unhealthy", "error": str(e)}
            all_healthy = False

        # Check Ariba
        try:
            if settings.ariba_api_base_url and settings.ariba_client_id:
                checks["ariba"] = {"status": "configured"}
            else:
                checks["ariba"] = {"status": "not_configured"}
                all_healthy = False
        except Exception as e:
            checks["ariba"] = {"status": "unhealthy", "error": str(e)}
            all_healthy = False

        return {
            "status": "ready" if all_healthy else "not_ready",
            "timestamp": datetime.utcnow().isoformat(),
            "checks": checks,
        }

    @staticmethod
    async def check_liveness() -> Dict[str, Any]:
        """
        Perform liveness check (is app alive).

        Returns:
            Liveness status
        """
        return {
            "status": "alive",
            "timestamp": datetime.utcnow().isoformat(),
            "python_version": sys.version,
        }
