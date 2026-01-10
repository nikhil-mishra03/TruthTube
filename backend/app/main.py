"""
TruthTube - YouTube Video Quality Analyzer

FastAPI application entry point.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.models.database import db
from app.api.routes import router
from app.utils.logging import setup_logging, get_logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup/shutdown."""
    # Startup
    logger = setup_logging()
    logger.info("Starting TruthTube API...")
    
    settings = get_settings()
    logger.info(f"Environment: {settings.environment}")
    
    # Initialize database
    try:
        await db.init()
    except Exception as e:
        logger.warning(f"Database initialization skipped: {e}")
        logger.info("Running without database persistence")
    
    yield
    
    # Shutdown
    logger.info("Shutting down TruthTube API...")
    await db.close()


# Create FastAPI app
settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Analyze YouTube videos for content quality and information density",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes with /api prefix
app.include_router(router, prefix="/api")

# Include agent testing routes (for debugging)
from app.api.agents import router as agents_router
app.include_router(agents_router, prefix="/api")


# For development: allow running with python -m app.main
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
