from __future__ import annotations

from functools import lru_cache

from prometheus_client import Counter, Histogram, Summary

REQUEST_COUNT = Counter(
    "rag_requests_total",
    "Total RAG requests",
    ["method", "endpoint", "status"],
)

REQUEST_LATENCY = Histogram(
    "rag_request_latency_seconds",
    "Request latency in seconds",
    ["endpoint"],
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0],
)

RETRIEVAL_LATENCY = Histogram(
    "rag_retrieval_latency_seconds",
    "Retrieval latency in seconds",
    buckets=[0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
)

GENERATION_LATENCY = Histogram(
    "rag_generation_latency_seconds",
    "LLM generation latency in seconds",
    buckets=[0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0],
)

CHUNKS_INGESTED = Counter(
    "rag_chunks_ingested_total",
    "Total chunks ingested",
    ["source_type"],
)

RETRIEVAL_RESULTS = Histogram(
    "rag_retrieval_results_count",
    "Number of retrieval results per query",
    buckets=[1, 2, 3, 5, 10, 20],
)

GUARDRAIL_TRIGGERED = Counter(
    "rag_guardrails_triggered_total",
    "Total guardrail triggers",
    ["type", "reason"],
)

ACTIVE_REQUESTS = Summary(
    "rag_active_requests",
    "Number of active requests",
)


class MetricsCollector:
    def record_request(
        self, method: str, endpoint: str, status: str, latency: float,
    ) -> None:
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status).inc()
        REQUEST_LATENCY.labels(endpoint=endpoint).observe(latency)

    def record_retrieval(self, latency: float, result_count: int) -> None:
        RETRIEVAL_LATENCY.observe(latency)
        RETRIEVAL_RESULTS.observe(result_count)

    def record_generation(self, latency: float) -> None:
        GENERATION_LATENCY.observe(latency)

    def record_ingestion(self, source_type: str, count: int) -> None:
        CHUNKS_INGESTED.labels(source_type=source_type).inc(count)

    def record_guardrail(self, trigger_type: str, reason: str) -> None:
        GUARDRAIL_TRIGGERED.labels(type=trigger_type, reason=reason).inc()


@lru_cache
def get_metrics_collector() -> MetricsCollector:
    return MetricsCollector()
