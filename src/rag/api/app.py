from __future__ import annotations

import time

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from rag.api.middleware.rate_limiter import RateLimiterMiddleware
from rag.api.routers import ingest_router, query_router, system_router
from rag.config.logging import setup_logging
from rag.config.settings import get_settings
from rag.monitoring.tracing import setup_tracing

logger = structlog.get_logger(__name__)


def create_app() -> FastAPI:
    settings = get_settings()

    setup_logging()
    setup_tracing()

    app = FastAPI(
        title="Production RAG API",
        description="Production-grade RAG system with MLOps best practices",
        version="1.0.0",
        docs_url="/docs" if settings.api.enable_docs else None,
        redoc_url="/redoc" if settings.api.enable_docs else None,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.api.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(RateLimiterMiddleware)

    Instrumentator().instrument(app).expose(app, endpoint="/metrics")

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        elapsed = time.perf_counter() - start
        logger.info(
            "http_request",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            latency_ms=round(elapsed * 1000, 2),
        )
        return response

    app.include_router(system_router)
    app.include_router(query_router)
    app.include_router(ingest_router)

    return app
