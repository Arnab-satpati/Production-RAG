from __future__ import annotations

import structlog

logger = structlog.get_logger(__name__)


def setup_tracing(service_name: str = "rag-production") -> None:
    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        provider = TracerProvider()
        processor = BatchSpanProcessor()
        provider.add_span_processor(processor)
        trace.set_tracer_provider(provider)

        logger.info("tracing_configured", service_name=service_name)
    except ImportError:
        logger.warning("opentelemetry_not_installed")
    except Exception as e:
        logger.warning("tracing_setup_failed", error=str(e))
