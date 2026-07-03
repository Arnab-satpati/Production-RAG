from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

import structlog
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

from rag.config.settings import get_settings

if TYPE_CHECKING:
    from rag.ingestion.loaders.base import ChunkedDocument

logger = structlog.get_logger(__name__)

_vector_store_instance: QdrantVectorStore | None = None


def get_vector_store() -> QdrantVectorStore:
    global _vector_store_instance
    if _vector_store_instance is None:
        _vector_store_instance = QdrantVectorStore()
    return _vector_store_instance


class QdrantVectorStore:
    def __init__(self) -> None:
        self._settings = get_settings().qdrant
        self._client: QdrantClient | None = None

    def _get_client(self) -> QdrantClient:
        if self._client is None:
            if self._settings.local_mode:
                self._client = QdrantClient(":memory:")
                logger.info("qdrant_in_memory_mode")
            else:
                self._client = QdrantClient(
                    host=self._settings.host,
                    port=self._settings.port,
                    grpc_port=self._settings.grpc_port,
                )
                logger.info(
                    "qdrant_connected",
                    host=self._settings.host,
                    port=self._settings.port,
                )
        return self._client

    def ensure_collection(self) -> None:
        client = self._get_client()
        collections = client.get_collections().collections
        existing = [c.name for c in collections]

        if self._settings.collection not in existing:
            client.create_collection(
                collection_name=self._settings.collection,
                vectors_config=VectorParams(
                    size=self._settings.embedding_dim,
                    distance=Distance.COSINE,
                ),
            )
            logger.info(
                "collection_created",
                collection=self._settings.collection,
                dim=self._settings.embedding_dim,
            )

    def upsert(
        self,
        chunks: list[ChunkedDocument],
        embeddings: list[list[float]],
    ) -> int:
        client = self._get_client()
        points = []

        for chunk, embedding in zip(chunks, embeddings, strict=False):
            point_id = str(uuid.uuid5(uuid.NAMESPACE_URL, chunk.chunk_id))
            payload = {
                "content": chunk.content,
                "chunk_id": chunk.chunk_id,
                "source": chunk.source,
                "doc_type": chunk.doc_type,
                "chunk_index": chunk.chunk_index,
                "total_chunks": chunk.total_chunks,
                **chunk.metadata,
            }
            points.append(PointStruct(id=point_id, vector=embedding, payload=payload))

        client.upsert(
            collection_name=self._settings.collection,
            points=points,
        )

        logger.info("upserted_chunks", count=len(points))
        return len(points)

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        filter_source: str | None = None,
        score_threshold: float | None = None,
    ) -> list[dict[str, Any]]:
        client = self._get_client()

        query_filter = None
        if filter_source:
            query_filter = Filter(
                must=[FieldCondition(key="source", match=MatchValue(value=filter_source))],
            )

        results = client.query_points(
            collection_name=self._settings.collection,
            query=query_embedding,
            query_filter=query_filter,
            limit=top_k,
            score_threshold=score_threshold,
        )

        hits = []
        for hit in results.points:
            hits.append(
                {
                    "id": str(hit.id),
                    "score": hit.score,
                    "content": hit.payload.get("content", ""),
                    "metadata": {
                        k: v
                        for k, v in hit.payload.items()
                        if k != "content"
                    },
                },
            )

        return hits

    def delete_by_source(self, source: str) -> int:
        client = self._get_client()
        result = client.delete(
            collection_name=self._settings.collection,
            points_selector=Filter(
                must=[FieldCondition(key="source", match=MatchValue(value=source))],
            ),
        )
        logger.info("deleted_by_source", source=source)
        return result

    def get_collection_info(self) -> dict[str, Any]:
        client = self._get_client()
        info = client.get_collection(self._settings.collection)
        return {
            "name": self._settings.collection,
            "vectors_count": info.vectors_count,
            "points_count": info.points_count,
            "status": str(info.status),
        }
