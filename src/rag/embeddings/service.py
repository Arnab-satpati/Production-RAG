from __future__ import annotations

import asyncio
from functools import lru_cache

import structlog
from sentence_transformers import SentenceTransformer

from rag.config.settings import get_settings

logger = structlog.get_logger(__name__)


class EmbeddingService:
    def __init__(self) -> None:
        self._settings = get_settings().ollama
        self._model_name = self._settings.embedding_model
        self._model: SentenceTransformer | None = None

    def _get_model(self) -> SentenceTransformer:
        if self._model is None:
            logger.info("loading_embedding_model", model=self._model_name)
            self._model = SentenceTransformer(self._model_name)
            logger.info("embedding_model_loaded", model=self._model_name)
        return self._model

    def embed(self, texts: list[str]) -> list[list[float]]:
        model = self._get_model()
        embeddings = model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
        return embeddings.tolist()

    def embed_single(self, text: str) -> list[float]:
        return self.embed([text])[0]

    async def aembed(self, texts: list[str]) -> list[list[float]]:
        return await asyncio.to_thread(self.embed, texts)

    async def aembed_single(self, text: str) -> list[float]:
        return await asyncio.to_thread(self.embed_single, text)

    @property
    def dimensions(self) -> int:
        return self._get_model().get_sentence_embedding_dimension()


@lru_cache
def get_embedding_service() -> EmbeddingService:
    return EmbeddingService()
