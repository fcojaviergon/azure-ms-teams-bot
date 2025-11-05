"""Authentication service for OAuth2 and token management."""

import time
from typing import Optional
import httpx
from datetime import datetime, timedelta

from src.config.settings import settings
from src.utils.logger import get_logger
from src.services.cache_service import cache_service

logger = get_logger(__name__)


class AuthService:
    """OAuth2 authentication service for SAP Ariba."""

    def __init__(self):
        """Initialize auth service."""
        self.token_cache_key = "auth:ariba:token"
        self.token: Optional[str] = None
        self.token_expiry: Optional[datetime] = None

    async def get_ariba_token(self, force_refresh: bool = False) -> str:
        """
        Get OAuth2 access token for SAP Ariba.

        Args:
            force_refresh: Force token refresh even if cached

        Returns:
            Access token

        Raises:
            Exception: If token acquisition fails
        """
        # Check cache if not forcing refresh
        if not force_refresh:
            cached_token = await cache_service.get(self.token_cache_key)
            if cached_token:
                logger.debug("Using cached Ariba token")
                return cached_token

        # Request new token
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    settings.ariba_oauth_token_url,
                    data={
                        "grant_type": "client_credentials",
                        "client_id": settings.ariba_client_id,
                        "client_secret": settings.ariba_client_secret,
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    timeout=30.0,
                )

                response.raise_for_status()
                token_data = response.json()

                access_token = token_data["access_token"]
                expires_in = token_data.get("expires_in", 3600)

                # Cache token with buffer (expires 5 minutes early)
                cache_ttl = max(expires_in - 300, 60)
                await cache_service.set(
                    self.token_cache_key, access_token, ttl=cache_ttl
                )

                logger.info(f"Successfully obtained Ariba token (expires in {expires_in}s)")
                return access_token

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error obtaining Ariba token: {e.response.status_code}")
            raise Exception(f"Failed to obtain Ariba token: {e}")
        except Exception as e:
            logger.error(f"Error obtaining Ariba token: {e}")
            raise

    async def validate_token(self, token: str) -> bool:
        """
        Validate an OAuth2 token.

        Args:
            token: Token to validate

        Returns:
            True if valid, False otherwise
        """
        # For now, just check if token exists and is not empty
        # In production, you might want to call a token validation endpoint
        return bool(token and len(token) > 0)

    async def revoke_token(self) -> bool:
        """
        Revoke the current access token.

        Returns:
            True if successful, False otherwise
        """
        try:
            # Clear cached token
            await cache_service.delete(self.token_cache_key)
            self.token = None
            self.token_expiry = None
            logger.info("Ariba token revoked")
            return True
        except Exception as e:
            logger.error(f"Error revoking token: {e}")
            return False


# Global auth service instance
auth_service = AuthService()
