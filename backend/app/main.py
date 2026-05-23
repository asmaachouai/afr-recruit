"""
AFR-Recruit — AI Recruitment Fairness Platform
Main FastAPI application entry point
"""

import logging
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.core.config import settings
from app.core.logging import configure_logging

configure_logging()
logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — startup and shutdown events."""
    logger.info("Starting AFR-Recruit API", environment=settings.APP_ENV)
    # DB connection pool, ML model loading, FAISS index will be initialized here
    yield
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

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint — used by Docker and load balancers."""
    return {"status": "healthy", "service": "afr-recruit-api", "version": "1.0.0"}


@app.get("/", tags=["Root"])
async def root():
    return {"message": "AFR-Recruit API", "docs": "/api/docs"}
