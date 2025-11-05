"""Main application entry point with aiohttp."""

import sys
import traceback
from aiohttp import web
from aiohttp.web import Request, Response, json_response
from botbuilder.core import (
    BotFrameworkAdapter,
    BotFrameworkAdapterSettings,
    TurnContext,
)
from botbuilder.schema import Activity

from src.config.settings import settings
from src.bot.teams_bot import TeamsBot
from src.services.cache_service import cache_service
from src.api.health import HealthChecker
from src.utils.logger import get_logger

logger = get_logger(__name__)


# Bot adapter configuration
ADAPTER_SETTINGS = BotFrameworkAdapterSettings(
    app_id=settings.microsoft_app_id,
    app_password=settings.microsoft_app_password,
)

# If tenant ID is specified, configure for Single Tenant bot
if settings.microsoft_app_tenant_id:
    logger.info(f"Configuring Single Tenant bot with tenant: {settings.microsoft_app_tenant_id}")
    # For Single Tenant bots, the tenant ID should be used in authentication
    # This is handled automatically by the SDK when app_id and app_password are set

# Create adapter
ADAPTER = BotFrameworkAdapter(ADAPTER_SETTINGS)


# Error handler
async def on_error(context: TurnContext, error: Exception):
    """
    Handle adapter errors.

    Args:
        context: Turn context
        error: Exception that occurred
    """
    logger.error(f"Bot error: {error}", exc_info=True)
    logger.error(f"Traceback: {traceback.format_exc()}")

    # Try to send error message to user, but don't fail if we can't
    try:
        await context.send_activity(
            "Lo siento, ocurrió un error al procesar tu solicitud. "
            "Por favor intenta de nuevo más tarde."
        )
    except Exception as send_error:
        logger.error(f"Failed to send error message: {send_error}")


ADAPTER.on_turn_error = on_error


# Create bot instance
BOT = TeamsBot()


# Routes
async def messages(req: Request) -> Response:
    """
    Main endpoint for Bot Framework messages.

    Args:
        req: HTTP request

    Returns:
        HTTP response
    """
    try:
        # Parse activity
        if "application/json" in req.headers.get("Content-Type", ""):
            body = await req.json()
        else:
            return Response(status=415, text="Unsupported Media Type")

        activity = Activity().deserialize(body)

        # Create auth header
        auth_header = req.headers.get("Authorization", "")

        # Process activity
        async def aux_func(turn_context: TurnContext):
            await BOT.on_turn(turn_context)

        await ADAPTER.process_activity(activity, auth_header, aux_func)

        return Response(status=200)

    except Exception as e:
        logger.error(f"Error processing message: {e}", exc_info=True)
        return Response(status=500, text=str(e))


async def health(req: Request) -> Response:
    """Health check endpoint."""
    try:
        health_status = await HealthChecker.check_health()
        return json_response(health_status)
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return json_response(
            {"status": "unhealthy", "error": str(e)}, status=500
        )


async def ready(req: Request) -> Response:
    """Readiness check endpoint."""
    try:
        readiness_status = await HealthChecker.check_readiness()
        status_code = 200 if readiness_status["status"] == "ready" else 503
        return json_response(readiness_status, status=status_code)
    except Exception as e:
        logger.error(f"Readiness check error: {e}")
        return json_response(
            {"status": "not_ready", "error": str(e)}, status=503
        )


async def live(req: Request) -> Response:
    """Liveness check endpoint."""
    try:
        liveness_status = await HealthChecker.check_liveness()
        return json_response(liveness_status)
    except Exception as e:
        logger.error(f"Liveness check error: {e}")
        return json_response(
            {"status": "dead", "error": str(e)}, status=500
        )


async def index(req: Request) -> Response:
    """Root endpoint."""
    return json_response(
        {
            "name": "Azure MS Teams Bot with SAP Ariba Integration",
            "version": "1.0.0",
            "status": "running",
            "endpoints": {
                "messages": "/api/messages",
                "health": "/api/health",
                "ready": "/api/health/ready",
                "live": "/api/health/live",
            },
        }
    )


# Lifecycle handlers
async def on_startup(app: web.Application):
    """
    Handle application startup.

    Args:
        app: Application instance
    """
    logger.info("Starting Azure Teams Bot...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Port: {settings.port}")

    # Initialize cache
    try:
        await cache_service.connect()
        logger.info("Cache service initialized")
    except Exception as e:
        logger.warning(f"Cache service initialization failed: {e}")

    logger.info("Bot started successfully!")


async def on_shutdown(app: web.Application):
    """
    Handle application shutdown.

    Args:
        app: Application instance
    """
    logger.info("Shutting down Azure Teams Bot...")

    # Disconnect cache
    try:
        await cache_service.disconnect()
        logger.info("Cache service disconnected")
    except Exception as e:
        logger.warning(f"Cache service disconnection failed: {e}")

    logger.info("Bot shut down successfully")


def create_app() -> web.Application:
    """
    Create and configure the application.

    Returns:
        Configured application
    """
    app = web.Application()

    # Register routes
    app.router.add_get("/", index)
    app.router.add_post("/api/messages", messages)
    app.router.add_get("/api/health", health)
    app.router.add_get("/api/health/ready", ready)
    app.router.add_get("/api/health/live", live)

    # Register lifecycle handlers
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    return app


def main():
    """Main entry point."""
    try:
        app = create_app()

        logger.info(f"Starting server on port {settings.port}...")

        web.run_app(
            app,
            host="0.0.0.0",
            port=settings.port,
            print=lambda x: logger.info(x),
        )

    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
