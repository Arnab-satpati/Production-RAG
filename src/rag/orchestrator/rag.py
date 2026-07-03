from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

import structlog

from rag.config.settings import get_settings
from rag.generation.llm import LLMService
from rag.retrieval.engine import RetrievalEngine

logger = structlog.get_logger(__name__)


@dataclass
class RAGResponse:
    answer: str
    sources: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class RAGOrchestrator:
    def __init__(
        self,
        retrieval_engine: RetrievalEngine | None = None,
        llm_service: LLMService | None = None,
    ) -> None:
        self._retrieval = retrieval_engine or RetrievalEngine()
        self._llm = llm_service or LLMService()
        self._settings = get_settings()

    async def query(
        self,
        question: str,
        top_k: int | None = None,
        filter_source: str | None = None,
    ) -> RAGResponse:
        start = time.perf_counter()

        logger.info("rag_query_started", question_length=len(question))

        results = await self._retrieval.retrieve(
            query=question,
            top_k=top_k,
            filter_source=filter_source,
        )

        context = self._retrieval.build_context(results)

        llm_result = await self._llm.generate(
            query=question,
            context=context,
        )

        sources = []
        for r in results:
            sources.append({
                "content": r.content[:200] + "..." if len(r.content) > 200 else r.content,
                "score": r.score,
                "source": r.source,
                "chunk_id": r.chunk_id,
            })

        total_ms = (time.perf_counter() - start) * 1000

        response = RAGResponse(
            answer=llm_result["answer"],
            sources=sources,
            metadata={
                "latency_ms": round(total_ms, 2),
                "retrieval_latency_ms": round(total_ms - llm_result["latency_ms"], 2),
                "generation_latency_ms": llm_result["latency_ms"],
                "model": llm_result["model"],
                "tokens_generated": llm_result["tokens_generated"],
                "retrieved_chunks": len(results),
            },
        )

        logger.info(
            "rag_query_completed",
            total_latency_ms=round(total_ms, 2),
            sources_count=len(sources),
        )

        return response
