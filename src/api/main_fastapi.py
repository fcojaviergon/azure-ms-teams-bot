"""Main FastAPI application entry point."""

import sys
import traceback
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
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
    logger.error(f"Bot error: {error}")
    logger.error(f"Error type: {type(error).__name__}")

    # Check if it's an authentication error
    error_str = str(error)
    if "access_token" in error_str.lower() or "unauthorized" in error_str.lower():
        logger.error("❌ Authentication error detected!")
        logger.error("❌ Check that MICROSOFT_APP_ID and MICROSOFT_APP_PASSWORD are correctly configured")
        logger.error("❌ See docs/AUTHENTICATION.md for help")
        return

    logger.error(f"Traceback: {traceback.format_exc()}")

    # Try to send error message to user (may fail if auth is broken)
    try:
        await context.send_activity(
            "Lo siento, ocurrió un error al procesar tu solicitud. "
            "Por favor intenta de nuevo más tarde."
        )
    except Exception as send_error:
        logger.error(f"Could not send error message to user: {send_error}")


ADAPTER.on_turn_error = on_error


# Create bot instance
BOT = TeamsBot()


# FastAPI app
app = FastAPI(
    title="Azure MS Teams Bot with SAP Ariba Integration",
    description="Bot inteligente con FastAPI, PostgreSQL y Azure OpenAI",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Routes
@app.post("/api/messages")
async def messages(request: Request):
    """
    Main endpoint for Bot Framework messages.

    Args:
        request: HTTP request

    Returns:
        JSON response
    """
    try:
        # Check content type
        if "application/json" not in request.headers.get("content-type", ""):
            raise HTTPException(status_code=415, detail="Unsupported Media Type")

        # Parse activity
        body = await request.json()
        activity = Activity().deserialize(body)

        # Get auth header
        auth_header = request.headers.get("authorization", "")

        # Process activity
        async def aux_func(turn_context: TurnContext):
            await BOT.on_turn(turn_context)

        await ADAPTER.process_activity(activity, auth_header, aux_func)

        return JSONResponse(content={"status": "ok"}, status_code=200)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing message: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health():
    """Health check endpoint."""
    try:
        health_status = await HealthChecker.check_health()
        return JSONResponse(content=health_status)
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return JSONResponse(
            content={"status": "unhealthy", "error": str(e)},
            status_code=500
        )


@app.get("/api/health/ready")
async def ready():
    """Readiness check endpoint."""
    try:
        readiness_status = await HealthChecker.check_readiness()
        status_code = 200 if readiness_status["status"] == "ready" else 503
        return JSONResponse(content=readiness_status, status_code=status_code)
    except Exception as e:
        logger.error(f"Readiness check error: {e}")
        return JSONResponse(
            content={"status": "not_ready", "error": str(e)},
            status_code=503
        )


@app.get("/api/health/live")
async def live():
    """Liveness check endpoint."""
    try:
        liveness_status = await HealthChecker.check_liveness()
        return JSONResponse(content=liveness_status)
    except Exception as e:
        logger.error(f"Liveness check error: {e}")
        return JSONResponse(
            content={"status": "dead", "error": str(e)},
            status_code=500
        )


@app.get("/")
async def index():
    """Root endpoint."""
    return {
        "name": "Azure MS Teams Bot with SAP Ariba Integration",
        "version": "2.0.0",
        "framework": "FastAPI",
        "database": "PostgreSQL with pgvector",
        "status": "running",
        "endpoints": {
            "messages": "/api/messages",
            "health": "/api/health",
            "ready": "/api/health/ready",
            "live": "/api/health/live",
            "docs": "/docs",
            "redoc": "/redoc",
        },
    }


# Lifecycle events
@app.on_event("startup")
async def on_startup():
    """Handle application startup."""
    logger.info("Starting Azure Teams Bot with FastAPI...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Port: {settings.port}")

    # Validate bot credentials
    if not settings.microsoft_app_id or not settings.microsoft_app_password:
        logger.warning("⚠️  Bot credentials (MICROSOFT_APP_ID/PASSWORD) not configured!")
        logger.warning("⚠️  The bot will NOT work with Microsoft Teams without valid credentials.")
        logger.warning("⚠️  Options:")
        logger.warning("   1. Configure valid Azure Bot credentials in .env")
        logger.warning("   2. Use Bot Framework Emulator for local testing")
        logger.warning("   3. See docs/AUTHENTICATION.md for more info")
    else:
        logger.info(f"✅ Bot credentials configured (App ID: {settings.microsoft_app_id[:8]}...)")

    # Check Ariba mode
    if settings.ariba_use_mock:
        logger.info("🎭 Ariba MOCK mode enabled - using simulated data")
    else:
        logger.info("🌐 Ariba REAL mode enabled - using live API")

    # Initialize cache
    try:
        await cache_service.connect()
        logger.info("✅ Cache service initialized")
    except Exception as e:
        logger.warning(f"⚠️  Cache service initialization failed: {e}")

    logger.info("✅ Bot started successfully with FastAPI!")
    logger.info(f"📚 API Documentation available at http://localhost:{settings.port}/docs")


@app.on_event("shutdown")
async def on_shutdown():
    """Handle application shutdown."""
    logger.info("Shutting down Azure Teams Bot...")

    # Disconnect cache
    try:
        await cache_service.disconnect()
        logger.info("Cache service disconnected")
    except Exception as e:
        logger.warning(f"Cache service disconnection failed: {e}")

    logger.info("Bot shut down successfully")


# For development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.main_fastapi:app",
        host="0.0.0.0",
        port=settings.port,
        reload=True,
        log_level="info"
    )
