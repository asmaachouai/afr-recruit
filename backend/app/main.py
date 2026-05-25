"""
AFR-Recruit API — main application entry point.
"""

import sys

if sys.platform == "win32":
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import logging
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.core.config import settings
from app.core.logging import configure_logging
from app.core.redis import close_redis
from app.api.v1.auth import router as auth_router

configure_logging()
logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting AFR-Recruit API", environment=settings.APP_ENV)
    yield
    await close_redis()
    logger.info("Shutting down AFR-Recruit API")


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


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "service": "afr-recruit-api", "version": "1.0.0"}


@app.get("/", tags=["Root"])
async def root():
    return {"message": "AFR-Recruit API", "docs": "/api/docs"}