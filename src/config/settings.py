"""Application settings and configuration."""

import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Azure Bot Service
    microsoft_app_id: str = Field(..., alias="MICROSOFT_APP_ID")
    microsoft_app_password: str = Field(..., alias="MICROSOFT_APP_PASSWORD")
    microsoft_app_tenant_id: Optional[str] = Field(None, alias="MICROSOFT_APP_TENANT_ID")
    bot_id: str = Field(..., alias="BOT_ID")

    # Azure OpenAI
    azure_openai_endpoint: str = Field(..., alias="AZURE_OPENAI_ENDPOINT")
    azure_openai_api_key: str = Field(..., alias="AZURE_OPENAI_API_KEY")
    azure_openai_deployment_name: str = Field(
        default="gpt-4", alias="AZURE_OPENAI_DEPLOYMENT_NAME"
    )
    azure_openai_api_version: str = Field(
        default="2024-02-15-preview", alias="AZURE_OPENAI_API_VERSION"
    )

    # Azure Cognitive Search
    azure_search_endpoint: str = Field(..., alias="AZURE_SEARCH_ENDPOINT")
    azure_search_api_key: str = Field(..., alias="AZURE_SEARCH_API_KEY")
    azure_search_index_name: str = Field(
        default="ariba-knowledge", alias="AZURE_SEARCH_INDEX_NAME"
    )

    # Azure Key Vault
    azure_key_vault_url: Optional[str] = Field(None, alias="AZURE_KEY_VAULT_URL")

    # Azure Redis Cache
    redis_host: str = Field(..., alias="REDIS_HOST")
    redis_port: int = Field(default=6380, alias="REDIS_PORT")
    redis_password: str = Field(..., alias="REDIS_PASSWORD")
    redis_ssl: bool = Field(default=True, alias="REDIS_SSL")

    # SAP Ariba Configuration
    ariba_api_base_url: str = Field(..., alias="ARIBA_API_BASE_URL")
    ariba_api_key: str = Field(..., alias="ARIBA_API_KEY")
    ariba_realm: str = Field(..., alias="ARIBA_REALM")
    ariba_client_id: str = Field(..., alias="ARIBA_CLIENT_ID")
    ariba_client_secret: str = Field(..., alias="ARIBA_CLIENT_SECRET")
    ariba_oauth_token_url: str = Field(..., alias="ARIBA_OAUTH_TOKEN_URL")

    # Application Insights
    appinsights_instrumentation_key: Optional[str] = Field(
        None, alias="APPINSIGHTS_INSTRUMENTATION_KEY"
    )
    appinsights_connection_string: Optional[str] = Field(
        None, alias="APPINSIGHTS_CONNECTION_STRING"
    )

    # Application Settings
    environment: str = Field(default="development", alias="ENVIRONMENT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    debug: bool = Field(default=False, alias="DEBUG")
    port: int = Field(default=3978, alias="PORT")

    # Cache Settings
    cache_ttl_seconds: int = Field(default=3600, alias="CACHE_TTL_SECONDS")
    cache_enabled: bool = Field(default=True, alias="CACHE_ENABLED")

    # Rate Limiting
    rate_limit_enabled: bool = Field(default=True, alias="RATE_LIMIT_ENABLED")
    rate_limit_requests: int = Field(default=100, alias="RATE_LIMIT_REQUESTS")
    rate_limit_period: int = Field(default=60, alias="RATE_LIMIT_PERIOD")

    # Feature Flags
    enable_feedback_loop: bool = Field(default=True, alias="ENABLE_FEEDBACK_LOOP")
    enable_analytics: bool = Field(default=True, alias="ENABLE_ANALYTICS")
    enable_proactive_notifications: bool = Field(
        default=False, alias="ENABLE_PROACTIVE_NOTIFICATIONS"
    )

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        populate_by_name = True


# Global settings instance
settings = Settings()
