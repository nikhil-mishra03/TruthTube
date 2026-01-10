"""
Async database configuration using SQLAlchemy 2.0.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, DateTime, JSON, Text, Boolean, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from contextlib import asynccontextmanager

from app.config import get_settings
from app.utils.logging import get_logger

logger = get_logger(__name__)


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


# ============================================================================
# Database Models
# ============================================================================

class Session(Base):
    """Analysis session - groups multiple video analyses together."""
    __tablename__ = "sessions"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending, processing, completed, failed
    urls: Mapped[dict] = mapped_column(JSON)  # List of submitted URLs
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    video_results: Mapped[list["VideoResult"]] = relationship(back_populates="session", cascade="all, delete-orphan")


class VideoResult(Base):
    """Analysis result for a single video."""
    __tablename__ = "video_results"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("sessions.id"))
    youtube_id: Mapped[str] = mapped_column(String(20))
    title: Mapped[str] = mapped_column(Text)
    duration_seconds: Mapped[int] = mapped_column(Integer)
    thumbnail_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    transcript: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Analysis scores
    density_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    density_details: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    redundancy_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    redundancy_details: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    title_relevance_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    title_relevance_details: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    originality_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    originality_details: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Ranking
    overall_rank: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    recommendation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session: Mapped["Session"] = relationship(back_populates="video_results")


class TranscriptCache(Base):
    """Cache for YouTube transcripts to avoid re-fetching."""
    __tablename__ = "transcript_cache"
    
    youtube_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    transcript: Mapped[str] = mapped_column(Text)
    title: Mapped[str] = mapped_column(Text)
    duration_seconds: Mapped[int] = mapped_column(Integer)
    thumbnail_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    fetched_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# ============================================================================
# Database Connection
# ============================================================================

class DatabaseManager:
    """Manages async database connections."""
    
    def __init__(self):
        self._engine = None
        self._session_factory = None
    
    async def init(self):
        """Initialize database connection."""
        settings = get_settings()
        logger.info(f"Connecting to database: {settings.database_url.split('@')[-1]}")
        
        self._engine = create_async_engine(
            settings.database_url,
            echo=settings.environment == "development",
            pool_pre_ping=True,
        )
        
        self._session_factory = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        
        # Create tables
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("Database initialized successfully")
    
    async def close(self):
        """Close database connection."""
        if self._engine:
            await self._engine.dispose()
            logger.info("Database connection closed")
    
    @asynccontextmanager
    async def session(self):
        """Get a database session."""
        if not self._session_factory:
            raise RuntimeError("Database not initialized. Call init() first.")
        
        async with self._session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise


# Global database manager instance
db = DatabaseManager()
