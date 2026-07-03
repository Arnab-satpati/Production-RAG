from __future__ import annotations

import asyncio
from functools import lru_cache

import httpx
import structlog

from rag.config.settings import get_settings

logger = structlog.get_logger(__name__)

NOMIC_EMBED_DIMENSIONS = 768


class EmbeddingService:
    def __init__(self) -> None:
        self._settings = get_settings().ollama
        self._model_name = self._settings.embedding_model
        self._client: httpx.Client | None = None

    def _get_client(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(
                base_url=self._settings.base_url,
                timeout=self._settings.timeout,
            )
        return self._client

    def embed(self, texts: list[str]) -> list[list[float]]:
        client = self._get_client()
        embeddings = []

        for text in texts:
            response = client.post(
                "/api/embeddings",
                json={"model": self._model_name, "prompt": text},
            )
            response.raise_for_status()
            data = response.json()
            embeddings.append(data["embedding"])

        return embeddings

    def embed_single(self, text: str) -> list[float]:
        return self.embed([text])[0]

    async def aembed(self, texts: list[str]) -> list[list[float]]:
        return await asyncio.to_thread(self.embed, texts)

    async def aembed_single(self, text: str) -> list[float]:
        return await asyncio.to_thread(self.embed_single, text)

    @property
    def dimensions(self) -> int:
        return NOMIC_EMBED_DIMENSIONS


@lru_cache
def get_embedding_service() -> EmbeddingService:
    return EmbeddingService()
