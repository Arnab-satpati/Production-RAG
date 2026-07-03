from rag.monitoring.metrics import MetricsCollector


def test_metrics_collector():
    collector = MetricsCollector()
    collector.record_request("POST", "/api/v1/query", "200", 0.5)
    collector.record_retrieval(0.1, 5)
    collector.record_generation(1.2)
    collector.record_ingestion("pdf", 10)
    collector.record_guardrail("input", "too_long")
