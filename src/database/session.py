"""Database session management."""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from src.config.settings import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Base class for models
Base = declarative_base()

# Database URL
# Format: postgresql+asyncpg://user:password@host:port/database
DATABASE_URL = f"postgresql+asyncpg://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_database}"

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=settings.debug,  # Log SQL queries in debug mode
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verify connections before using
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db():
    """
    Dependency for FastAPI to get database session.

    Yields:
        AsyncSession: Database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize database - create tables."""
    async with engine.begin() as conn:
        logger.info("Creating database tables...")
        await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Database tables created")


async def close_db():
    """Close database engine."""
    await engine.dispose()
    logger.info("Database engine disposed")
