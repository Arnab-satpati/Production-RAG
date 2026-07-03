from __future__ import annotations

import time

import structlog
from fastapi import APIRouter, HTTPException

from rag.api.models.schemas import QueryRequest, QueryResponse, SourceChunk
from rag.guardrails.engine import GuardrailsEngine
from rag.monitoring.metrics import get_metrics_collector
from rag.orchestrator.rag import RAGOrchestrator

router = APIRouter(prefix="/api/v1", tags=["query"])
logger = structlog.get_logger(__name__)

_orchestrator: RAGOrchestrator | None = None
_guardrails: GuardrailsEngine | None = None


def _get_orchestrator() -> RAGOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = RAGOrchestrator()
    return _orchestrator


def _get_guardrails() -> GuardrailsEngine:
    global _guardrails
    if _guardrails is None:
        _guardrails = GuardrailsEngine()
    return _guardrails


@router.post("/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest) -> QueryResponse:
    guardrails = _get_guardrails()
    validation = await guardrails.validate_input(request.question)
    if not validation.passed:
        raise HTTPException(status_code=400, detail=validation.reason)

    sanitized_question = validation.sanitized_input

    start = time.perf_counter()
    try:
        orchestrator = _get_orchestrator()
        response = await orchestrator.query(
            question=sanitized_question,
            top_k=request.top_k,
            filter_source=request.filter_source,
        )

        elapsed = time.perf_counter() - start
        metrics = get_metrics_collector()
        metrics.record_request("POST", "/api/v1/query", "200", elapsed)

        return QueryResponse(
            answer=response.answer,
            sources=[
                SourceChunk(
                    content=s["content"],
                    score=s["score"],
                    source=s["source"],
                    chunk_id=s["chunk_id"],
                )
                for s in response.sources
            ],
            metadata=response.metadata,
        )

    except ConnectionError as e:
        metrics = get_metrics_collector()
        metrics.record_request("POST", "/api/v1/query", "503", time.perf_counter() - start)
        raise HTTPException(status_code=503, detail=str(e)) from e
    except Exception as e:
        import traceback
        logger.error("query_failed", error=str(e), traceback=traceback.format_exc())
        metrics = get_metrics_collector()
        metrics.record_request("POST", "/api/v1/query", "500", time.perf_counter() - start)
        detail = f"Internal server error: {type(e).__name__}: {e}"
        raise HTTPException(status_code=500, detail=detail) from e
