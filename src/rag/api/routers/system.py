from __future__ import annotations

from fastapi import APIRouter

from rag import __version__
from rag.api.models.schemas import CollectionInfoResponse, HealthResponse
from rag.config.settings import get_settings
from rag.generation.llm import LLMService
from rag.vectorstore.qdrant import QdrantVectorStore

router = APIRouter(tags=["system"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    get_settings()
    services: dict[str, str] = {}

    llm = LLMService()
    try:
        healthy = await llm.health_check()
        services["ollama"] = "healthy" if healthy else "unhealthy"
    except Exception:
        services["ollama"] = "unreachable"

    try:
        vs = QdrantVectorStore()
        vs.ensure_collection()
        services["qdrant"] = "healthy"
    except Exception:
        services["qdrant"] = "unreachable"

    overall = "healthy" if all(
        s == "healthy" for s in services.values()
    ) else "degraded"

    return HealthResponse(
        status=overall,
        version=__version__,
        services=services,
    )


@router.get("/collection", response_model=CollectionInfoResponse)
async def collection_info() -> CollectionInfoResponse:
    vs = QdrantVectorStore()
    vs.ensure_collection()
    info = vs.get_collection_info()
    return CollectionInfoResponse(**info)
