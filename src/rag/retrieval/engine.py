from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

import structlog

from rag.config.settings import get_settings
from rag.embeddings.service import EmbeddingService, get_embedding_service
from rag.vectorstore.qdrant import QdrantVectorStore

logger = structlog.get_logger(__name__)


@dataclass
class RetrievalResult:
    content: str
    score: float
    metadata: dict[str, Any] = field(default_factory=dict)
    source: str = ""
    chunk_id: str = ""


class RetrievalEngine:
    def __init__(
        self,
        vector_store: QdrantVectorStore | None = None,
        embedding_service: EmbeddingService | None = None,
    ) -> None:
        self._settings = get_settings().retrieval
        self._vector_store = vector_store or QdrantVectorStore()
        self._embedding_service = embedding_service or get_embedding_service()

    async def retrieve(
        self,
        query: str,
        top_k: int | None = None,
        filter_source: str | None = None,
        score_threshold: float | None = None,
    ) -> list[RetrievalResult]:
        k = top_k or self._settings.top_k
        threshold = score_threshold or self._settings.similarity_threshold

        start = time.perf_counter()
        query_embedding = await self._embedding_service.aembed_single(query)

        hits = await self._vector_store.search(
            query_embedding=query_embedding,
            top_k=k,
            filter_source=filter_source,
            score_threshold=threshold,
        )

        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "retrieval_completed",
            query_length=len(query),
            results_count=len(hits),
            latency_ms=round(elapsed_ms, 2),
        )

        results = []
        for hit in hits:
            results.append(
                RetrievalResult(
                    content=hit["content"],
                    score=hit["score"],
                    metadata=hit["metadata"],
                    source=hit["metadata"].get("source", ""),
                    chunk_id=hit["metadata"].get("chunk_id", ""),
                ),
            )

        return results

    def build_context(self, results: list[RetrievalResult]) -> str:
        if not results:
            return "No relevant context found."

        context_parts = []
        for _i, result in enumerate(results, 1):
            source = result.source.split("/")[-1] if result.source else "unknown"
            context_parts.append(
                f"[Source: {source} | Relevance: {result.score:.2f}]\n{result.content}",
            )

        return "\n\n---\n\n".join(context_parts)
