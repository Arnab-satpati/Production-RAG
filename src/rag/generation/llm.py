from __future__ import annotations

import time

import httpx
import structlog

from rag.config.settings import get_settings

logger = structlog.get_logger(__name__)

SYSTEM_PROMPT = (
    "You are a helpful AI assistant that answers questions based on the provided context. "
    "Always base your answers on the context provided. If the context doesn't contain enough "
    "information, say so clearly. Be concise, accurate, and cite specific parts of the "
    "context when possible. Format your responses with clear structure using markdown."
)


class LLMService:
    def __init__(self) -> None:
        self._settings = get_settings().ollama
        self._client: httpx.AsyncClient | None = None

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self._settings.base_url,
                timeout=httpx.Timeout(self._settings.timeout),
            )
        return self._client

    async def generate(
        self,
        query: str,
        context: str,
        system_prompt: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> dict:
        prompt = f"""Context:
{context}

Question: {query}

Answer:"""

        payload = {
            "model": self._settings.model,
            "messages": [
                {"role": "system", "content": system_prompt or SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "stream": False,
            "options": {
                "temperature": temperature or self._settings.temperature,
                "num_predict": max_tokens or self._settings.max_tokens,
            },
        }

        start = time.perf_counter()
        client = self._get_client()

        try:
            response = await client.post("/api/chat", json=payload)
            response.raise_for_status()
            data = response.json()

            elapsed_ms = (time.perf_counter() - start) * 1000

            answer = data.get("message", {}).get("content", "")
            total_duration = data.get("total_duration", 0)
            eval_count = data.get("eval_count", 0)

            logger.info(
                "llm_generation_completed",
                model=self._settings.model,
                latency_ms=round(elapsed_ms, 2),
                ollama_duration_ns=total_duration,
                tokens_generated=eval_count,
            )

            return {
                "answer": answer,
                "model": self._settings.model,
                "latency_ms": round(elapsed_ms, 2),
                "tokens_generated": eval_count,
                "total_duration_ns": total_duration,
            }

        except httpx.HTTPStatusError as e:
            logger.error("llm_generation_failed", status=e.response.status_code, error=str(e))
            raise
        except httpx.ConnectError as e:
            logger.error("llm_connection_failed", base_url=self._settings.base_url)
            raise ConnectionError(
                f"Cannot connect to Ollama at {self._settings.base_url}. "
                "Ensure Ollama is running: ollama serve",
            ) from e

    async def health_check(self) -> bool:
        try:
            client = self._get_client()
            response = await client.get("/api/tags")
            return response.status_code == 200
        except Exception:
            return False
