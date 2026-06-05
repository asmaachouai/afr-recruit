"""
AFR-Recruit API — main application entry point.
"""

import sys

if sys.platform == "win32":
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import logging
from contextlib import asynccontextmanager
from app.api.v1.candidates import router as candidates_router
from app.api.v1.jobs import router as jobs_router
from app.api.v1.fairness import router as fairness_router

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from huggingface_hub import login

from app.core.config import settings
from app.core.logging import configure_logging
from app.core.redis import close_redis
from app.api.v1.auth import router as auth_router

configure_logging()
logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting AFR-Recruit API", environment=settings.APP_ENV)

    # Pre-load ML models in background so first request is fast
    import asyncio
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _preload_models)

    yield
    await close_redis()
    logger.info("Shutting down AFR-Recruit API")


def _preload_models():
    """Load heavy ML models at startup instead of on first request."""
    try:
        import os
        from app.core.config import settings
        if settings.HF_TOKEN:
            os.environ["HF_TOKEN"] = settings.HF_TOKEN
            os.environ["HUGGING_FACE_HUB_TOKEN"] = settings.HF_TOKEN

        from app.ml.models.embedding_service import embedding_service
        embedding_service.load()
    except Exception as e:
        pass
    try:
        from app.ml.models.embedding_service import embedding_service
        embedding_service.load()
    except Exception as e:
        pass  # non-fatal — model will load on first request


app = FastAPI(
    title="AFR-Recruit API",
    description="AI-powered multilingual recruitment fairness platform for Morocco and Francophone Africa",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Register routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(candidates_router, prefix="/api/v1")
app.include_router(jobs_router, prefix="/api/v1")
app.include_router(fairness_router, prefix="/api/v1")




@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "service": "afr-recruit-api", "version": "1.0.0"}


@app.get("/", tags=["Root"])
async def root():
    return {"message": "AFR-Recruit API", "docs": "/api/docs"}